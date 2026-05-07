# Batch Inference Results — DataProvider

_Generated: 2026-04-28 12:38_

**Dataset:** LIDC-IDRI  |  **Target:** 80 malignant + 80 benign  |  **Cases run:** 160  |  **Skipped:** 0

## Summary

| Metric | Value |
|--------|-------|
| Total cases run | 160 |
| Correct predictions | 93 |
| Wrong predictions | 67 |
| **Overall Accuracy** | **58.1%** |
| True Positives (TP) | 30 |
| True Negatives (TN) | 63 |
| False Positives (FP) | 17 |
| False Negatives (FN) | 50 |
| **Sensitivity (Recall)** | **37.5%** |
| **Specificity** | **78.8%** |
| **Precision** | **63.8%** |
| **F1 Score** | **0.472** |

## Confusion Matrix

|  | Predicted Malignant | Predicted Benign |
|--|:-------------------:|:----------------:|
| **Actual Malignant** | 30 (TP) | 50 (FN) |
| **Actual Benign**    | 17 (FP) | 63 (TN) |

## Malignant Cases (80 / 80)

| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |
|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|
| 1 | LIDC-IDRI-0035 | Malignancy | Benign | ✗ | 58.9% | 0.411 | 0.589 |
| 2 | LIDC-IDRI-0099 | Malignancy | Benign | ✗ | 93.6% | 0.064 | 0.936 |
| 3 | LIDC-IDRI-0221 | Malignancy | Malignancy | ✓ | 77.3% | 0.773 | 0.227 |
| 4 | LIDC-IDRI-0096 | Malignancy | Benign | ✗ | 52.5% | 0.475 | 0.525 |
| 5 | LIDC-IDRI-0237 | Malignancy | Benign | ✗ | 54.8% | 0.452 | 0.548 |
| 6 | LIDC-IDRI-0098 | Malignancy | Benign | ✗ | 61.5% | 0.385 | 0.615 |
| 7 | LIDC-IDRI-0203 | Malignancy | Malignancy | ✓ | 84.1% | 0.841 | 0.159 |
| 8 | LIDC-IDRI-0044 | Malignancy | Malignancy | ✓ | 50.1% | 0.501 | 0.499 |
| 9 | LIDC-IDRI-0079 | Malignancy | Malignancy | ✓ | 50.4% | 0.504 | 0.496 |
| 10 | LIDC-IDRI-0045 | Malignancy | Malignancy | ✓ | 69.8% | 0.698 | 0.302 |
| 11 | LIDC-IDRI-0154 | Malignancy | Malignancy | ✓ | 57.6% | 0.576 | 0.424 |
| 12 | LIDC-IDRI-0010 | Malignancy | Benign | ✗ | 85.9% | 0.141 | 0.859 |
| 13 | LIDC-IDRI-0284 | Malignancy | Benign | ✗ | 66.9% | 0.331 | 0.669 |
| 14 | LIDC-IDRI-0066 | Malignancy | Benign | ✗ | 92.3% | 0.077 | 0.923 |
| 15 | LIDC-IDRI-0299 | Malignancy | Benign | ✗ | 74.7% | 0.253 | 0.747 |
| 16 | LIDC-IDRI-0050 | Malignancy | Benign | ✗ | 68.6% | 0.314 | 0.686 |
| 17 | LIDC-IDRI-0234 | Malignancy | Benign | ✗ | 74.3% | 0.257 | 0.743 |
| 18 | LIDC-IDRI-0088 | Malignancy | Malignancy | ✓ | 74.5% | 0.745 | 0.255 |
| 19 | LIDC-IDRI-0119 | Malignancy | Benign | ✗ | 94.5% | 0.055 | 0.945 |
| 20 | LIDC-IDRI-0269 | Malignancy | Malignancy | ✓ | 69.1% | 0.691 | 0.309 |
| 21 | LIDC-IDRI-0108 | Malignancy | Malignancy | ✓ | 87.2% | 0.872 | 0.128 |
| 22 | LIDC-IDRI-0072 | Malignancy | Benign | ✗ | 70.4% | 0.296 | 0.704 |
| 23 | LIDC-IDRI-0084 | Malignancy | Benign | ✗ | 81.8% | 0.182 | 0.818 |
| 24 | LIDC-IDRI-0157 | Malignancy | Benign | ✗ | 90.9% | 0.091 | 0.909 |
| 25 | LIDC-IDRI-0017 | Malignancy | Malignancy | ✓ | 58.5% | 0.585 | 0.415 |
| 26 | LIDC-IDRI-0042 | Malignancy | Malignancy | ✓ | 60.8% | 0.608 | 0.392 |
| 27 | LIDC-IDRI-0270 | Malignancy | Benign | ✗ | 67.0% | 0.330 | 0.670 |
| 28 | LIDC-IDRI-0022 | Malignancy | Benign | ✗ | 79.0% | 0.210 | 0.790 |
| 29 | LIDC-IDRI-0249 | Malignancy | Malignancy | ✓ | 99.7% | 0.997 | 0.003 |
| 30 | LIDC-IDRI-0065 | Malignancy | Malignancy | ✓ | 67.7% | 0.677 | 0.323 |
| 31 | LIDC-IDRI-0152 | Malignancy | Benign | ✗ | 53.3% | 0.467 | 0.533 |
| 32 | LIDC-IDRI-0254 | Malignancy | Malignancy | ✓ | 68.2% | 0.682 | 0.318 |
| 33 | LIDC-IDRI-0245 | Malignancy | Benign | ✗ | 73.3% | 0.267 | 0.733 |
| 34 | LIDC-IDRI-0005 | Malignancy | Benign | ✗ | 68.2% | 0.318 | 0.682 |
| 35 | LIDC-IDRI-0178 | Malignancy | Benign | ✗ | 88.4% | 0.116 | 0.884 |
| 36 | LIDC-IDRI-0041 | Malignancy | Benign | ✗ | 77.0% | 0.230 | 0.770 |
| 37 | LIDC-IDRI-0273 | Malignancy | Benign | ✗ | 64.2% | 0.358 | 0.642 |
| 38 | LIDC-IDRI-0107 | Malignancy | Benign | ✗ | 69.0% | 0.310 | 0.690 |
| 39 | LIDC-IDRI-0134 | Malignancy | Malignancy | ✓ | 58.7% | 0.587 | 0.413 |
| 40 | LIDC-IDRI-0280 | Malignancy | Benign | ✗ | 87.7% | 0.123 | 0.877 |
| 41 | LIDC-IDRI-0159 | Malignancy | Benign | ✗ | 82.9% | 0.171 | 0.829 |
| 42 | LIDC-IDRI-0223 | Malignancy | Benign | ✗ | 86.1% | 0.139 | 0.861 |
| 43 | LIDC-IDRI-0135 | Malignancy | Benign | ✗ | 77.6% | 0.224 | 0.776 |
| 44 | LIDC-IDRI-0129 | Malignancy | Benign | ✗ | 69.6% | 0.304 | 0.696 |
| 45 | LIDC-IDRI-0070 | Malignancy | Benign | ✗ | 78.6% | 0.214 | 0.786 |
| 46 | LIDC-IDRI-0075 | Malignancy | Malignancy | ✓ | 71.5% | 0.715 | 0.285 |
| 47 | LIDC-IDRI-0198 | Malignancy | Malignancy | ✓ | 59.8% | 0.598 | 0.402 |
| 48 | LIDC-IDRI-0171 | Malignancy | Benign | ✗ | 64.6% | 0.354 | 0.646 |
| 49 | LIDC-IDRI-0140 | Malignancy | Benign | ✗ | 93.9% | 0.061 | 0.939 |
| 50 | LIDC-IDRI-0025 | Malignancy | Benign | ✗ | 84.9% | 0.151 | 0.849 |
| 51 | LIDC-IDRI-0053 | Malignancy | Benign | ✗ | 57.8% | 0.422 | 0.578 |
| 52 | LIDC-IDRI-0019 | Malignancy | Benign | ✗ | 83.8% | 0.162 | 0.838 |
| 53 | LIDC-IDRI-0257 | Malignancy | Malignancy | ✓ | 78.5% | 0.785 | 0.215 |
| 54 | LIDC-IDRI-0109 | Malignancy | Malignancy | ✓ | 95.9% | 0.959 | 0.041 |
| 55 | LIDC-IDRI-0182 | Malignancy | Benign | ✗ | 76.2% | 0.238 | 0.762 |
| 56 | LIDC-IDRI-0001 | Malignancy | Benign | ✗ | 54.7% | 0.453 | 0.547 |
| 57 | LIDC-IDRI-0038 | Malignancy | Benign | ✗ | 79.6% | 0.204 | 0.796 |
| 58 | LIDC-IDRI-0120 | Malignancy | Benign | ✗ | 56.0% | 0.440 | 0.560 |
| 59 | LIDC-IDRI-0086 | Malignancy | Benign | ✗ | 68.2% | 0.318 | 0.682 |
| 60 | LIDC-IDRI-0219 | Malignancy | Malignancy | ✓ | 74.8% | 0.748 | 0.252 |
| 61 | LIDC-IDRI-0117 | Malignancy | Malignancy | ✓ | 57.6% | 0.576 | 0.424 |
| 62 | LIDC-IDRI-0298 | Malignancy | Benign | ✗ | 79.5% | 0.205 | 0.795 |
| 63 | LIDC-IDRI-0289 | Malignancy | Malignancy | ✓ | 99.1% | 0.991 | 0.009 |
| 64 | LIDC-IDRI-0047 | Malignancy | Benign | ✗ | 72.1% | 0.279 | 0.721 |
| 65 | LIDC-IDRI-0281 | Malignancy | Benign | ✗ | 87.5% | 0.125 | 0.875 |
| 66 | LIDC-IDRI-0102 | Malignancy | Malignancy | ✓ | 52.4% | 0.524 | 0.476 |
| 67 | LIDC-IDRI-0064 | Malignancy | Benign | ✗ | 64.4% | 0.356 | 0.644 |
| 68 | LIDC-IDRI-0294 | Malignancy | Malignancy | ✓ | 70.0% | 0.700 | 0.300 |
| 69 | LIDC-IDRI-0081 | Malignancy | Benign | ✗ | 74.5% | 0.255 | 0.745 |
| 70 | LIDC-IDRI-0034 | Malignancy | Benign | ✗ | 53.8% | 0.462 | 0.538 |
| 71 | LIDC-IDRI-0260 | Malignancy | Malignancy | ✓ | 80.6% | 0.806 | 0.194 |
| 72 | LIDC-IDRI-0147 | Malignancy | Benign | ✗ | 55.2% | 0.448 | 0.552 |
| 73 | LIDC-IDRI-0067 | Malignancy | Malignancy | ✓ | 99.5% | 0.995 | 0.005 |
| 74 | LIDC-IDRI-0287 | Malignancy | Malignancy | ✓ | 85.7% | 0.857 | 0.143 |
| 75 | LIDC-IDRI-0097 | Malignancy | Malignancy | ✓ | 68.3% | 0.683 | 0.317 |
| 76 | LIDC-IDRI-0176 | Malignancy | Benign | ✗ | 83.6% | 0.164 | 0.836 |
| 77 | LIDC-IDRI-0276 | Malignancy | Benign | ✗ | 76.8% | 0.232 | 0.768 |
| 78 | LIDC-IDRI-0229 | Malignancy | Malignancy | ✓ | 79.5% | 0.795 | 0.205 |
| 79 | LIDC-IDRI-0112 | Malignancy | Benign | ✗ | 71.7% | 0.283 | 0.717 |
| 80 | LIDC-IDRI-0252 | Malignancy | Malignancy | ✓ | 73.3% | 0.733 | 0.267 |

## Benign Cases (80 / 80)

| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |
|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|
| 1 | LIDC-IDRI-0463 | Benign | Benign | ✓ | 92.0% | 0.080 | 0.920 |
| 2 | LIDC-IDRI-0954 | Benign | Benign | ✓ | 86.4% | 0.136 | 0.864 |
| 3 | LIDC-IDRI-1009 | Benign | Malignancy | ✗ | 50.7% | 0.507 | 0.493 |
| 4 | LIDC-IDRI-0774 | Benign | Benign | ✓ | 79.5% | 0.205 | 0.795 |
| 5 | LIDC-IDRI-0847 | Benign | Benign | ✓ | 52.8% | 0.472 | 0.528 |
| 6 | LIDC-IDRI-0644 | Benign | Benign | ✓ | 97.5% | 0.025 | 0.975 |
| 7 | LIDC-IDRI-0265 | Benign | Benign | ✓ | 75.3% | 0.247 | 0.753 |
| 8 | LIDC-IDRI-0933 | Benign | Malignancy | ✗ | 68.9% | 0.689 | 0.311 |
| 9 | LIDC-IDRI-0911 | Benign | Benign | ✓ | 69.4% | 0.306 | 0.694 |
| 10 | LIDC-IDRI-0397 | Benign | Benign | ✓ | 68.9% | 0.311 | 0.689 |
| 11 | LIDC-IDRI-0897 | Benign | Benign | ✓ | 64.7% | 0.353 | 0.647 |
| 12 | LIDC-IDRI-0625 | Benign | Benign | ✓ | 84.9% | 0.151 | 0.849 |
| 13 | LIDC-IDRI-0409 | Benign | Benign | ✓ | 77.2% | 0.228 | 0.772 |
| 14 | LIDC-IDRI-0713 | Benign | Benign | ✓ | 58.3% | 0.417 | 0.583 |
| 15 | LIDC-IDRI-0948 | Benign | Benign | ✓ | 77.9% | 0.221 | 0.779 |
| 16 | LIDC-IDRI-0316 | Benign | Benign | ✓ | 56.3% | 0.437 | 0.563 |
| 17 | LIDC-IDRI-0305 | Benign | Benign | ✓ | 74.7% | 0.253 | 0.747 |
| 18 | LIDC-IDRI-0627 | Benign | Benign | ✓ | 68.1% | 0.319 | 0.681 |
| 19 | LIDC-IDRI-0447 | Benign | Malignancy | ✗ | 98.2% | 0.982 | 0.018 |
| 20 | LIDC-IDRI-0610 | Benign | Benign | ✓ | 66.2% | 0.338 | 0.662 |
| 21 | LIDC-IDRI-0990 | Benign | Benign | ✓ | 87.3% | 0.127 | 0.873 |
| 22 | LIDC-IDRI-0643 | Benign | Malignancy | ✗ | 54.1% | 0.541 | 0.459 |
| 23 | LIDC-IDRI-0310 | Benign | Malignancy | ✗ | 63.7% | 0.637 | 0.363 |
| 24 | LIDC-IDRI-0997 | Benign | Benign | ✓ | 77.4% | 0.226 | 0.774 |
| 25 | LIDC-IDRI-0071 | Benign | Malignancy | ✗ | 65.2% | 0.652 | 0.348 |
| 26 | LIDC-IDRI-0454 | Benign | Benign | ✓ | 88.5% | 0.115 | 0.885 |
| 27 | LIDC-IDRI-0965 | Benign | Benign | ✓ | 86.3% | 0.137 | 0.863 |
| 28 | LIDC-IDRI-0791 | Benign | Malignancy | ✗ | 55.5% | 0.555 | 0.445 |
| 29 | LIDC-IDRI-0478 | Benign | Benign | ✓ | 92.9% | 0.071 | 0.929 |
| 30 | LIDC-IDRI-0665 | Benign | Benign | ✓ | 76.6% | 0.234 | 0.766 |
| 31 | LIDC-IDRI-1005 | Benign | Benign | ✓ | 77.7% | 0.223 | 0.777 |
| 32 | LIDC-IDRI-0499 | Benign | Malignancy | ✗ | 53.4% | 0.534 | 0.466 |
| 33 | LIDC-IDRI-0830 | Benign | Benign | ✓ | 82.5% | 0.175 | 0.825 |
| 34 | LIDC-IDRI-0824 | Benign | Benign | ✓ | 91.6% | 0.084 | 0.916 |
| 35 | LIDC-IDRI-0670 | Benign | Malignancy | ✗ | 60.6% | 0.606 | 0.394 |
| 36 | LIDC-IDRI-0328 | Benign | Benign | ✓ | 77.0% | 0.230 | 0.770 |
| 37 | LIDC-IDRI-0438 | Benign | Benign | ✓ | 94.6% | 0.054 | 0.946 |
| 38 | LIDC-IDRI-0763 | Benign | Benign | ✓ | 94.1% | 0.059 | 0.941 |
| 39 | LIDC-IDRI-0552 | Benign | Benign | ✓ | 65.5% | 0.345 | 0.655 |
| 40 | LIDC-IDRI-0381 | Benign | Malignancy | ✗ | 57.2% | 0.572 | 0.428 |
| 41 | LIDC-IDRI-0515 | Benign | Benign | ✓ | 87.6% | 0.124 | 0.876 |
| 42 | LIDC-IDRI-0450 | Benign | Benign | ✓ | 93.6% | 0.064 | 0.936 |
| 43 | LIDC-IDRI-0459 | Benign | Benign | ✓ | 68.1% | 0.319 | 0.681 |
| 44 | LIDC-IDRI-0327 | Benign | Benign | ✓ | 65.0% | 0.350 | 0.650 |
| 45 | LIDC-IDRI-0465 | Benign | Benign | ✓ | 88.8% | 0.112 | 0.888 |
| 46 | LIDC-IDRI-0533 | Benign | Benign | ✓ | 56.2% | 0.438 | 0.562 |
| 47 | LIDC-IDRI-0390 | Benign | Benign | ✓ | 54.1% | 0.459 | 0.541 |
| 48 | LIDC-IDRI-0819 | Benign | Benign | ✓ | 92.4% | 0.076 | 0.924 |
| 49 | LIDC-IDRI-0864 | Benign | Malignancy | ✗ | 54.4% | 0.544 | 0.456 |
| 50 | LIDC-IDRI-0825 | Benign | Benign | ✓ | 79.6% | 0.204 | 0.796 |
| 51 | LIDC-IDRI-0629 | Benign | Benign | ✓ | 96.8% | 0.032 | 0.968 |
| 52 | LIDC-IDRI-0776 | Benign | Benign | ✓ | 64.9% | 0.351 | 0.649 |
| 53 | LIDC-IDRI-0916 | Benign | Benign | ✓ | 87.0% | 0.130 | 0.870 |
| 54 | LIDC-IDRI-0734 | Benign | Benign | ✓ | 66.2% | 0.338 | 0.662 |
| 55 | LIDC-IDRI-0761 | Benign | Benign | ✓ | 79.2% | 0.208 | 0.792 |
| 56 | LIDC-IDRI-0699 | Benign | Malignancy | ✗ | 80.0% | 0.800 | 0.200 |
| 57 | LIDC-IDRI-0958 | Benign | Malignancy | ✗ | 58.2% | 0.582 | 0.418 |
| 58 | LIDC-IDRI-0969 | Benign | Benign | ✓ | 81.5% | 0.185 | 0.815 |
| 59 | LIDC-IDRI-0851 | Benign | Malignancy | ✗ | 69.1% | 0.691 | 0.309 |
| 60 | LIDC-IDRI-0571 | Benign | Benign | ✓ | 78.8% | 0.212 | 0.788 |
| 61 | LIDC-IDRI-0383 | Benign | Benign | ✓ | 51.9% | 0.481 | 0.519 |
| 62 | LIDC-IDRI-0555 | Benign | Benign | ✓ | 77.2% | 0.228 | 0.772 |
| 63 | LIDC-IDRI-0907 | Benign | Benign | ✓ | 92.9% | 0.071 | 0.929 |
| 64 | LIDC-IDRI-0837 | Benign | Benign | ✓ | 53.4% | 0.466 | 0.534 |
| 65 | LIDC-IDRI-0867 | Benign | Benign | ✓ | 96.3% | 0.037 | 0.963 |
| 66 | LIDC-IDRI-0495 | Benign | Malignancy | ✗ | 59.7% | 0.597 | 0.403 |
| 67 | LIDC-IDRI-0789 | Benign | Benign | ✓ | 91.3% | 0.087 | 0.913 |
| 68 | LIDC-IDRI-0868 | Benign | Benign | ✓ | 67.7% | 0.323 | 0.677 |
| 69 | LIDC-IDRI-0314 | Benign | Malignancy | ✗ | 58.0% | 0.580 | 0.420 |
| 70 | LIDC-IDRI-0306 | Benign | Benign | ✓ | 79.7% | 0.203 | 0.797 |
| 71 | LIDC-IDRI-0437 | Benign | Benign | ✓ | 91.0% | 0.090 | 0.910 |
| 72 | LIDC-IDRI-0794 | Benign | Benign | ✓ | 90.4% | 0.096 | 0.904 |
| 73 | LIDC-IDRI-0991 | Benign | Benign | ✓ | 97.1% | 0.029 | 0.971 |
| 74 | LIDC-IDRI-0609 | Benign | Benign | ✓ | 74.6% | 0.254 | 0.746 |
| 75 | LIDC-IDRI-0664 | Benign | Benign | ✓ | 62.3% | 0.377 | 0.623 |
| 76 | LIDC-IDRI-0344 | Benign | Benign | ✓ | 88.5% | 0.115 | 0.885 |
| 77 | LIDC-IDRI-0648 | Benign | Benign | ✓ | 69.3% | 0.307 | 0.693 |
| 78 | LIDC-IDRI-0784 | Benign | Benign | ✓ | 85.4% | 0.146 | 0.854 |
| 79 | LIDC-IDRI-0607 | Benign | Malignancy | ✗ | 60.8% | 0.608 | 0.392 |
| 80 | LIDC-IDRI-0667 | Benign | Benign | ✓ | 83.3% | 0.167 | 0.833 |

