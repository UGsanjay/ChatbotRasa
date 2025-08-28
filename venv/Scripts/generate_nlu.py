import os
import glob
import pandas as pd
from ruamel.yaml import YAML

# 1. Path ke semua CSV
csv_paths = glob.glob("*.csv")  # asumsi semua dataset CSV berada di root PI

# 2. Kumpulkan semua judul resep
examples = []
for path in csv_paths:
    df = pd.read_csv(path)
    for title in df["Title"].dropna().unique():
        # contoh format: "- Bagaimana cara memasak [<title>](recipe)?"
        examples.append(f"- Bagaimana cara memasak [{title}](recipe)?")

# 3. Siapkan struktur YAML
yaml = YAML()
nlu_data = {
    "version": "3.1",
    "nlu": [
        {
            "intent": "ask_recipe",
            "examples": "\n".join(examples)
        }
    ]
}

# 4. Tulis ke data/nlu.yml
os.makedirs("data", exist_ok=True)
with open("data/nlu.yml", "w", encoding="utf-8") as f:
    yaml.dump(nlu_data, f)

print(f"Terbitkan {len(examples)} contoh ke data/nlu.yml")
