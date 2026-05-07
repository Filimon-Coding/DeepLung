# Batch Inference Results — DataProvider

_Generated: 2026-04-29 13:19_

**Dataset:** LIDC-IDRI  |  **Target:** 50 malignant + 50 benign  |  **Cases run:** 100  |  **Skipped:** 0

## Summary

| Metric | Value |
|--------|-------|
| Total cases run | 100 |
| Correct predictions | 76 |
| Wrong predictions | 24 |
| **Overall Accuracy** | **76.0%** |
| True Positives (TP) | 42 |
| True Negatives (TN) | 34 |
| False Positives (FP) | 16 |
| False Negatives (FN) | 8 |
| **Sensitivity (Recall)** | **84.0%** |
| **Specificity** | **68.0%** |
| **Precision** | **72.4%** |
| **F1 Score** | **0.778** |

## Confusion Matrix

|  | Predicted Malignant | Predicted Benign |
|--|:-------------------:|:----------------:|
| **Actual Malignant** | 42 (TP) | 8 (FN) |
| **Actual Benign**    | 16 (FP) | 34 (TN) |

## Malignant Cases (50 / 50)

| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |
|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|
| 1 | LIDC-IDRI-0012 | Malignancy | Malignancy | ✓ | 76.5% | 0.765 | 0.235 |
| 2 | LIDC-IDRI-0015 | Malignancy | Malignancy | ✓ | 58.9% | 0.589 | 0.411 |
| 3 | LIDC-IDRI-0102 | Malignancy | Malignancy | ✓ | 74.8% | 0.748 | 0.252 |
| 4 | LIDC-IDRI-0018 | Malignancy | Malignancy | ✓ | 73.0% | 0.730 | 0.270 |
| 5 | LIDC-IDRI-0054 | Malignancy | Malignancy | ✓ | 77.5% | 0.775 | 0.225 |
| 6 | LIDC-IDRI-0037 | Malignancy | Malignancy | ✓ | 70.6% | 0.706 | 0.294 |
| 7 | LIDC-IDRI-0004 | Malignancy | Malignancy | ✓ | 54.9% | 0.549 | 0.451 |
| 8 | LIDC-IDRI-0077 | Malignancy | Benign | ✗ | 66.9% | 0.331 | 0.669 |
| 9 | LIDC-IDRI-0094 | Malignancy | Benign | ✗ | 93.3% | 0.067 | 0.933 |
| 10 | LIDC-IDRI-0092 | Malignancy | Malignancy | ✓ | 51.8% | 0.518 | 0.482 |
| 11 | LIDC-IDRI-0063 | Malignancy | Malignancy | ✓ | 85.4% | 0.854 | 0.146 |
| 12 | LIDC-IDRI-0011 | Malignancy | Malignancy | ✓ | 65.0% | 0.650 | 0.350 |
| 13 | LIDC-IDRI-0047 | Malignancy | Malignancy | ✓ | 86.9% | 0.869 | 0.131 |
| 14 | LIDC-IDRI-0051 | Malignancy | Malignancy | ✓ | 84.4% | 0.844 | 0.156 |
| 15 | LIDC-IDRI-0058 | Malignancy | Malignancy | ✓ | 50.2% | 0.502 | 0.498 |
| 16 | LIDC-IDRI-0006 | Malignancy | Malignancy | ✓ | 85.9% | 0.859 | 0.141 |
| 17 | LIDC-IDRI-0048 | Malignancy | Benign | ✗ | 60.2% | 0.398 | 0.602 |
| 18 | LIDC-IDRI-0002 | Malignancy | Benign | ✗ | 59.1% | 0.409 | 0.591 |
| 19 | LIDC-IDRI-0029 | Malignancy | Malignancy | ✓ | 60.1% | 0.601 | 0.399 |
| 20 | LIDC-IDRI-0104 | Malignancy | Malignancy | ✓ | 76.6% | 0.766 | 0.234 |
| 21 | LIDC-IDRI-0020 | Malignancy | Malignancy | ✓ | 53.4% | 0.534 | 0.466 |
| 22 | LIDC-IDRI-0061 | Malignancy | Malignancy | ✓ | 60.8% | 0.608 | 0.392 |
| 23 | LIDC-IDRI-0105 | Malignancy | Malignancy | ✓ | 71.8% | 0.718 | 0.282 |
| 24 | LIDC-IDRI-0019 | Malignancy | Malignancy | ✓ | 61.8% | 0.618 | 0.382 |
| 25 | LIDC-IDRI-0039 | Malignancy | Malignancy | ✓ | 55.6% | 0.556 | 0.444 |
| 26 | LIDC-IDRI-0046 | Malignancy | Malignancy | ✓ | 77.3% | 0.773 | 0.227 |
| 27 | LIDC-IDRI-0079 | Malignancy | Malignancy | ✓ | 79.8% | 0.798 | 0.202 |
| 28 | LIDC-IDRI-0045 | Malignancy | Malignancy | ✓ | 67.0% | 0.670 | 0.330 |
| 29 | LIDC-IDRI-0016 | Malignancy | Malignancy | ✓ | 75.5% | 0.755 | 0.245 |
| 30 | LIDC-IDRI-0069 | Malignancy | Benign | ✗ | 56.2% | 0.438 | 0.562 |
| 31 | LIDC-IDRI-0082 | Malignancy | Malignancy | ✓ | 99.0% | 0.990 | 0.010 |
| 32 | LIDC-IDRI-0041 | Malignancy | Malignancy | ✓ | 70.4% | 0.704 | 0.296 |
| 33 | LIDC-IDRI-0033 | Malignancy | Malignancy | ✓ | 82.5% | 0.825 | 0.175 |
| 34 | LIDC-IDRI-0034 | Malignancy | Benign | ✗ | 61.2% | 0.388 | 0.612 |
| 35 | LIDC-IDRI-0074 | Malignancy | Benign | ✗ | 74.8% | 0.252 | 0.748 |
| 36 | LIDC-IDRI-0010 | Malignancy | Malignancy | ✓ | 55.0% | 0.550 | 0.450 |
| 37 | LIDC-IDRI-0064 | Malignancy | Malignancy | ✓ | 82.9% | 0.829 | 0.171 |
| 38 | LIDC-IDRI-0076 | Malignancy | Malignancy | ✓ | 64.1% | 0.641 | 0.359 |
| 39 | LIDC-IDRI-0007 | Malignancy | Benign | ✗ | 85.6% | 0.144 | 0.856 |
| 40 | LIDC-IDRI-0078 | Malignancy | Malignancy | ✓ | 58.2% | 0.582 | 0.418 |
| 41 | LIDC-IDRI-0090 | Malignancy | Malignancy | ✓ | 85.9% | 0.859 | 0.141 |
| 42 | LIDC-IDRI-0022 | Malignancy | Malignancy | ✓ | 55.2% | 0.552 | 0.448 |
| 43 | LIDC-IDRI-0031 | Malignancy | Malignancy | ✓ | 85.9% | 0.859 | 0.141 |
| 44 | LIDC-IDRI-0070 | Malignancy | Malignancy | ✓ | 83.7% | 0.837 | 0.163 |
| 45 | LIDC-IDRI-0099 | Malignancy | Malignancy | ✓ | 88.8% | 0.888 | 0.112 |
| 46 | LIDC-IDRI-0021 | Malignancy | Malignancy | ✓ | 55.7% | 0.557 | 0.443 |
| 47 | LIDC-IDRI-0083 | Malignancy | Malignancy | ✓ | 87.9% | 0.879 | 0.121 |
| 48 | LIDC-IDRI-0091 | Malignancy | Malignancy | ✓ | 89.4% | 0.894 | 0.106 |
| 49 | LIDC-IDRI-0065 | Malignancy | Malignancy | ✓ | 63.9% | 0.639 | 0.361 |
| 50 | LIDC-IDRI-0072 | Malignancy | Malignancy | ✓ | 53.5% | 0.535 | 0.465 |

## Benign Cases (50 / 50)

| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |
|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|
| 1 | LIDC-IDRI-0107 | Benign | Malignancy | ✗ | 92.6% | 0.926 | 0.074 |
| 2 | LIDC-IDRI-0519 | Benign | Malignancy | ✗ | 51.2% | 0.512 | 0.488 |
| 3 | LIDC-IDRI-0710 | Benign | Malignancy | ✗ | 59.3% | 0.593 | 0.407 |
| 4 | LIDC-IDRI-0218 | Benign | Malignancy | ✗ | 64.4% | 0.644 | 0.356 |
| 5 | LIDC-IDRI-0689 | Benign | Malignancy | ✗ | 65.2% | 0.652 | 0.348 |
| 6 | LIDC-IDRI-0293 | Benign | Benign | ✓ | 60.9% | 0.391 | 0.609 |
| 7 | LIDC-IDRI-0143 | Benign | Malignancy | ✗ | 78.5% | 0.785 | 0.215 |
| 8 | LIDC-IDRI-0571 | Benign | Benign | ✓ | 95.8% | 0.042 | 0.958 |
| 9 | LIDC-IDRI-0685 | Benign | Malignancy | ✗ | 67.4% | 0.674 | 0.326 |
| 10 | LIDC-IDRI-0322 | Benign | Benign | ✓ | 85.0% | 0.150 | 0.850 |
| 11 | LIDC-IDRI-0174 | Benign | Malignancy | ✗ | 86.1% | 0.861 | 0.139 |
| 12 | LIDC-IDRI-0711 | Benign | Benign | ✓ | 76.8% | 0.232 | 0.768 |
| 13 | LIDC-IDRI-0383 | Benign | Benign | ✓ | 55.5% | 0.445 | 0.555 |
| 14 | LIDC-IDRI-0361 | Benign | Benign | ✓ | 79.4% | 0.206 | 0.794 |
| 15 | LIDC-IDRI-0716 | Benign | Benign | ✓ | 91.7% | 0.083 | 0.917 |
| 16 | LIDC-IDRI-0189 | Benign | Benign | ✓ | 94.1% | 0.059 | 0.941 |
| 17 | LIDC-IDRI-0316 | Benign | Benign | ✓ | 98.5% | 0.015 | 0.985 |
| 18 | LIDC-IDRI-0718 | Benign | Malignancy | ✗ | 54.0% | 0.540 | 0.460 |
| 19 | LIDC-IDRI-0389 | Benign | Malignancy | ✗ | 73.8% | 0.738 | 0.262 |
| 20 | LIDC-IDRI-0295 | Benign | Benign | ✓ | 61.5% | 0.385 | 0.615 |
| 21 | LIDC-IDRI-0071 | Benign | Benign | ✓ | 59.4% | 0.406 | 0.594 |
| 22 | LIDC-IDRI-0573 | Benign | Benign | ✓ | 87.8% | 0.122 | 0.878 |
| 23 | LIDC-IDRI-0253 | Benign | Malignancy | ✗ | 84.9% | 0.849 | 0.151 |
| 24 | LIDC-IDRI-0224 | Benign | Malignancy | ✗ | 87.1% | 0.871 | 0.129 |
| 25 | LIDC-IDRI-0306 | Benign | Benign | ✓ | 89.8% | 0.102 | 0.898 |
| 26 | LIDC-IDRI-0536 | Benign | Malignancy | ✗ | 60.4% | 0.604 | 0.396 |
| 27 | LIDC-IDRI-0589 | Benign | Benign | ✓ | 89.1% | 0.109 | 0.891 |
| 28 | LIDC-IDRI-0691 | Benign | Benign | ✓ | 85.6% | 0.144 | 0.856 |
| 29 | LIDC-IDRI-0731 | Benign | Benign | ✓ | 65.4% | 0.346 | 0.654 |
| 30 | LIDC-IDRI-0511 | Benign | Benign | ✓ | 97.1% | 0.029 | 0.971 |
| 31 | LIDC-IDRI-0632 | Benign | Benign | ✓ | 74.3% | 0.257 | 0.743 |
| 32 | LIDC-IDRI-0472 | Benign | Benign | ✓ | 98.1% | 0.019 | 0.981 |
| 33 | LIDC-IDRI-0225 | Benign | Benign | ✓ | 55.7% | 0.443 | 0.557 |
| 34 | LIDC-IDRI-0668 | Benign | Benign | ✓ | 96.9% | 0.031 | 0.969 |
| 35 | LIDC-IDRI-0032 | Benign | Malignancy | ✗ | 50.4% | 0.504 | 0.496 |
| 36 | LIDC-IDRI-0417 | Benign | Benign | ✓ | 97.9% | 0.021 | 0.979 |
| 37 | LIDC-IDRI-0428 | Benign | Benign | ✓ | 59.8% | 0.402 | 0.598 |
| 38 | LIDC-IDRI-0482 | Benign | Benign | ✓ | 90.0% | 0.100 | 0.900 |
| 39 | LIDC-IDRI-0572 | Benign | Benign | ✓ | 63.2% | 0.368 | 0.632 |
| 40 | LIDC-IDRI-0425 | Benign | Benign | ✓ | 83.7% | 0.163 | 0.837 |
| 41 | LIDC-IDRI-0653 | Benign | Benign | ✓ | 73.7% | 0.263 | 0.737 |
| 42 | LIDC-IDRI-0307 | Benign | Benign | ✓ | 52.8% | 0.472 | 0.528 |
| 43 | LIDC-IDRI-0514 | Benign | Benign | ✓ | 87.4% | 0.126 | 0.874 |
| 44 | LIDC-IDRI-0401 | Benign | Benign | ✓ | 70.2% | 0.298 | 0.702 |
| 45 | LIDC-IDRI-0679 | Benign | Benign | ✓ | 74.4% | 0.256 | 0.744 |
| 46 | LIDC-IDRI-0512 | Benign | Malignancy | ✗ | 55.4% | 0.554 | 0.446 |
| 47 | LIDC-IDRI-0690 | Benign | Benign | ✓ | 78.2% | 0.218 | 0.782 |
| 48 | LIDC-IDRI-0627 | Benign | Benign | ✓ | 74.9% | 0.251 | 0.749 |
| 49 | LIDC-IDRI-0331 | Benign | Malignancy | ✗ | 67.4% | 0.674 | 0.326 |
| 50 | LIDC-IDRI-0239 | Benign | Benign | ✓ | 62.3% | 0.377 | 0.623 |

