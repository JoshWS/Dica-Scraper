import os.path
import csv
import pandas as pd

# checks if folders exist
def folder_checker(folder_name):
    if os.path.exists(f"data/{folder_name}"):
        pass
    else:
        path = os.path.join("data/", folder_name)
        os.mkdir(path)


# creates csv files
def csv_maker(path, address_name, field_names):
    with open(
        f"{path}{address_name}.csv",
        mode="w",
        newline="",
        encoding="utf8",
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()


# checks if files exist
def file_exists_checker(path, file_name, field_names):
    if os.path.isfile(f"{path}{file_name}.csv"):
        pass
    else:
        csv_maker(path, file_name, field_names)


def dedupe_succeeded_registration_numbers():
    df = pd.read_csv("data/succeeded_registration_numbers.csv")
    df.drop_duplicates(inplace=True)
    df.to_csv("data/succeeded_registration_numbers.csv", index=False)


def dedupe_output_files():
    output_files = [
        "addresses.csv",
        "companies.csv",
        "filing_history.csv",
        "officers.csv",
    ]
    for output_file in output_files:
        df = pd.read_csv(f"data/output/{output_file}")
        df.drop_duplicates(inplace=True)
        df.to_csv(f"data/output/{output_file}", index=False)
