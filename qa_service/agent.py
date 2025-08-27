import re
import json
import time
from typing import Dict, Any, List, Optional, Tuple
import logging
import ollama
from .knowledge_base import KnowledgeBase
from .tools import SettlementCalculator, TerzaghiBearingCapacity

logger = logging.getLogger(__name__)

class TechnicalAgent:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.settlement_calc = SettlementCalculator()
        self.bearing_capacity = TerzaghiBearingCapacity()
        self.ollama_model = "llama3"  # Specify the Ollama model to use

    def _should_use_settlement_tool(self, question: str) -> bool:
        """Determine if settlement calculation tool should be used"""
        settlement_keywords = [
            "settlement", "immediate settlement", "elastic settlement",
            "load", "young", "modulus", "settlement = load",
            "calculate settlement", "settlement calculation"
        ]
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in settlement_keywords)

    def _should_use_bearing_capacity_tool(self, question: str) -> bool:
        """Determine if bearing capacity tool should be used"""
        bearing_keywords = [
            "bearing capacity", "ultimate bearing", "terzaghi", "qu", "q_ult",
            "bearing", "footing", "foundation capacity", "nq", "nr", "friction angle"
        ]
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in bearing_keywords)

    def _extract_settlement_params(self, question: str, context: str = "") -> Optional[Tuple[float, float]]:
        """Extract load and Young's modulus from question"""
        text = f"{question} {context}".lower()
        
        # Look for patterns like "load = 100", "youngs modulus = 25000", etc.
        load_match = re.search(r'load[s]?\s*[=:]\s*([0-9.]+)', text)
        modulus_patterns = [
            r'young[\'s\s]*modulus[s]?\s*[=:]\s*([0-9.]+)',
            r'modulus[s]?\s*[=:]\s*([0-9.]+)',
            r'e\s*[=:]\s*([0-9.]+)'
        ]
        
        load = None
        modulus = None
        
        if load_match:
            load = float(load_match.group(1))
        
        for pattern in modulus_patterns:
            modulus_match = re.search(pattern, text)
            if modulus_match:
                modulus = float(modulus_match.group(1))
                break
        
        if load is not None and modulus is not None:
            return (load, modulus)
        return None

    def _extract_bearing_capacity_params(self, question: str, context: str = "") -> Optional[Dict[str, float]]:
        """Extract bearing capacity parameters from question"""
        text = f"{question} {context}".lower()
        
        params = {}
        
        # Extract parameters using regex patterns
        patterns = {
            'B': r'b\s*[=:]\s*([0-9.]+)',
            'gamma': r'gamma\s*[=:]\s*([0-9.]+)',
            'Df': r'df\s*[=:]\s*([0-9.]+)',
            'friction_angle': r'friction[_\s]*angle\s*[=:]\s*([0-9.]+)'
        }
        
        for param, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                params[param] = float(match.group(1))
        
        # Check if we have all required parameters
        if len(params) == 4:
            return params
        return None

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama to generate a response"""
        try:
            response = ollama.generate(model=self.ollama_model, prompt=prompt)
            return response['response'].strip()
        except Exception as e:
            logger.error(f"Ollama call failed: {str(e)}")
            return f"Error calling Ollama: {str(e)}"

    def process_question(self, question: str, context: str = "") -> Dict[str, Any]:
        """Main agent logic to process questions"""
        trace_steps = []
        start_time = time.time()
        
        try:
            # Step 1: Decide what to do
            use_settlement = self._should_use_settlement_tool(question)
            use_bearing = self._should_use_bearing_capacity_tool(question)
            use_retrieval = True  # Always try retrieval for context
            
            citations = []
            answer_parts = []
            tools_used = []
            
            # Step 2: Retrieval
            if use_retrieval:
                retrieval_start = time.time()
                search_results = self.kb.search(question, k=3)
                retrieval_time = (time.time() - retrieval_start) * 1000
                
                trace_steps.append({
                    "step": "retrieval",
                    "duration_ms": round(retrieval_time, 2),
                    "results_count": len(search_results),
                    "top_score": search_results[0]['score'] if search_results else 0
                })
                
                if search_results:
                    citations = [
                        {
                            "source": result['filename'],
                            "title": result['title'],
                            "score": result['score']
                        }
                        for result in search_results[:2]  # Top 2 results
                    ]
            
            # Step 3: Tool usage
            if use_settlement:
                tool_start = time.time()
                params = self._extract_settlement_params(question, context)
                if params:
                    load, modulus = params
                    try:
                        result = self.settlement_calc.calculate(load, modulus)
                        tools_used.append("settlement_calculator")
                        answer_parts.append(
                            f"Settlement calculation: {result['settlement']:.4f} {result['units']}. "
                            f"Formula used: {result['formula']}"
                        )
                        
                        tool_time = (time.time() - tool_start) * 1000
                        trace_steps.append({
                            "step": "settlement_tool",
                            "duration_ms": round(tool_time, 2),
                            "inputs": result['inputs'],
                            "result": result['settlement']
                        })
                    except Exception as e:
                        answer_parts.append(f"Error in settlement calculation: {str(e)}")
                else:
                    answer_parts.append(
                        "To calculate settlement, please provide both load and Young's modulus values. "
                        "Format: 'Calculate settlement for load = X and Young's modulus = Y'"
                    )
            
            if use_bearing:
                tool_start = time.time()
                params = self._extract_bearing_capacity_params(question, context)
                if params:
                    try:
                        result = self.bearing_capacity.calculate(**params)
                        tools_used.append("bearing_capacity_calculator")
                        answer_parts.append(
                            f"Ultimate bearing capacity: {result['ultimate_bearing_capacity']:.2f} {result['units']}. "
                            f"Factors used: Nq = {result['factors']['Nq']}, Nr = {result['factors']['Nr']}"
                        )
                        
                        tool_time = (time.time() - tool_start) * 1000
                        trace_steps.append({
                            "step": "bearing_capacity_tool",
                            "duration_ms": round(tool_time, 2),
                            "inputs": result['inputs'],
                            "result": result['ultimate_bearing_capacity']
                        })
                    except Exception as e:
                        answer_parts.append(f"Error in bearing capacity calculation: {str(e)}")
                else:
                    answer_parts.append(
                        "To calculate bearing capacity, please provide: B (footing width), "
                        "gamma (unit weight), Df (footing depth), and friction angle. "
                        "Format: 'Calculate bearing capacity for B = X, gamma = Y, Df = Z, friction angle = A'"
                    )
            
            # Step 4: Use Ollama for general questions or to enhance answers
            if not answer_parts or (search_results and not tools_used):
                tool_start = time.time()
                ollama_prompt = (
                    f"Question: {question}\n"
                    f"Context from knowledge base:\n"
                    + "\n".join([f"{result['title']}: {result['content'][:300]}" for result in search_results])
                    + "\n\nProvide a concise and accurate answer based on the context and question."
                )
                ollama_response = self._call_ollama(ollama_prompt)
                answer_parts.append(ollama_response)
                trace_steps.append({
                    "step": "ollama_generation",
                    "duration_ms": round((time.time() - tool_start) * 1000, 2)
                })
            
            # Step 5: Generate final answer
            if answer_parts:
                final_answer = " ".join(answer_parts)
            else:
                final_answer = "I couldn't find specific information to answer your question. " + \
                             "Please provide more details or check if your question relates to " + \
                             "settlement calculations, bearing capacity analysis, or CPT/liquefaction analysis."
            
            total_time = (time.time() - start_time) * 1000
            trace_steps.append({
                "step": "final_answer_generation",
                "duration_ms": round(total_time - sum(step.get('duration_ms', 0) for step in trace_steps), 2)
            })
            
            return {
                "answer": final_answer,
                "citations": citations,
                "tools_used": tools_used,
                "retrieval_used": use_retrieval,
                "trace": trace_steps,
                "total_duration_ms": round(total_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Agent processing error: {str(e)}")
            return {
                "answer": f"An error occurred while processing your question: {str(e)}",
                "citations": [],
                "tools_used": [],
                "retrieval_used": False,
                "trace": trace_steps,
                "total_duration_ms": round((time.time() - start_time) * 1000, 2)
            }