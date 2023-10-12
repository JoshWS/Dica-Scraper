import pandas as pd
import shutil
from datetime import datetime
import pathlib


def clean_registration_numbers():

    d = pathlib.Path("data/backup")
    d.mkdir(parents=True, exist_ok=True)

    # makes backup registration numbers
    timestamp = datetime.now().strftime("%Y-%m-%d-%I%M%S")
    backup_file_name = f"{timestamp}-dica_registration_numbers"
    shutil.copyfile(
        "data/dica_registration_numbers.csv",
        f"data/backup/{backup_file_name}.csv",
    )

    # removes succeeded registration numbers
    scraped_df = pd.read_csv("data/succeeded_registration_numbers.csv")
    scraped_df["registration_number"] = scraped_df["registration_number"].astype(
        "string"
    )
    list_of_scraped_registration_numbers = scraped_df["registration_number"].tolist()

    df = pd.read_csv("data/dica_registration_numbers.csv")
    df["registration_number"] = df["registration_number"].astype("string")
    df.drop_duplicates(inplace=True)
    df = df[~df.registration_number.isin(list_of_scraped_registration_numbers)]
    df.to_csv("data/dica_registration_numbers.csv", index=False)


if __name__ == "__main__":
    clean_registration_numbers()
