# Batch Inference Results — underdev4 (MedicalNet ResNet-18)

_Generated: 2026-04-28 11:06_

**Dataset:** LIDC-IDRI  |  **Cases run:** 60  |  **Skipped:** 0

## Summary

| Metric | Value |
|--------|-------|
| Total cases run | 60 |
| Correct predictions | 31 |
| Wrong predictions | 29 |
| **Overall Accuracy** | **51.7%** |
| True Positives (TP) | 8 |
| True Negatives (TN) | 23 |
| False Positives (FP) | 7 |
| False Negatives (FN) | 22 |
| **Sensitivity (Recall)** | **26.7%** |
| **Specificity** | **76.7%** |
| **Precision** | **53.3%** |
| **F1 Score** | **0.356** |

## Confusion Matrix

|  | Predicted Malignant | Predicted Benign |
|--|:-------------------:|:----------------:|
| **Actual Malignant** | 8 (TP) | 22 (FN) |
| **Actual Benign**    | 7 (FP) | 23 (TN) |

## Malignant Cases (30 / 30)

| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |
|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|
| 1 | LIDC-IDRI-0106 | Malignancy | Benign | ✗ | 65.8% | 0.342 | 0.658 |
| 2 | LIDC-IDRI-0132 | Malignancy | Benign | ✗ | 60.0% | 0.401 | 0.600 |
| 3 | LIDC-IDRI-0158 | Malignancy | Benign | ✗ | 68.8% | 0.312 | 0.688 |
| 4 | LIDC-IDRI-0184 | Malignancy | Malignancy | ✓ | 99.7% | 0.997 | 0.003 |
| 5 | LIDC-IDRI-0212 | Malignancy | Benign | ✗ | 70.0% | 0.300 | 0.700 |
| 6 | LIDC-IDRI-0244 | Malignancy | Benign | ✗ | 65.3% | 0.347 | 0.653 |
| 7 | LIDC-IDRI-0271 | Malignancy | Malignancy | ✓ | 99.7% | 0.997 | 0.003 |
| 8 | LIDC-IDRI-0299 | Malignancy | Benign | ✗ | 70.2% | 0.298 | 0.702 |
| 9 | LIDC-IDRI-0329 | Malignancy | Benign | ✗ | 70.2% | 0.298 | 0.702 |
| 10 | LIDC-IDRI-0360 | Malignancy | Benign | ✗ | 67.8% | 0.322 | 0.678 |
| 11 | LIDC-IDRI-0390 | Malignancy | Malignancy | ✓ | 92.3% | 0.923 | 0.077 |
| 12 | LIDC-IDRI-0420 | Malignancy | Benign | ✗ | 68.0% | 0.320 | 0.680 |
| 13 | LIDC-IDRI-0450 | Malignancy | Benign | ✗ | 68.6% | 0.314 | 0.686 |
| 14 | LIDC-IDRI-0478 | Malignancy | Benign | ✗ | 68.0% | 0.320 | 0.680 |
| 15 | LIDC-IDRI-0504 | Malignancy | Malignancy | ✓ | 100.0% | 1.000 | 0.000 |
| 16 | LIDC-IDRI-0538 | Malignancy | Benign | ✗ | 69.3% | 0.306 | 0.694 |
| 17 | LIDC-IDRI-0568 | Malignancy | Benign | ✗ | 67.9% | 0.321 | 0.679 |
| 18 | LIDC-IDRI-0598 | Malignancy | Benign | ✗ | 68.8% | 0.312 | 0.688 |
| 19 | LIDC-IDRI-0631 | Malignancy | Benign | ✗ | 69.5% | 0.305 | 0.695 |
| 20 | LIDC-IDRI-0660 | Malignancy | Benign | ✗ | 67.8% | 0.322 | 0.678 |
| 21 | LIDC-IDRI-0695 | Malignancy | Benign | ✗ | 68.3% | 0.317 | 0.683 |
| 22 | LIDC-IDRI-0724 | Malignancy | Benign | ✗ | 66.2% | 0.338 | 0.662 |
| 23 | LIDC-IDRI-0754 | Malignancy | Benign | ✗ | 67.5% | 0.325 | 0.675 |
| 24 | LIDC-IDRI-0783 | Malignancy | Benign | ✗ | 67.8% | 0.322 | 0.678 |
| 25 | LIDC-IDRI-0811 | Malignancy | Malignancy | ✓ | 100.0% | 1.000 | 0.000 |
| 26 | LIDC-IDRI-0836 | Malignancy | Malignancy | ✓ | 99.9% | 0.999 | 0.001 |
| 27 | LIDC-IDRI-0864 | Malignancy | Benign | ✗ | 67.0% | 0.330 | 0.670 |
| 28 | LIDC-IDRI-0898 | Malignancy | Malignancy | ✓ | 100.0% | 1.000 | 0.000 |
| 29 | LIDC-IDRI-0929 | Malignancy | Benign | ✗ | 67.1% | 0.329 | 0.671 |
| 30 | LIDC-IDRI-0962 | Malignancy | Malignancy | ✓ | 100.0% | 1.000 | 0.000 |

## Benign Cases (30 / 30)

| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |
|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|
| 1 | LIDC-IDRI-0746 | Benign | Benign | ✓ | 68.3% | 0.317 | 0.683 |
| 2 | LIDC-IDRI-0755 | Benign | Benign | ✓ | 68.8% | 0.312 | 0.688 |
| 3 | LIDC-IDRI-0760 | Benign | Benign | ✓ | 67.5% | 0.325 | 0.675 |
| 4 | LIDC-IDRI-0764 | Benign | Benign | ✓ | 69.4% | 0.306 | 0.694 |
| 5 | LIDC-IDRI-0774 | Benign | Benign | ✓ | 68.1% | 0.319 | 0.681 |
| 6 | LIDC-IDRI-0784 | Benign | Benign | ✓ | 67.6% | 0.324 | 0.676 |
| 7 | LIDC-IDRI-0804 | Benign | Benign | ✓ | 67.8% | 0.322 | 0.678 |
| 8 | LIDC-IDRI-0808 | Benign | Malignancy | ✗ | 100.0% | 1.000 | 0.000 |
| 9 | LIDC-IDRI-0839 | Benign | Benign | ✓ | 67.6% | 0.324 | 0.676 |
| 10 | LIDC-IDRI-0853 | Benign | Malignancy | ✗ | 99.8% | 0.998 | 0.002 |
| 11 | LIDC-IDRI-0862 | Benign | Benign | ✓ | 68.4% | 0.316 | 0.684 |
| 12 | LIDC-IDRI-0876 | Benign | Benign | ✓ | 67.3% | 0.327 | 0.673 |
| 13 | LIDC-IDRI-0877 | Benign | Benign | ✓ | 66.8% | 0.333 | 0.667 |
| 14 | LIDC-IDRI-0878 | Benign | Benign | ✓ | 65.5% | 0.345 | 0.655 |
| 15 | LIDC-IDRI-0881 | Benign | Malignancy | ✗ | 100.0% | 1.000 | 0.000 |
| 16 | LIDC-IDRI-0885 | Benign | Benign | ✓ | 68.1% | 0.319 | 0.681 |
| 17 | LIDC-IDRI-0887 | Benign | Benign | ✓ | 66.1% | 0.339 | 0.661 |
| 18 | LIDC-IDRI-0889 | Benign | Benign | ✓ | 67.2% | 0.328 | 0.672 |
| 19 | LIDC-IDRI-0891 | Benign | Benign | ✓ | 67.8% | 0.322 | 0.678 |
| 20 | LIDC-IDRI-0897 | Benign | Benign | ✓ | 67.5% | 0.326 | 0.674 |
| 21 | LIDC-IDRI-0900 | Benign | Benign | ✓ | 61.7% | 0.383 | 0.617 |
| 22 | LIDC-IDRI-0901 | Benign | Malignancy | ✗ | 100.0% | 1.000 | 0.000 |
| 23 | LIDC-IDRI-0903 | Benign | Benign | ✓ | 67.3% | 0.327 | 0.673 |
| 24 | LIDC-IDRI-0906 | Benign | Benign | ✓ | 67.1% | 0.329 | 0.671 |
| 25 | LIDC-IDRI-0918 | Benign | Malignancy | ✗ | 100.0% | 1.000 | 0.000 |
| 26 | LIDC-IDRI-0927 | Benign | Benign | ✓ | 67.3% | 0.327 | 0.673 |
| 27 | LIDC-IDRI-0930 | Benign | Malignancy | ✗ | 61.2% | 0.612 | 0.388 |
| 28 | LIDC-IDRI-0931 | Benign | Benign | ✓ | 66.6% | 0.334 | 0.666 |
| 29 | LIDC-IDRI-0934 | Benign | Benign | ✓ | 64.1% | 0.359 | 0.641 |
| 30 | LIDC-IDRI-0937 | Benign | Malignancy | ✗ | 100.0% | 1.000 | 0.000 |

