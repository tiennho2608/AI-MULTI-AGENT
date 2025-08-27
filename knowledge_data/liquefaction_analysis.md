# Liquefaction Analysis Using Settle3

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

Settle3 provides automated workflows for processing CPT data through these procedures, generating liquefaction potential profiles and safety factor distributions.