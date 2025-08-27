from typing import List, Dict, Any, Tuple
from .knowledge_base import KnowledgeBase
from .agent import TechnicalAgent

class EvaluationSuite:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.agent = TechnicalAgent()
        
        self.qa_pairs = [
            {
                "question": "What is CPT analysis used for in settlement calculations?",
                "expected_sources": ["cpt_analysis_basics.md", "cpt_correlations.md"],
                "expected_keywords": ["cone penetration test", "tip resistance", "settlement", "modulus"]
            },
            {
                "question": "How is liquefaction potential assessed using CPT data?",
                "expected_sources": ["liquefaction_analysis.md"],
                "expected_keywords": ["liquefaction", "cyclic resistance", "factor of safety", "cpt"]
            },
            {
                "question": "Calculate settlement for load = 150 and Young's modulus = 30000",
                "expected_sources": [],
                "expected_keywords": ["settlement", "0.005", "calculation"],
                "tool_expected": "settlement_calculator"
            },
            {
                "question": "What are the main features of Settle3 software?",
                "expected_sources": ["settle3_help_overview.md"],
                "expected_keywords": ["settle3", "settlement analysis", "3d", "multi-layer"]
            },
            {
                "question": "Calculate bearing capacity for B = 2, gamma = 18, Df = 1.5, friction angle = 35",
                "expected_sources": [],
                "expected_keywords": ["bearing capacity", "ultimate", "terzaghi"],
                "tool_expected": "bearing_capacity_calculator"
            },
            {
                "question": "How do you correlate CPT data to soil strength parameters?",
                "expected_sources": ["cpt_correlations.md"],
                "expected_keywords": ["correlations", "undrained shear strength", "friction angle"]
            },
            {
                "question": "What is the difference between immediate and consolidation settlement?",
                "expected_sources": ["settlement_calculation_methods.md"],
                "expected_keywords": ["immediate settlement", "consolidation", "primary", "secondary"]
            },
            {
                "question": "What are bearing capacity factors Nq and Nr?",
                "expected_sources": ["bearing_capacity_fundamentals.md"],
                "expected_keywords": ["bearing capacity factors", "terzaghi", "friction angle", "nq", "nr"]
            }
        ]
    
    def evaluate_retrieval(self, k: int = 3) -> Dict[str, Any]:
        """Evaluate retrieval performance"""
        hit_at_k = 0
        total_questions = 0
        confidence_scores = []
        
        results_detail = []
        
        for qa in self.qa_pairs:
            if qa["expected_sources"]:  # Only evaluate retrieval questions
                total_questions += 1
                search_results = self.kb.search(qa["question"], k=k)
                
                retrieved_sources = [result["filename"] for result in search_results]
                expected_sources = qa["expected_sources"]
                
                # Check if any expected source is in top-k
                hit = any(source in retrieved_sources for source in expected_sources)
                if hit:
                    hit_at_k += 1
                
                # Record confidence score of top result
                if search_results:
                    confidence_scores.append(search_results[0]["score"])
                
                results_detail.append({
                    "question": qa["question"],
                    "expected": expected_sources,
                    "retrieved": retrieved_sources,
                    "hit": hit,
                    "top_score": search_results[0]["score"] if search_results else 0
                })
        
        return {
            "hit_at_k": hit_at_k / total_questions if total_questions > 0 else 0,
            "avg_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            "total_evaluated": total_questions,
            "details": results_detail
        }
    
    def evaluate_answers(self) -> Dict[str, Any]:
        """Evaluate answer quality using keyword matching"""
        keyword_matches = 0
        total_questions = len(self.qa_pairs)
        tool_accuracy = 0
        tool_questions = 0
        
        results_detail = []
        
        for qa in self.qa_pairs:
            result = self.agent.process_question(qa["question"])
            answer = result["answer"].lower()
            expected_keywords = [kw.lower() for kw in qa["expected_keywords"]]
            
            # Check keyword overlap
            matches = sum(1 for keyword in expected_keywords if keyword in answer)
            keyword_score = matches / len(expected_keywords) if expected_keywords else 0
            
            if keyword_score > 0.5:  # At least half keywords match
                keyword_matches += 1
            
            # Check tool usage
            if "tool_expected" in qa:
                tool_questions += 1
                if qa["tool_expected"] in result.get("tools_used", []):
                    tool_accuracy += 1
            
            results_detail.append({
                "question": qa["question"],
                "expected_keywords": qa["expected_keywords"],
                "keyword_score": keyword_score,
                "tools_used": result.get("tools_used", []),
                "answer_length": len(result["answer"])
            })
        
        return {
            "keyword_match_rate": keyword_matches / total_questions,
            "tool_accuracy": tool_accuracy / tool_questions if tool_questions > 0 else 0,
            "total_evaluated": total_questions,
            "details": results_detail
        }
    
    def run_full_evaluation(self) -> Dict[str, Any]:
        """Run complete evaluation suite"""
        print("Running evaluation suite...")
        
        retrieval_results = self.evaluate_retrieval(k=3)
        answer_results = self.evaluate_answers()
        
        print(f"\nRetrieval Results:")
        print(f"Hit@3: {retrieval_results['hit_at_k']:.3f}")
        print(f"Avg Confidence: {retrieval_results['avg_confidence']:.3f}")
        
        print(f"\nAnswer Quality Results:")
        print(f"Keyword Match Rate: {answer_results['keyword_match_rate']:.3f}")
        print(f"Tool Usage Accuracy: {answer_results['tool_accuracy']:.3f}")
        
        return {
            "retrieval": retrieval_results,
            "answers": answer_results,
            "summary": {
                "hit_at_3": retrieval_results['hit_at_k'],
                "keyword_match_rate": answer_results['keyword_match_rate'],
                "tool_accuracy": answer_results['tool_accuracy']
            }
        }