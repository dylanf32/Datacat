from pathlib import Path
import pandas as pd


folder = Path(r"C:\Users\ferre\Desktop\College\Coding\Datacat\data\Get data")


def get_data(filename):

    extension = Path(filename).suffix.lower()

    if extension == ".csv":
        df = pd.read_csv(folder / filename)

    elif extension == ".xlsx":
        df = pd.read_excel(folder / filename)

    else:
        raise ValueError("Please enter a .csv or .xlsx file.")

    return df, filename


def processed(df, filename):
    folder = Path(r"C:\Users\ferre\Desktop\College\Coding\Datacat\data\processed_data")
    
    folder.mkdir(parents=True, exist_ok=True)
    name = f"{filename}.csv"

    df.to_csv(folder / name , index=False )

    return folder