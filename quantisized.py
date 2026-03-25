import torch
from torch import nn
from torch.nn import functional


def quantisize_mat_q4_0(mat):
    shape = mat.shape
    mat = mat.flatten()
    if len(mat) % 32 != 0:
        raise ValueError("mat must be div by 32")
    blocked = mat.view(-1, 32)
    idx = torch.argmax(blocked.abs(), dim=1)
    d = (blocked[range(blocked.shape[0]), idx] / -8).unsqueeze(dim=1)
    q = torch.clamp(torch.trunc(blocked / d + 8.5), 0, 15)
    return ((q - 8) * d).reshape(shape)


class q4_0_Linear(nn.Linear):
    def forward(self, x):
        w = quantisize_mat_q4_0(self.weight)
        return functional.linear(x, w, self.bias)


class q4_0_Conv2d(nn.Conv2d):
    def forward(self, x):
        w = quantisize_mat_q4_0(self.weight)
        return functional.conv2d(x, w, self.bias, self.stride, self.padding, self.dilation, self.groups)


def replace_with_q4_0(module: nn.Module) -> nn.Module:
    """
    Recursively replace nn.Linear and nn.Conv2d in a model with
    q4_0_Linear and q4_0_Conv2d, preserving parameters.
    """
    for name, child in list(module.named_children()):
        replace_with_q4_0(child)

        if isinstance(child, nn.Linear):
            new_layer = q4_0_Linear(
                in_features=child.in_features,
                out_features=child.out_features,
                bias=(child.bias is not None),
                device=child.weight.device,
                dtype=child.weight.dtype,
            )
            new_layer.weight = nn.Parameter(child.weight.detach().clone())
            if child.bias is not None:
                new_layer.bias = nn.Parameter(child.bias.detach().clone())
            new_layer.train(child.training)
            setattr(module, name, new_layer)

        elif isinstance(child, nn.Conv2d):
            new_layer = q4_0_Conv2d(
                in_channels=child.in_channels,
                out_channels=child.out_channels,
                kernel_size=child.kernel_size,
                stride=child.stride,
                padding=child.padding,
                dilation=child.dilation,
                groups=child.groups,
                bias=(child.bias is not None),
                padding_mode=child.padding_mode,
                device=child.weight.device,
                dtype=child.weight.dtype,
            )
            new_layer.weight = nn.Parameter(child.weight.detach().clone())
            if child.bias is not None:
                new_layer.bias = nn.Parameter(child.bias.detach().clone())
            new_layer.train(child.training)
            setattr(module, name, new_layer)

    return module


if __name__ == "__main__":
    mat = torch.randint(0, 100, (64, 64, 32))
    print(mat[0][0])
    print(quantisize_mat_q4_0(mat)[0][0])
