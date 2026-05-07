# Batch Inference Results — DataProvider

_Generated: 2026-04-28 09:31_

**Dataset:** LIDC-IDRI  |  **Cases run:** 60  |  **Skipped:** 0

## Summary

| Metric | Value |
|--------|-------|
| Total cases run | 60 |
| Correct predictions | 34 |
| Wrong predictions | 26 |
| **Overall Accuracy** | **56.7%** |
| True Positives (TP) | 6 |
| True Negatives (TN) | 28 |
| False Positives (FP) | 2 |
| False Negatives (FN) | 24 |
| **Sensitivity (Recall)** | **20.0%** |
| **Specificity** | **93.3%** |
| **Precision** | **75.0%** |
| **F1 Score** | **0.316** |

## Confusion Matrix

|  | Predicted Malignant | Predicted Benign |
|--|:-------------------:|:----------------:|
| **Actual Malignant** | 6 (TP) | 24 (FN) |
| **Actual Benign**    | 2 (FP) | 28 (TN) |

## Malignant Cases (30 / 30)

| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |
|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|
| 1 | LIDC-IDRI-0106 | Malignancy | Benign | ✗ | 71.0% | 0.290 | 0.710 |
| 2 | LIDC-IDRI-0132 | Malignancy | Benign | ✗ | 58.0% | 0.420 | 0.580 |
| 3 | LIDC-IDRI-0158 | Malignancy | Benign | ✗ | 52.9% | 0.471 | 0.529 |
| 4 | LIDC-IDRI-0184 | Malignancy | Malignancy | ✓ | 99.9% | 0.999 | 0.001 |
| 5 | LIDC-IDRI-0212 | Malignancy | Malignancy | ✓ | 86.7% | 0.867 | 0.133 |
| 6 | LIDC-IDRI-0244 | Malignancy | Benign | ✗ | 75.5% | 0.245 | 0.755 |
| 7 | LIDC-IDRI-0271 | Malignancy | Malignancy | ✓ | 94.1% | 0.941 | 0.059 |
| 8 | LIDC-IDRI-0299 | Malignancy | Benign | ✗ | 74.7% | 0.253 | 0.747 |
| 9 | LIDC-IDRI-0329 | Malignancy | Benign | ✗ | 61.9% | 0.381 | 0.619 |
| 10 | LIDC-IDRI-0360 | Malignancy | Benign | ✗ | 85.9% | 0.141 | 0.859 |
| 11 | LIDC-IDRI-0390 | Malignancy | Benign | ✗ | 54.1% | 0.459 | 0.541 |
| 12 | LIDC-IDRI-0420 | Malignancy | Benign | ✗ | 65.4% | 0.346 | 0.654 |
| 13 | LIDC-IDRI-0450 | Malignancy | Benign | ✗ | 93.6% | 0.064 | 0.936 |
| 14 | LIDC-IDRI-0478 | Malignancy | Benign | ✗ | 92.9% | 0.071 | 0.929 |
| 15 | LIDC-IDRI-0504 | Malignancy | Benign | ✗ | 54.8% | 0.452 | 0.548 |
| 16 | LIDC-IDRI-0538 | Malignancy | Benign | ✗ | 78.6% | 0.214 | 0.786 |
| 17 | LIDC-IDRI-0568 | Malignancy | Benign | ✗ | 74.4% | 0.256 | 0.744 |
| 18 | LIDC-IDRI-0598 | Malignancy | Benign | ✗ | 91.3% | 0.087 | 0.913 |
| 19 | LIDC-IDRI-0631 | Malignancy | Benign | ✗ | 92.7% | 0.073 | 0.927 |
| 20 | LIDC-IDRI-0660 | Malignancy | Benign | ✗ | 84.3% | 0.157 | 0.843 |
| 21 | LIDC-IDRI-0695 | Malignancy | Malignancy | ✓ | 60.5% | 0.605 | 0.395 |
| 22 | LIDC-IDRI-0724 | Malignancy | Malignancy | ✓ | 57.6% | 0.576 | 0.424 |
| 23 | LIDC-IDRI-0754 | Malignancy | Benign | ✗ | 72.6% | 0.274 | 0.726 |
| 24 | LIDC-IDRI-0783 | Malignancy | Benign | ✗ | 97.7% | 0.023 | 0.977 |
| 25 | LIDC-IDRI-0811 | Malignancy | Benign | ✗ | 93.4% | 0.066 | 0.934 |
| 26 | LIDC-IDRI-0836 | Malignancy | Benign | ✗ | 58.1% | 0.419 | 0.581 |
| 27 | LIDC-IDRI-0864 | Malignancy | Malignancy | ✓ | 54.4% | 0.544 | 0.456 |
| 28 | LIDC-IDRI-0898 | Malignancy | Benign | ✗ | 94.6% | 0.054 | 0.946 |
| 29 | LIDC-IDRI-0929 | Malignancy | Benign | ✗ | 97.4% | 0.026 | 0.974 |
| 30 | LIDC-IDRI-0962 | Malignancy | Benign | ✗ | 50.5% | 0.495 | 0.505 |

## Benign Cases (30 / 30)

| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |
|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|
| 1 | LIDC-IDRI-0746 | Benign | Malignancy | ✗ | 74.5% | 0.745 | 0.255 |
| 2 | LIDC-IDRI-0755 | Benign | Benign | ✓ | 92.3% | 0.077 | 0.923 |
| 3 | LIDC-IDRI-0760 | Benign | Benign | ✓ | 98.2% | 0.018 | 0.982 |
| 4 | LIDC-IDRI-0764 | Benign | Benign | ✓ | 87.0% | 0.130 | 0.870 |
| 5 | LIDC-IDRI-0774 | Benign | Benign | ✓ | 79.5% | 0.205 | 0.795 |
| 6 | LIDC-IDRI-0784 | Benign | Benign | ✓ | 85.4% | 0.146 | 0.854 |
| 7 | LIDC-IDRI-0804 | Benign | Benign | ✓ | 94.9% | 0.051 | 0.949 |
| 8 | LIDC-IDRI-0808 | Benign | Benign | ✓ | 94.1% | 0.059 | 0.941 |
| 9 | LIDC-IDRI-0839 | Benign | Benign | ✓ | 60.5% | 0.395 | 0.605 |
| 10 | LIDC-IDRI-0853 | Benign | Benign | ✓ | 79.4% | 0.206 | 0.794 |
| 11 | LIDC-IDRI-0862 | Benign | Benign | ✓ | 87.6% | 0.124 | 0.876 |
| 12 | LIDC-IDRI-0876 | Benign | Benign | ✓ | 62.1% | 0.379 | 0.621 |
| 13 | LIDC-IDRI-0877 | Benign | Benign | ✓ | 84.5% | 0.155 | 0.845 |
| 14 | LIDC-IDRI-0878 | Benign | Benign | ✓ | 56.7% | 0.433 | 0.567 |
| 15 | LIDC-IDRI-0881 | Benign | Benign | ✓ | 88.8% | 0.112 | 0.888 |
| 16 | LIDC-IDRI-0885 | Benign | Benign | ✓ | 53.4% | 0.466 | 0.534 |
| 17 | LIDC-IDRI-0887 | Benign | Benign | ✓ | 94.5% | 0.055 | 0.945 |
| 18 | LIDC-IDRI-0889 | Benign | Benign | ✓ | 89.3% | 0.107 | 0.893 |
| 19 | LIDC-IDRI-0891 | Benign | Benign | ✓ | 86.6% | 0.134 | 0.866 |
| 20 | LIDC-IDRI-0897 | Benign | Benign | ✓ | 64.7% | 0.353 | 0.647 |
| 21 | LIDC-IDRI-0900 | Benign | Benign | ✓ | 75.5% | 0.245 | 0.755 |
| 22 | LIDC-IDRI-0901 | Benign | Benign | ✓ | 52.8% | 0.472 | 0.528 |
| 23 | LIDC-IDRI-0903 | Benign | Benign | ✓ | 97.1% | 0.029 | 0.971 |
| 24 | LIDC-IDRI-0906 | Benign | Benign | ✓ | 58.0% | 0.420 | 0.580 |
| 25 | LIDC-IDRI-0918 | Benign | Benign | ✓ | 69.7% | 0.303 | 0.697 |
| 26 | LIDC-IDRI-0927 | Benign | Benign | ✓ | 75.8% | 0.242 | 0.758 |
| 27 | LIDC-IDRI-0930 | Benign | Benign | ✓ | 87.2% | 0.128 | 0.872 |
| 28 | LIDC-IDRI-0931 | Benign | Benign | ✓ | 81.2% | 0.188 | 0.812 |
| 29 | LIDC-IDRI-0934 | Benign | Benign | ✓ | 93.2% | 0.068 | 0.932 |
| 30 | LIDC-IDRI-0937 | Benign | Malignancy | ✗ | 62.8% | 0.628 | 0.372 |

