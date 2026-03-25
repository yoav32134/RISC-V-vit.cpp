import time
import math
import timm
import torch
import torch.nn as nn
from torch.utils import data
from torchmetrics.classification import MulticlassAccuracy
from torchvision import datasets
from torchvision import transforms

from quantisized import replace_with_q4_0
from vit import ImageDataset
from torch.utils.tensorboard import SummaryWriter
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert PyTorch weights of a Vision Transformer to the ggml file format."
    )
    parser.add_argument(
        "--dataset_path",
        type=str,
        default="./",
        help="path to imagenet1k dataset(I used the one from kaggle)",
    )
    parser.add_argument(
        "--val_labels",
        type=str,
        default="val_labels.txt",
        help="path to validation answers",
    )
    parser.add_argument(
        "--timm_model",
        type=str,
        default="vit_tiny_patch16_384.augreg_in21k_ft_in1k",
        help="timm ViT model to use for training",
    )
    args = parser.parse_args()

    SEED = 42
    torch.manual_seed(SEED)
    torch.cuda.manual_seed(SEED)

    writer = SummaryWriter("runs/QAT1")
    torch.set_float32_matmul_precision("high")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    amp_dtype = torch.bfloat16
    scaler = torch.amp.GradScaler(device)
    print(f"running on {device}")
    model = timm.create_model(
        args.timm_model,
        pretrained=True
    )

    with open(args.val_labels) as f:
        y = f.readlines()
    y = [int(b[:-1]) for b in y]
    y = torch.tensor(y)
    paths = [
        fr"{args.dataset_path}\val\ILSVRC2012_val_{i:08}.JPEG"
        for i in range(1, 50 * 1000 + 1)]
    test_transform = transforms.Compose(
        [transforms.Resize((384, 384)), transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(
            384,
            scale=(0.05, 1.0),
            ratio=(0.75, 1.3333333333333333),
            interpolation=transforms.InterpolationMode.BICUBIC
        ),
        transforms.RandomHorizontalFlip(0.5),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])
    full = datasets.ImageFolder(
        root=fr"{args.dataset_path}\train",
        transform=test_transform)

    test_dataset = ImageDataset(paths, y, transform=test_transform)
    train_dataset = datasets.ImageFolder(
        root=fr"{args.dataset_path}\train",
        transform=train_transform)

    train_dataloader = data.DataLoader(train_dataset, batch_size=256, shuffle=True, num_workers=4)
    test_dataloader = data.DataLoader(test_dataset, batch_size=256, shuffle=False, num_workers=4)

    replace_with_q4_0(model)
    model = model.to(device)
    decay = []
    no_decay = []

    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        if param.ndim == 1 or name.endswith(".bias") or "norm" in name.lower():
            no_decay.append(param)
        else:
            decay.append(param)

    optimizer = torch.optim.AdamW(
        [
            {"params":decay,"weight_decay":0.05},
            {"params": no_decay, "weight_decay": 0}
        ],
        lr=1e-4,
    )
    loss_func = nn.CrossEntropyLoss(reduction="mean")
    accuracy1 = MulticlassAccuracy(num_classes=1000, top_k=1).to(device)
    accuracy5 = MulticlassAccuracy(num_classes=1000, top_k=5).to(device)

    epochs = 5
    total_steps = epochs * len(train_dataloader)
    warmup_steps = total_steps // 10
    def lr_lambda(step):
        if step < warmup_steps:
            return float(step + 1) / float(warmup_steps)
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return 0.5 * (1.0 + math.cos(math.pi * progress))
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
    count = 0
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for x, y in train_dataloader:
            start_time = time.time()
            x = x.to(device, non_blocking=True)
            y = y.to(device, non_blocking=True)
            with torch.autocast(device,amp_dtype):
                predictions = model(x)
                loss = loss_func(predictions, y)
            train_loss += loss * y.size(0)
            count += 1
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            writer.add_scalar("train/loss_step", loss.item(), count)
            writer.add_scalar("train/lr", optimizer.param_groups[0]["lr"], count)
            scheduler.step()
        model.eval()
        with torch.inference_mode():
            accuracy1.reset()
            accuracy5.reset()
            test_loss = 0
            for image, label in test_dataloader:
                start_time = time.time()
                image = image.to(device)
                label = label.to(device)
                with torch.autocast(device, amp_dtype):
                    predictions = model(image)
                    loss = loss_func(predictions, label)
                test_loss += loss.item() * y.size(0)
                accuracy1.update(predictions, label)
                accuracy5.update(predictions, label)
            test_acc1 = accuracy1.compute().item()
            test_acc5 = accuracy5.compute().item()
            writer.add_scalar("test/accuracy@1", test_acc1, epoch)
            writer.add_scalar("test/accuracy@5", test_acc5, epoch)
            writer.add_scalar("test/loss", test_loss / len(test_dataset), epoch)
            writer.add_scalar("train/loss_epoch", train_loss / len(train_dataset), epoch)
            writer.flush()

        # print(f"epoch {epoch} | train loss {train_loss / (len(train_dataset) / 256)} | test loss "
        #       f"{test_loss / (len(test_dataset) / 256)} | test accuracy1 {test_acc1} | test accuracy5 {test_acc5}")
        torch.save(model.state_dict(), f"./ViTQAT{epoch}.pth")
    writer.flush()
    writer.close()