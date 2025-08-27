# CPT Correlations for Engineering Parameters

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

These correlations form the foundation for interpreting CPT data in geotechnical design and are implemented in Settle3's analysis routines.