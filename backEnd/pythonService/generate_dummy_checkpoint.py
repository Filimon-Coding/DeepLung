"""
generate_dummy_checkpoint.py
-----------------------------
Run this script once from your project root (where model.py lives):

    python generate_dummy_checkpoint.py

It will create:  checkpoints/resnet3d_latest.pth

The weights are randomly initialised but the architecture is 100% compatible
with ResNetShort, so load_model() in infer.py will load it without errors and
the full Grad-CAM pipeline will run end-to-end.
"""

import os
import torch
import torch.nn as nn


# ── Exact copy of ResNetShort from model.py ──────────────────────────────────

class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, mid_channels=None, stride=1):
        super().__init__()
        if mid_channels is None:
            mid_channels = out_channels // 2

        self.conv = nn.Sequential(
            nn.Conv3d(in_channels, mid_channels, kernel_size=1, stride=1),
            nn.BatchNorm3d(mid_channels),
            nn.ReLU(),
            nn.Conv3d(mid_channels, mid_channels, kernel_size=3, stride=stride, padding=1),
            nn.BatchNorm3d(mid_channels),
            nn.ReLU(),
            nn.Conv3d(mid_channels, out_channels, kernel_size=1, stride=1),
            nn.BatchNorm3d(out_channels)
        )

        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv3d(in_channels, out_channels, kernel_size=1, stride=stride),
                nn.BatchNorm3d(out_channels)
            )

    def forward(self, x):
        return torch.relu(self.conv(x) + self.shortcut(x))


class ResNetShort(nn.Module):
    def __init__(self):
        super().__init__()
        self.prep = nn.Sequential(
            nn.Conv3d(1, 32, 3, padding=1),
            nn.BatchNorm3d(32),
            nn.ReLU()
        )
        self.layer1 = ResidualBlock(32,  64,  stride=2)
        self.layer2 = ResidualBlock(64,  128, stride=2)
        self.layer3 = ResidualBlock(128, 256, stride=2)

        self.avgpool    = nn.AdaptiveAvgPool3d(1)
        self.dropout    = nn.Dropout3d(p=0.3)
        self.classifier = nn.Linear(256, 2)

    def forward(self, x):
        x = self.prep(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.avgpool(x)
        x = self.dropout(x)
        x = x.flatten(1)
        return self.classifier(x)


# ── Generate & save ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    torch.manual_seed(42)          # reproducible random weights

    model = ResNetShort()
    model.eval()

    os.makedirs("checkpoints", exist_ok=True)
    out_path = os.path.join("checkpoints", "resnet3d_latest.pth")

    torch.save({"model_state_dict": model.state_dict()}, out_path)

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"✅  Saved dummy checkpoint → {out_path}  ({size_mb:.1f} MB)")
    print("    Architecture : ResNetShort  (prep → layer1 → layer2 → layer3 → classifier)")
    print("    Classes      : [Benign, Malignancy]")
    print("    Weights      : random (seed=42) — pipeline-compatible, not trained")
    print()
    print("You can now start your FastAPI server normally:")
    print("    uvicorn app:app --reload")
