import csv
import argparse

parser = argparse.ArgumentParser(
    description="Convert PyTorch weights of a Vision Transformer to the ggml file format."
)
parser.add_argument(
    "--mapping file",
    type=str,
    default="synset_words.txt",
    help="path to mapping file(it is synset_words.txt in kaggle imagenet 1k)",
)
parser.add_argument(
    "--val_csv_file",
    type=str,
    default="LOC_val_solution.csv",
    help="path to val_csv file(it is LOC_val_solution.csv in kaggle imagenet 1k)",
)
parser.add_argument(
    "--output_file",
    type=str,
    default="val_labels.txt",
    help="path to output file",
)

mapping_file = "synset_words.txt"
val_csv_file = "LOC_val_solution.csv"
output_file = "val_labels.txt"

with open(mapping_file) as f:
    synset_to_idx = {
        line.split()[0]: i
        for i, line in enumerate(f)
        if line.strip()
    }

with open(val_csv_file) as f:
    rows = sorted(csv.DictReader(f), key=lambda row: row["ImageId"])

labels = [
    str(synset_to_idx[row["PredictionString"].split()[0]])
    for row in rows
]

with open(output_file, "w") as f:
    f.write("\n".join(labels))
print(synset_to_idx)