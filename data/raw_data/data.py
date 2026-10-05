from pathlib import Path
import pandas as pd


folder = Path(r"C:\Users\ferre\Desktop\College\Coding\Datacat\data\Get data")


def get_data(filename):

    extension = Path(filename).suffix.lower()

    if extension == ".csv":
        data = pd.read_csv(folder / filename)

    elif extension == ".xlsx":
        data = pd.read_excel(folder / filename)

    else:
        raise ValueError("Please enter a .csv or .xlsx file.")


