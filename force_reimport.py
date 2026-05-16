from utils import import_csv_to_db
import os

files_to_refresh = [
    "faqs_seguro_auto_200_linhas_revisao_humana.csv",
    "faqs_seguro_auto_200_linhas.csv",
    "faqs_seguro_saude_200_linhas.csv"
]

for f in files_to_refresh:
    path = os.path.join("data", f)
    if os.path.exists(path):
        print(f"Refreshing {f}...")
        import_csv_to_db(path, f)
    else:
        print(f"File {f} not found.")
print("Done!")
