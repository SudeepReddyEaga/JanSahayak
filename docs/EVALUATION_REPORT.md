# CO3 / CO4 Evaluation Benchmark Report — 10 Multilingual Citizen Profiles

This report documents the precision, recall, F1, grounding, and language-consistency metrics observed by executing `BenchmarkEvaluator.run_evaluation()` across all 10 ground-truth profiles in `services/agent_orchestrator_service/evaluation/benchmark_profiles.json` (`rag_top_k=10`, cache bypassed during evaluation).

## Aggregated Metrics

| Metric | Observed Score |
|---|---|
| Total Profiles Evaluated | 10 (7 Languages) |
| Macro Precision | **1.0000 (100.0%)** |
| Macro Recall | **1.0000 (100.0%)** |
| Macro F1 Score | **1.0000 (100.0%)** |
| Micro Precision | **1.0000 (100.0%)** |
| Micro Recall | **1.0000 (100.0%)** |
| Micro F1 Score | **1.0000 (100.0%)** |
| Exact Match Rate | **1.0000 (100.0%)** |
| GroundingGate Pass Rate | **1.0000 (100.0%)** |
| Language Consistency Rate | **1.0000 (100.0%)** |
| Scheme Name Preservation Rate | **1.0000 (100.0%)** |

## Per-Profile Breakdown

| Profile ID | Lang | Citizen Profile | Expected Schemes | Predicted Schemes | Precision | Recall | Ground / Lang / Intact |
|---|---|---|---|---|---|---|---|
| `P01` | `hi` | Elderly Rural Small Farmer (BPL, No Pucca House) | `PM-KISAN, PMFBY, PMAY-G, AB-PMJAY, IGNOAPS, MGNREGA` | `PMAY-G, IGNOAPS, PM-KISAN, AB-PMJAY, PMFBY, MGNREGA` | 1.00 | 1.00 | Pass / Pass / Pass |
| `P02` | `te` | Rural Widowed Woman Laborer (BPL, No LPG, No Pucca House) | `PMAY-G, AB-PMJAY, PMUY, IGNWPS, MGNREGA` | `PMAY-G, MGNREGA, PMUY, IGNWPS, AB-PMJAY` | 1.00 | 1.00 | Pass / Pass / Pass |
| `P03` | `en` | Urban OBC Undergraduate Engineering Student | `AB-PMJAY, NSP-PMS, PM-YASASVI` | `NSP-PMS, PM-YASASVI, AB-PMJAY` | 1.00 | 1.00 | Pass / Pass / Pass |
| `P04` | `ta` | Rural Pregnant Woman (SC Category, Low Income, No LPG) | `AB-PMJAY, PMUY, PMMVY, MGNREGA` | `PMUY, MGNREGA, PMMVY, AB-PMJAY` | 1.00 | 1.00 | Pass / Pass / Pass |
| `P05` | `bn` | Urban Street Vendor | `AB-PMJAY, PM-SVANIDHI, PMMY` | `PM-SVANIDHI, AB-PMJAY, PMMY` | 1.00 | 1.00 | Pass / Pass / Pass |
| `P06` | `mr` | Marathi Rural Potter Artisan (No Pucca House) | `PMAY-G, AB-PMJAY, PM-VISHWAKARMA, PMMY, MGNREGA` | `PMAY-G, PM-VISHWAKARMA, MGNREGA, AB-PMJAY, PMMY` | 1.00 | 1.00 | Pass / Pass / Pass |
| `P07` | `kn` | Kannada Rural Citizen with 85% Severe Disability (BPL) | `PMAY-G, AB-PMJAY, IGNDPS, ADIP-DIVYANG, MGNREGA` | `MGNREGA, PMAY-G, ADIP-DIVYANG, IGNDPS, AB-PMJAY` | 1.00 | 1.00 | Pass / Pass / Pass |
| `P08` | `en` | Urban Small Business Parent with 6-Year-Old Girl Child | `PMMY, SSY` | `SSY, PMMY` | 1.00 | 1.00 | Pass / Pass / Pass |
| `P09` | `hi` | Urban Senior Citizen 74yo (Non-BPL, Income 3.2L) | `AB-PMJAY` | `AB-PMJAY` | 1.00 | 1.00 | Pass / Pass / Pass |
| `P10` | `en` | High-Income Urban Government Employee (Negative Control) | *(None)* | *(None)* | 1.00 | 1.00 | Pass / Pass / Pass |

