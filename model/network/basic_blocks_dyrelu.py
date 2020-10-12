import torch.nn as nn
import torch.nn.functional as F

from .dyrelu import DyReLUA


# 基本卷积+激活函数，注意这里的激活函数采用的是 leaky_relu
class BasicConv2d(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, dy_relu=False, **kwargs):
        super(BasicConv2d, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, bias=False, **kwargs)
        if dy_relu is True:
            self.dy_relu = DyReLUA(out_channels)

    def forward(self, x):
        x = self.conv(x)
        if hasattr(self, "dy_relu"):
            return self.dy_relu(x)
        else:
            return F.leaky_relu(x, inplace=True)


class SetBlock(nn.Module):
    def __init__(self, forward_block, pooling=False):
        super(SetBlock, self).__init__()
        self.forward_block = forward_block
        self.pooling = pooling
        if pooling:
            self.pool2d = nn.MaxPool2d(2)

    def forward(self, x):
        n, s, c, h, w = x.size()
        x = self.forward_block(x.view(-1, c, h, w))
        if self.pooling:
            x = self.pool2d(x)
        _, c, h, w = x.size()
        return x.view(n, s, c, h, w)
