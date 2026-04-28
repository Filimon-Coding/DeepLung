# Batch Inference Results — DataProvider

_Generated: 2026-04-16 13:23_

**Dataset:** LIDC-IDRI  |  **Cases run:** 60  |  **Skipped:** 0

## Summary

| Metric | Value |
|--------|-------|
| Total cases run | 60 |
| Correct predictions | 42 |
| Wrong predictions | 18 |
| **Overall Accuracy** | **70.0%** |
| True Positives (TP) | 15 |
| True Negatives (TN) | 27 |
| False Positives (FP) | 3 |
| False Negatives (FN) | 15 |
| **Sensitivity (Recall)** | **50.0%** |
| **Specificity** | **90.0%** |
| **Precision** | **83.3%** |
| **F1 Score** | **0.625** |

## Confusion Matrix

|  | Predicted Malignant | Predicted Benign |
|--|:-------------------:|:----------------:|
| **Actual Malignant** | 15 (TP) | 15 (FN) |
| **Actual Benign**    | 3 (FP) | 27 (TN) |

## Malignant Cases (30 / 30)

| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |
|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|
| 1 | LIDC-IDRI-0106 | Malignancy | Malignancy | ✓ | 85.7% | 0.857 | 0.143 |
| 2 | LIDC-IDRI-0132 | Malignancy | Malignancy | ✓ | 80.9% | 0.809 | 0.191 |
| 3 | LIDC-IDRI-0158 | Malignancy | Benign | ✗ | 56.6% | 0.434 | 0.566 |
| 4 | LIDC-IDRI-0184 | Malignancy | Malignancy | ✓ | 59.6% | 0.596 | 0.404 |
| 5 | LIDC-IDRI-0212 | Malignancy | Malignancy | ✓ | 55.3% | 0.553 | 0.447 |
| 6 | LIDC-IDRI-0244 | Malignancy | Malignancy | ✓ | 68.4% | 0.684 | 0.316 |
| 7 | LIDC-IDRI-0271 | Malignancy | Malignancy | ✓ | 54.1% | 0.541 | 0.459 |
| 8 | LIDC-IDRI-0299 | Malignancy | Benign | ✗ | 58.3% | 0.417 | 0.583 |
| 9 | LIDC-IDRI-0329 | Malignancy | Benign | ✗ | 87.0% | 0.130 | 0.870 |
| 10 | LIDC-IDRI-0360 | Malignancy | Malignancy | ✓ | 56.4% | 0.564 | 0.436 |
| 11 | LIDC-IDRI-0390 | Malignancy | Malignancy | ✓ | 54.2% | 0.542 | 0.458 |
| 12 | LIDC-IDRI-0420 | Malignancy | Benign | ✗ | 91.7% | 0.083 | 0.917 |
| 13 | LIDC-IDRI-0450 | Malignancy | Benign | ✗ | 72.2% | 0.278 | 0.722 |
| 14 | LIDC-IDRI-0478 | Malignancy | Malignancy | ✓ | 74.7% | 0.747 | 0.253 |
| 15 | LIDC-IDRI-0504 | Malignancy | Malignancy | ✓ | 72.0% | 0.720 | 0.280 |
| 16 | LIDC-IDRI-0538 | Malignancy | Malignancy | ✓ | 70.4% | 0.704 | 0.296 |
| 17 | LIDC-IDRI-0568 | Malignancy | Benign | ✗ | 57.2% | 0.428 | 0.572 |
| 18 | LIDC-IDRI-0598 | Malignancy | Benign | ✗ | 67.7% | 0.323 | 0.677 |
| 19 | LIDC-IDRI-0631 | Malignancy | Malignancy | ✓ | 59.5% | 0.595 | 0.405 |
| 20 | LIDC-IDRI-0660 | Malignancy | Benign | ✗ | 69.8% | 0.302 | 0.698 |
| 21 | LIDC-IDRI-0695 | Malignancy | Benign | ✗ | 66.3% | 0.337 | 0.663 |
| 22 | LIDC-IDRI-0724 | Malignancy | Malignancy | ✓ | 96.0% | 0.960 | 0.040 |
| 23 | LIDC-IDRI-0754 | Malignancy | Benign | ✗ | 67.8% | 0.322 | 0.678 |
| 24 | LIDC-IDRI-0783 | Malignancy | Benign | ✗ | 64.3% | 0.357 | 0.643 |
| 25 | LIDC-IDRI-0811 | Malignancy | Malignancy | ✓ | 70.1% | 0.701 | 0.299 |
| 26 | LIDC-IDRI-0836 | Malignancy | Benign | ✗ | 96.2% | 0.038 | 0.962 |
| 27 | LIDC-IDRI-0864 | Malignancy | Benign | ✗ | 97.0% | 0.030 | 0.970 |
| 28 | LIDC-IDRI-0898 | Malignancy | Malignancy | ✓ | 73.6% | 0.736 | 0.264 |
| 29 | LIDC-IDRI-0929 | Malignancy | Benign | ✗ | 77.7% | 0.223 | 0.777 |
| 30 | LIDC-IDRI-0962 | Malignancy | Benign | ✗ | 52.1% | 0.479 | 0.521 |

## Benign Cases (30 / 30)

| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |
|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|
| 1 | LIDC-IDRI-0746 | Benign | Benign | ✓ | 72.3% | 0.277 | 0.723 |
| 2 | LIDC-IDRI-0755 | Benign | Benign | ✓ | 76.7% | 0.233 | 0.767 |
| 3 | LIDC-IDRI-0760 | Benign | Benign | ✓ | 66.5% | 0.335 | 0.665 |
| 4 | LIDC-IDRI-0764 | Benign | Benign | ✓ | 64.1% | 0.359 | 0.641 |
| 5 | LIDC-IDRI-0774 | Benign | Benign | ✓ | 68.7% | 0.313 | 0.687 |
| 6 | LIDC-IDRI-0784 | Benign | Benign | ✓ | 75.5% | 0.245 | 0.755 |
| 7 | LIDC-IDRI-0804 | Benign | Benign | ✓ | 77.0% | 0.230 | 0.770 |
| 8 | LIDC-IDRI-0808 | Benign | Malignancy | ✗ | 73.6% | 0.736 | 0.264 |
| 9 | LIDC-IDRI-0839 | Benign | Benign | ✓ | 78.7% | 0.213 | 0.787 |
| 10 | LIDC-IDRI-0853 | Benign | Benign | ✓ | 77.0% | 0.230 | 0.770 |
| 11 | LIDC-IDRI-0862 | Benign | Benign | ✓ | 68.8% | 0.312 | 0.688 |
| 12 | LIDC-IDRI-0876 | Benign | Benign | ✓ | 73.4% | 0.266 | 0.734 |
| 13 | LIDC-IDRI-0877 | Benign | Benign | ✓ | 53.4% | 0.466 | 0.534 |
| 14 | LIDC-IDRI-0878 | Benign | Benign | ✓ | 72.2% | 0.278 | 0.722 |
| 15 | LIDC-IDRI-0881 | Benign | Benign | ✓ | 82.7% | 0.173 | 0.827 |
| 16 | LIDC-IDRI-0885 | Benign | Benign | ✓ | 88.9% | 0.111 | 0.889 |
| 17 | LIDC-IDRI-0887 | Benign | Benign | ✓ | 87.2% | 0.128 | 0.872 |
| 18 | LIDC-IDRI-0889 | Benign | Benign | ✓ | 92.6% | 0.074 | 0.926 |
| 19 | LIDC-IDRI-0891 | Benign | Benign | ✓ | 68.2% | 0.318 | 0.682 |
| 20 | LIDC-IDRI-0897 | Benign | Benign | ✓ | 57.9% | 0.421 | 0.579 |
| 21 | LIDC-IDRI-0900 | Benign | Benign | ✓ | 76.8% | 0.232 | 0.768 |
| 22 | LIDC-IDRI-0901 | Benign | Malignancy | ✗ | 82.7% | 0.827 | 0.173 |
| 23 | LIDC-IDRI-0903 | Benign | Benign | ✓ | 78.5% | 0.215 | 0.785 |
| 24 | LIDC-IDRI-0906 | Benign | Benign | ✓ | 56.0% | 0.440 | 0.560 |
| 25 | LIDC-IDRI-0918 | Benign | Benign | ✓ | 57.5% | 0.425 | 0.575 |
| 26 | LIDC-IDRI-0927 | Benign | Benign | ✓ | 96.7% | 0.033 | 0.967 |
| 27 | LIDC-IDRI-0930 | Benign | Benign | ✓ | 70.3% | 0.297 | 0.703 |
| 28 | LIDC-IDRI-0931 | Benign | Benign | ✓ | 93.9% | 0.061 | 0.939 |
| 29 | LIDC-IDRI-0934 | Benign | Benign | ✓ | 71.2% | 0.288 | 0.712 |
| 30 | LIDC-IDRI-0937 | Benign | Malignancy | ✗ | 65.2% | 0.652 | 0.348 |

