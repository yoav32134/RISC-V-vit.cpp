import struct

path = "ggml-model-f32.gguf"   # really old/custom ggml, despite the name

with open(path, "rb") as f:
    magic = struct.unpack("i", f.read(4))[0]
    hidden_size = struct.unpack("i", f.read(4))[0]
    num_hidden_layers = struct.unpack("i", f.read(4))[0]
    num_attention_heads = struct.unpack("i", f.read(4))[0]
    num_classes = struct.unpack("i", f.read(4))[0]
    patch_size = struct.unpack("i", f.read(4))[0]
    img_size = struct.unpack("i", f.read(4))[0]
    ftype = struct.unpack("i", f.read(4))[0]

print("magic:", hex(magic))
print("hidden_size:", hidden_size)
print("num_hidden_layers:", num_hidden_layers)
print("num_attention_heads:", num_attention_heads)
print("num_classes:", num_classes)
print("patch_size:", patch_size)
print("img_size:", img_size)
print("ftype:", ftype)