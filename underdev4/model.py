import torch
import torch.nn as nn
import torch.nn.functional as F


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super().__init__()
        self.conv1 = nn.Conv3d(inplanes, planes, 3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm3d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv3d(planes, planes, 3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm3d(planes)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        if self.downsample is not None:
            residual = self.downsample(x)
        return F.relu(out + residual)


class ResNet3D(nn.Module):
    """ResNet-18 3D matching Tencent MedicalNet resnet_18.pth (shortcut_type='A')."""

    def __init__(self, dropout=0.5):
        super().__init__()
        self.inplanes = 64
        self.conv1 = nn.Conv3d(1, 64, 7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm3d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool3d(3, stride=2, padding=1)
        self.layer1 = self._make_layer(64,  2)
        self.layer2 = self._make_layer(128, 2, stride=2)
        self.layer3 = self._make_layer(256, 2, stride=2)
        self.layer4 = self._make_layer(512, 2, stride=2)
        self.avgpool = nn.AdaptiveAvgPool3d(1)
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(512, 2),
        )

    def _make_layer(self, planes, blocks, stride=1):
        # shortcut_type='A': matches MedicalNet default — avg_pool3d + zero-cat,
        # no learned projection weights, so no downsample keys in the checkpoint.
        downsample = None
        if stride != 1 or self.inplanes != planes * BasicBlock.expansion:
            in_ch  = self.inplanes
            out_ch = planes * BasicBlock.expansion
            s      = stride
            def downsample(x, _in=in_ch, _out=out_ch, _s=s):
                out = F.avg_pool3d(x, kernel_size=1, stride=_s)
                zeros = torch.zeros(
                    out.size(0), _out - _in, out.size(2), out.size(3), out.size(4),
                    device=out.device, dtype=out.dtype,
                )
                return torch.cat([out, zeros], dim=1)

        layers = [BasicBlock(self.inplanes, planes, stride, downsample)]
        self.inplanes = planes * BasicBlock.expansion
        for _ in range(1, blocks):
            layers.append(BasicBlock(self.inplanes, planes))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.maxpool(self.relu(self.bn1(self.conv1(x))))
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avgpool(x)
        x = x.flatten(1)
        return self.classifier(x)
