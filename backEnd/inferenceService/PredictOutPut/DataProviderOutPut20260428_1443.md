# Batch Inference Results — DataProvider

_Generated: 2026-04-28 14:44_

**Dataset:** LIDC-IDRI  |  **Target:** 10 malignant + 10 benign  |  **Cases run:** 20  |  **Skipped:** 0

## Summary

| Metric | Value |
|--------|-------|
| Total cases run | 20 |
| Correct predictions | 14 |
| Wrong predictions | 6 |
| **Overall Accuracy** | **70.0%** |
| True Positives (TP) | 8 |
| True Negatives (TN) | 6 |
| False Positives (FP) | 4 |
| False Negatives (FN) | 2 |
| **Sensitivity (Recall)** | **80.0%** |
| **Specificity** | **60.0%** |
| **Precision** | **66.7%** |
| **F1 Score** | **0.727** |

## Confusion Matrix

|  | Predicted Malignant | Predicted Benign |
|--|:-------------------:|:----------------:|
| **Actual Malignant** | 8 (TP) | 2 (FN) |
| **Actual Benign**    | 4 (FP) | 6 (TN) |

## Malignant Cases (10 / 10)

| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |
|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|
| 1 | LIDC-IDRI-0080 | Malignancy | Malignancy | ✓ | 58.9% | 0.589 | 0.411 |
| 2 | LIDC-IDRI-0030 | Malignancy | Malignancy | ✓ | 91.8% | 0.918 | 0.082 |
| 3 | LIDC-IDRI-0086 | Malignancy | Malignancy | ✓ | 70.7% | 0.707 | 0.293 |
| 4 | LIDC-IDRI-0040 | Malignancy | Malignancy | ✓ | 68.4% | 0.684 | 0.316 |
| 5 | LIDC-IDRI-0058 | Malignancy | Malignancy | ✓ | 52.7% | 0.527 | 0.473 |
| 6 | LIDC-IDRI-0016 | Malignancy | Malignancy | ✓ | 76.5% | 0.765 | 0.235 |
| 7 | LIDC-IDRI-0054 | Malignancy | Malignancy | ✓ | 69.7% | 0.697 | 0.303 |
| 8 | LIDC-IDRI-0097 | Malignancy | Malignancy | ✓ | 51.4% | 0.514 | 0.486 |
| 9 | LIDC-IDRI-0019 | Malignancy | Benign | ✗ | 50.0% | 0.500 | 0.500 |
| 10 | LIDC-IDRI-0009 | Malignancy | Benign | ✗ | 62.4% | 0.376 | 0.624 |

## Benign Cases (10 / 10)

| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |
|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|
| 1 | LIDC-IDRI-0425 | Benign | Malignancy | ✗ | 56.2% | 0.562 | 0.438 |
| 2 | LIDC-IDRI-0573 | Benign | Benign | ✓ | 72.4% | 0.276 | 0.724 |
| 3 | LIDC-IDRI-0610 | Benign | Benign | ✓ | 65.1% | 0.349 | 0.651 |
| 4 | LIDC-IDRI-0512 | Benign | Malignancy | ✗ | 50.4% | 0.504 | 0.496 |
| 5 | LIDC-IDRI-0336 | Benign | Benign | ✓ | 63.4% | 0.366 | 0.634 |
| 6 | LIDC-IDRI-0226 | Benign | Malignancy | ✗ | 62.7% | 0.627 | 0.373 |
| 7 | LIDC-IDRI-0100 | Benign | Malignancy | ✗ | 59.6% | 0.596 | 0.404 |
| 8 | LIDC-IDRI-0666 | Benign | Benign | ✓ | 64.1% | 0.359 | 0.641 |
| 9 | LIDC-IDRI-0333 | Benign | Benign | ✓ | 65.8% | 0.342 | 0.658 |
| 10 | LIDC-IDRI-0632 | Benign | Benign | ✓ | 64.1% | 0.359 | 0.641 |

