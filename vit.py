
import torch
import torch.nn as nn
from torch.utils import data
from PIL import Image
from torchvision.models.detection import transform


class PatchEmbed(nn.Module):
    def __init__(self):
        super().__init__()
        self.proj = nn.Conv2d(3, 192, kernel_size=16, stride=16)
        self.norm = nn.Identity()

    def forward(self, x):
        x = self.proj(x)
        x = x.flatten(2).transpose(1, 2)
        x = self.norm(x)
        return x


class Attention(nn.Module):
    def __init__(self):
        super().__init__()
        self.qkv = nn.Linear(192, 576, bias=True)
        self.q_norm = nn.Identity()
        self.k_norm = nn.Identity()
        self.attn_drop = nn.Dropout(0.0)
        self.norm = nn.Identity()
        self.proj = nn.Linear(192, 192, bias=True)
        self.proj_drop = nn.Dropout(0.0)

        self.num_heads = 3
        self.head_dim = 192 // 3
        self.scale = self.head_dim ** -0.5

    def forward(self, x):
        B, N, C = x.shape

        qkv = self.qkv(x)
        qkv = qkv.reshape(B, N, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]

        q = self.q_norm(q)
        k = self.k_norm(k)

        attn = (q * self.scale) @ k.transpose(-2, -1)
        attn = attn.softmax(dim=-1)
        attn = self.attn_drop(attn)

        x = attn @ v
        x = x.transpose(1, 2).reshape(B, N, C)
        x = self.norm(x)
        x = self.proj(x)
        x = self.proj_drop(x)
        return x


class Mlp(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(192, 768, bias=True)
        self.act = nn.GELU(approximate='none')
        self.drop1 = nn.Dropout(0.0)
        self.norm = nn.Identity()
        self.fc2 = nn.Linear(768, 192, bias=True)
        self.drop2 = nn.Dropout(0.0)

    def forward(self, x):
        x = self.fc1(x)
        x = self.act(x)
        x = self.drop1(x)
        x = self.norm(x)
        x = self.fc2(x)
        x = self.drop2(x)
        return x


class Block(nn.Module):
    def __init__(self):
        super().__init__()
        self.norm1 = nn.LayerNorm(192, eps=1e-6, elementwise_affine=True)
        self.attn = Attention()
        self.ls1 = nn.Identity()
        self.drop_path1 = nn.Identity()

        self.norm2 = nn.LayerNorm(192, eps=1e-6, elementwise_affine=True)
        self.mlp = Mlp()
        self.ls2 = nn.Identity()
        self.drop_path2 = nn.Identity()

    def forward(self, x):
        x = x + self.drop_path1(self.ls1(self.attn(self.norm1(x))))
        x = x + self.drop_path2(self.ls2(self.mlp(self.norm2(x))))
        return x


class ViT(nn.Module):
    def __init__(self):
        super().__init__()

        self.patch_embed = PatchEmbed()

        self.cls_token = nn.Parameter(torch.zeros(1, 1, 192))
        self.pos_embed = nn.Parameter(torch.zeros(1, 577, 192))

        self.pos_drop = nn.Dropout(0.0)
        self.patch_drop = nn.Identity()
        self.norm_pre = nn.Identity()

        self.blocks = nn.Sequential(
            Block(), Block(), Block(), Block(),
            Block(), Block(), Block(), Block(),
            Block(), Block(), Block(), Block()
        )

        self.norm = nn.LayerNorm(192, eps=1e-6, elementwise_affine=True)
        self.fc_norm = nn.Identity()
        self.head_drop = nn.Dropout(0.0)
        self.head = nn.Linear(192, 1000, bias=True)

    def forward_features(self, x):
        x = self.patch_embed(x)

        B = x.shape[0]
        cls_token = self.cls_token.expand(B, -1, -1)
        x = torch.cat((cls_token, x), dim=1)

        x = x + self.pos_embed
        x = self.pos_drop(x)
        x = self.patch_drop(x)
        x = self.norm_pre(x)

        x = self.blocks(x)
        x = self.norm(x)

        x = x[:, 0]
        x = self.fc_norm(x)
        return x

    def forward(self, x):
        x = self.forward_features(x)
        x = self.head_drop(x)
        x = self.head(x)
        return x

class ImageDataset(data.Dataset):
    def __init__(self,paths,y,transform = None):
        self.paths = paths
        self.Y = y
        self.transform = transform
    def __len__(self):
        return len(self.paths)
    def __getitem__(self, index):
        x = Image.open(self.paths[index]).convert("RGB")
        if self.transform is not None:
            x = self.transform(x)
        return x,self.Y[index]