# CPT Analysis for Settlement Calculations

The Cone Penetration Test (CPT) is a fundamental geotechnical investigation method used in settlement analysis within Settle3. CPT provides continuous profiling of soil properties including tip resistance (qc), sleeve friction (fs), and pore water pressure (u).

## Key Parameters from CPT

**Tip Resistance (qc)**: Primary parameter indicating soil strength and bearing capacity. Higher values indicate denser/stronger soils.

**Friction Ratio (Rf)**: Calculated as fs/qc × 100%, used for soil classification. Sandy soils typically show Rf < 1%, while clayey soils show Rf > 3%.

**Soil Behavior Type Index (Ic)**: Derived parameter combining qc, fs, and effective stress to classify soil behavior for settlement calculations.

## Settlement Calculations

CPT data is used to estimate elastic modulus (E) through empirical correlations:
- For sands: E = α × qc (where α = 2-4 for normally consolidated sands)
- For clays: E = β × (qc - σvo) (where β = 3-8 depending on plasticity)

The settlement calculation integrates stress-strain relationships derived from CPT parameters through the soil profile. Settle3 uses these correlations to predict immediate and consolidation settlements.