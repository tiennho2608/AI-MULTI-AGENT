import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Any
import os
from pathlib import Path

class KnowledgeBase:
    def __init__(self, data_dir: str = "knowledge_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = []
        self.embeddings = None
        self.index = None
        
        self._create_knowledge_documents()
        self._build_index()
    
    def _create_knowledge_documents(self):
        """Create the knowledge base documents"""
        documents = [
            {
                "id": "cpt_analysis_basics",
                "title": "CPT Analysis for Settlement in Settle3",
                "filename": "cpt_analysis_basics.md",
                "content": """# CPT Analysis for Settlement Calculations

The Cone Penetration Test (CPT) is a fundamental geotechnical investigation method used in settlement analysis within Settle3. CPT provides continuous profiling of soil properties including tip resistance (qc), sleeve friction (fs), and pore water pressure (u).

## Key Parameters from CPT

**Tip Resistance (qc)**: Primary parameter indicating soil strength and bearing capacity. Higher values indicate denser/stronger soils.

**Friction Ratio (Rf)**: Calculated as fs/qc × 100%, used for soil classification. Sandy soils typically show Rf < 1%, while clayey soils show Rf > 3%.

**Soil Behavior Type Index (Ic)**: Derived parameter combining qc, fs, and effective stress to classify soil behavior for settlement calculations.

## Settlement Calculations

CPT data is used to estimate elastic modulus (E) through empirical correlations:
- For sands: E = α × qc (where α = 2-4 for normally consolidated sands)
- For clays: E = β × (qc - σvo) (where β = 3-8 depending on plasticity)

The settlement calculation integrates stress-strain relationships derived from CPT parameters through the soil profile. Settle3 uses these correlations to predict immediate and consolidation settlements."""
            },
            {
                "id": "liquefaction_analysis",
                "title": "Liquefaction Analysis in Settle3",
                "filename": "liquefaction_analysis.md",
                "content": """# Liquefaction Analysis Using Settle3

Liquefaction analysis evaluates the potential for soil liquefaction during seismic events. Settle3 implements advanced procedures based on CPT data for liquefaction assessment.

## CPT-Based Liquefaction Assessment

**Cyclic Resistance Ratio (CRR)**: Represents soil's resistance to liquefaction, calculated from normalized CPT tip resistance (qc1N).

**Cyclic Stress Ratio (CSR)**: Represents seismic demand on soil, calculated from peak ground acceleration and soil conditions.

## Key Steps in Analysis

1. **Data Processing**: Clean and normalize CPT data for depth, overburden stress, and equipment variations.

2. **Soil Classification**: Use Robertson (2009) charts to identify liquefiable soil layers based on Ic and qc1N values.

3. **CRR Calculation**: Apply Boulanger & Idriss (2014) correlations for clean sands, with corrections for fines content.

4. **Factor of Safety**: Calculate FS = CRR/CSR for each depth increment.

## Critical Parameters

- **Fines Content (FC)**: Affects liquefaction resistance, estimated from CPT using Ic parameter
- **Magnitude Scaling Factor (MSF)**: Adjusts CSR for earthquake magnitude effects
- **Overburden Correction (Kσ)**: Accounts for confining stress effects on liquefaction resistance

Settle3 provides automated workflows for processing CPT data through these procedures, generating liquefaction potential profiles and safety factor distributions."""
            },
            {
                "id": "settle3_help_overview",
                "title": "Settle3 Software Overview",
                "filename": "settle3_help_overview.md",
                "content": """# Settle3 Software Help Guide

Settle3 is a comprehensive 3D settlement analysis software developed by Rocscience for geotechnical engineering applications.

## Main Features

**Multi-Layer Analysis**: Handles complex soil profiles with varying properties, allowing detailed modeling of heterogeneous ground conditions.

**Load Types**: Supports various loading conditions including point loads, distributed loads, embankments, and foundation systems.

**Settlement Methods**: Implements multiple calculation approaches including elastic theory, consolidation theory, and empirical methods.

## Workflow Overview

1. **Model Setup**: Define geometry, soil layers, and material properties
2. **Load Definition**: Apply surface loads, foundation loads, or construction sequences
3. **Analysis Parameters**: Set calculation methods and convergence criteria
4. **Results Interpretation**: Review settlement contours, time-settlement curves, and factor of safety

## Key Analysis Options

**Immediate Settlement**: Calculated using elastic theory with appropriate modulus values from laboratory tests or field correlations.

**Consolidation Settlement**: Time-dependent analysis using Terzaghi's theory or more advanced approaches for layered systems.

**Secondary Compression**: Long-term settlement prediction using secondary compression indices.

## Integration Capabilities

Settle3 integrates with other Rocscience products and accepts data from various field investigation methods including CPT, SPT, and laboratory testing programs. The software supports both 2D and 3D visualization of results."""
            },
            {
                "id": "cpt_correlations",
                "title": "CPT Correlations for Geotechnical Parameters",
                "filename": "cpt_correlations.md",
                "content": """# CPT Correlations for Engineering Parameters

CPT provides direct measurements that can be correlated to various geotechnical engineering parameters essential for design.

## Strength Parameters

**Undrained Shear Strength (Su)**: For clays, Su = (qc - σvo)/Nkt, where Nkt is the cone factor (typically 10-20).

**Friction Angle (φ')**: For sands, φ' can be estimated using Kulhawy & Mayne (1990): φ' = 17.6° + 11.0°×log(qc1N/pa)

## Stiffness Parameters

**Young's Modulus (E)**: 
- Sands: E = α × qc (α = 2-4)
- Clays: E = β × (qc - σvo) (β = 3-8)

**Shear Modulus (G)**: G = E/[2(1+ν)] where ν is Poisson's ratio

## Consolidation Parameters

**Coefficient of Consolidation (cv)**: Can be estimated from CPT dissipation tests using theoretical solutions.

**Preconsolidation Pressure (σ'p)**: For clays, estimated using correlations with qt and effective stress.

## Soil Classification

**Soil Behavior Type (SBT)**: Robertson (2009) classification using Ic parameter:
- Ic < 1.31: Gravelly sand
- 1.31 < Ic < 2.05: Sand
- 2.05 < Ic < 2.60: Sand mixtures
- 2.60 < Ic < 2.95: Clay mixtures
- Ic > 2.95: Clay

These correlations form the foundation for interpreting CPT data in geotechnical design and are implemented in Settle3's analysis routines."""
            },
            {
                "id": "bearing_capacity_fundamentals",
                "title": "Bearing Capacity Analysis Fundamentals",
                "filename": "bearing_capacity_fundamentals.md",
                "content": """# Bearing Capacity Analysis Fundamentals

Bearing capacity analysis determines the maximum load a foundation can support without experiencing excessive settlement or shear failure.

## Terzaghi Bearing Capacity Theory

The ultimate bearing capacity equation for shallow foundations on cohesionless soils:

**qu = γ×Df×Nq + 0.5×γ×B×Nγ**

Where:
- qu = Ultimate bearing capacity
- γ = Unit weight of soil
- Df = Depth of foundation
- B = Width/diameter of foundation
- Nq, Nγ = Bearing capacity factors (function of friction angle φ)

## Bearing Capacity Factors

The bearing capacity factors are theoretical values that depend on the soil's friction angle:

**For φ = 0°**: Nq = 1.0, Nγ = 0.0
**For φ = 30°**: Nq ≈ 18.4, Nγ ≈ 15.1
**For φ = 35°**: Nq ≈ 33.3, Nγ ≈ 31.2
**For φ = 40°**: Nq ≈ 64.2, Nγ ≈ 66.8

## Design Considerations

**Factor of Safety**: Typically 2.5-3.0 for ultimate bearing capacity
**Allowable Bearing Pressure**: qa = qu/FS
**Settlement Considerations**: Often governs design over bearing capacity failure

## Application in Practice

Modern foundation design considers both bearing capacity and settlement criteria. CPT data provides direct correlation to bearing capacity through qc values, while settlement analysis requires additional parameters like modulus relationships."""
            },
            {
                "id": "settlement_calculation_methods",
                "title": "Settlement Calculation Methods",
                "filename": "settlement_calculation_methods.md",
                "content": """# Settlement Calculation Methods

Settlement analysis is critical for foundation design and typically governs over bearing capacity for most practical applications.

## Types of Settlement

**Immediate Settlement (Si)**: Occurs during load application, calculated using elastic theory. For simple cases: Si = q×B×(1-ν²)×If/E

**Primary Consolidation (Sc)**: Time-dependent settlement in saturated clays due to pore water expulsion. Calculated using: Sc = Cc×H×log(σ'f/σ'i)/(1+e0)

**Secondary Compression (Ss)**: Long-term settlement after primary consolidation. Calculated using: Ss = Cα×H×log(t2/t1)/(1+e0)

## Settlement Calculation Parameters

**Compression Index (Cc)**: Slope of virgin compression curve in e-log p' plot
**Recompression Index (Cr)**: Slope of unloading-reloading curve
**Secondary Compression Index (Cα)**: Rate of secondary compression

## Elastic Settlement Methods

**Influence Factor Method**: Uses influence factors (If) based on foundation geometry and soil layering
**Stress Distribution Method**: Calculates stress at depth and integrates settlement over profile
**Finite Element Method**: Advanced numerical approach for complex geometries

## CPT-Based Settlement Analysis

CPT provides continuous soil profiling for settlement calculations:
- Direct correlation to elastic modulus
- Soil classification for parameter selection
- Stress history assessment through qt measurements

Modern software like Settle3 integrates these methods with CPT data for comprehensive settlement analysis."""
            }
        ]
        
        self.documents = documents
        
        # Save documents to files
        for doc in documents:
            file_path = self.data_dir / doc["filename"]
            with open(file_path, 'w') as f:
                f.write(doc["content"])
    
    def _build_index(self):
        """Build FAISS index for similarity search"""
        texts = [doc["content"] for doc in self.documents]
        self.embeddings = self.model.encode(texts)
        
        # Create FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings)
    
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        scores, indices = self.index.search(query_embedding, k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['score'] = float(score)
                doc['rank'] = i + 1
                results.append(doc)
        
        return results