# Settlement Calculation Methods

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

Modern software like Settle3 integrates these methods with CPT data for comprehensive settlement analysis.