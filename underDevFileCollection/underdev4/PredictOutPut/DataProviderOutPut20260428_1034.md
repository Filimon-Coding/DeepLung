# Batch Inference Results — underdev4 (MedicalNet ResNet-18)

_Generated: 2026-04-28 10:37_

**Dataset:** LIDC-IDRI  |  **Cases run:** 60  |  **Skipped:** 0

## Summary

| Metric | Value |
|--------|-------|
| Total cases run | 60 |
| Correct predictions | 9 |
| Wrong predictions | 51 |
| **Overall Accuracy** | **15.0%** |
| True Positives (TP) | 8 |
| True Negatives (TN) | 1 |
| False Positives (FP) | 29 |
| False Negatives (FN) | 22 |
| **Sensitivity (Recall)** | **26.7%** |
| **Specificity** | **3.3%** |
| **Precision** | **21.6%** |
| **F1 Score** | **0.239** |

## Confusion Matrix

|  | Predicted Malignant | Predicted Benign |
|--|:-------------------:|:----------------:|
| **Actual Malignant** | 8 (TP) | 22 (FN) |
| **Actual Benign**    | 29 (FP) | 1 (TN) |

## Malignant Cases (30 / 30)

| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |
|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|
| 1 | LIDC-IDRI-0106 | Malignancy | Malignancy | ✓ | 52.3% | 0.523 | 0.477 |
| 2 | LIDC-IDRI-0132 | Malignancy | Malignancy | ✓ | 53.6% | 0.536 | 0.464 |
| 3 | LIDC-IDRI-0158 | Malignancy | Benign | ✗ | 51.9% | 0.480 | 0.519 |
| 4 | LIDC-IDRI-0184 | Malignancy | Benign | ✗ | 52.5% | 0.475 | 0.525 |
| 5 | LIDC-IDRI-0212 | Malignancy | Benign | ✗ | 50.5% | 0.495 | 0.505 |
| 6 | LIDC-IDRI-0244 | Malignancy | Benign | ✗ | 50.8% | 0.492 | 0.508 |
| 7 | LIDC-IDRI-0271 | Malignancy | Benign | ✗ | 51.2% | 0.488 | 0.512 |
| 8 | LIDC-IDRI-0299 | Malignancy | Benign | ✗ | 51.3% | 0.487 | 0.513 |
| 9 | LIDC-IDRI-0329 | Malignancy | Benign | ✗ | 51.1% | 0.489 | 0.511 |
| 10 | LIDC-IDRI-0360 | Malignancy | Benign | ✗ | 50.7% | 0.493 | 0.507 |
| 11 | LIDC-IDRI-0390 | Malignancy | Benign | ✗ | 50.4% | 0.496 | 0.504 |
| 12 | LIDC-IDRI-0420 | Malignancy | Benign | ✗ | 50.3% | 0.497 | 0.503 |
| 13 | LIDC-IDRI-0450 | Malignancy | Benign | ✗ | 50.2% | 0.498 | 0.502 |
| 14 | LIDC-IDRI-0478 | Malignancy | Benign | ✗ | 50.3% | 0.497 | 0.503 |
| 15 | LIDC-IDRI-0504 | Malignancy | Malignancy | ✓ | 50.1% | 0.501 | 0.499 |
| 16 | LIDC-IDRI-0538 | Malignancy | Malignancy | ✓ | 50.0% | 0.500 | 0.500 |
| 17 | LIDC-IDRI-0568 | Malignancy | Malignancy | ✓ | 50.1% | 0.501 | 0.499 |
| 18 | LIDC-IDRI-0598 | Malignancy | Benign | ✗ | 50.4% | 0.496 | 0.504 |
| 19 | LIDC-IDRI-0631 | Malignancy | Benign | ✗ | 50.3% | 0.497 | 0.503 |
| 20 | LIDC-IDRI-0660 | Malignancy | Benign | ✗ | 50.2% | 0.498 | 0.502 |
| 21 | LIDC-IDRI-0695 | Malignancy | Benign | ✗ | 50.6% | 0.494 | 0.506 |
| 22 | LIDC-IDRI-0724 | Malignancy | Benign | ✗ | 50.6% | 0.494 | 0.506 |
| 23 | LIDC-IDRI-0754 | Malignancy | Benign | ✗ | 50.4% | 0.496 | 0.504 |
| 24 | LIDC-IDRI-0783 | Malignancy | Benign | ✗ | 50.8% | 0.492 | 0.508 |
| 25 | LIDC-IDRI-0811 | Malignancy | Benign | ✗ | 50.2% | 0.498 | 0.502 |
| 26 | LIDC-IDRI-0836 | Malignancy | Malignancy | ✓ | 50.2% | 0.502 | 0.498 |
| 27 | LIDC-IDRI-0864 | Malignancy | Malignancy | ✓ | 50.4% | 0.504 | 0.496 |
| 28 | LIDC-IDRI-0898 | Malignancy | Benign | ✗ | 50.4% | 0.496 | 0.504 |
| 29 | LIDC-IDRI-0929 | Malignancy | Benign | ✗ | 50.0% | 0.500 | 0.500 |
| 30 | LIDC-IDRI-0962 | Malignancy | Malignancy | ✓ | 51.0% | 0.510 | 0.490 |

## Benign Cases (30 / 30)

| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |
|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|
| 1 | LIDC-IDRI-0746 | Benign | Malignancy | ✗ | 50.4% | 0.504 | 0.496 |
| 2 | LIDC-IDRI-0755 | Benign | Malignancy | ✗ | 50.8% | 0.508 | 0.492 |
| 3 | LIDC-IDRI-0760 | Benign | Malignancy | ✗ | 50.2% | 0.502 | 0.498 |
| 4 | LIDC-IDRI-0764 | Benign | Malignancy | ✗ | 51.3% | 0.513 | 0.487 |
| 5 | LIDC-IDRI-0774 | Benign | Malignancy | ✗ | 51.2% | 0.512 | 0.488 |
| 6 | LIDC-IDRI-0784 | Benign | Malignancy | ✗ | 50.2% | 0.502 | 0.498 |
| 7 | LIDC-IDRI-0804 | Benign | Malignancy | ✗ | 50.7% | 0.507 | 0.493 |
| 8 | LIDC-IDRI-0808 | Benign | Malignancy | ✗ | 50.7% | 0.507 | 0.492 |
| 9 | LIDC-IDRI-0839 | Benign | Malignancy | ✗ | 50.0% | 0.500 | 0.500 |
| 10 | LIDC-IDRI-0853 | Benign | Malignancy | ✗ | 50.7% | 0.507 | 0.493 |
| 11 | LIDC-IDRI-0862 | Benign | Malignancy | ✗ | 51.3% | 0.513 | 0.487 |
| 12 | LIDC-IDRI-0876 | Benign | Malignancy | ✗ | 50.9% | 0.509 | 0.491 |
| 13 | LIDC-IDRI-0877 | Benign | Malignancy | ✗ | 50.7% | 0.507 | 0.493 |
| 14 | LIDC-IDRI-0878 | Benign | Malignancy | ✗ | 50.2% | 0.502 | 0.497 |
| 15 | LIDC-IDRI-0881 | Benign | Malignancy | ✗ | 50.8% | 0.508 | 0.492 |
| 16 | LIDC-IDRI-0885 | Benign | Malignancy | ✗ | 50.7% | 0.507 | 0.493 |
| 17 | LIDC-IDRI-0887 | Benign | Malignancy | ✗ | 51.0% | 0.510 | 0.490 |
| 18 | LIDC-IDRI-0889 | Benign | Malignancy | ✗ | 50.9% | 0.509 | 0.491 |
| 19 | LIDC-IDRI-0891 | Benign | Malignancy | ✗ | 51.0% | 0.510 | 0.490 |
| 20 | LIDC-IDRI-0897 | Benign | Malignancy | ✗ | 50.4% | 0.504 | 0.496 |
| 21 | LIDC-IDRI-0900 | Benign | Malignancy | ✗ | 50.9% | 0.509 | 0.491 |
| 22 | LIDC-IDRI-0901 | Benign | Benign | ✓ | 50.1% | 0.499 | 0.501 |
| 23 | LIDC-IDRI-0903 | Benign | Malignancy | ✗ | 51.3% | 0.513 | 0.487 |
| 24 | LIDC-IDRI-0906 | Benign | Malignancy | ✗ | 50.9% | 0.509 | 0.491 |
| 25 | LIDC-IDRI-0918 | Benign | Malignancy | ✗ | 51.1% | 0.511 | 0.489 |
| 26 | LIDC-IDRI-0927 | Benign | Malignancy | ✗ | 51.8% | 0.518 | 0.482 |
| 27 | LIDC-IDRI-0930 | Benign | Malignancy | ✗ | 51.5% | 0.515 | 0.484 |
| 28 | LIDC-IDRI-0931 | Benign | Malignancy | ✗ | 51.7% | 0.517 | 0.483 |
| 29 | LIDC-IDRI-0934 | Benign | Malignancy | ✗ | 51.5% | 0.515 | 0.485 |
| 30 | LIDC-IDRI-0937 | Benign | Malignancy | ✗ | 100.0% | 1.000 | 0.000 |

