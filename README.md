# Datacat

Datacat is a Python command-line project for exploring tabular data. Load a CSV or Excel file, inspect its quality, clean it, run statistical summaries, and create plots from one interactive menu. Optional MySQL support lets you save the current dataset as a new table and load query results for further analysis.

## Features

- **Ingestion:** read `.csv` and `.xlsx` files and export processed data as CSV.
- **Profiling:** show column types, dataset dimensions, the first five rows, missing-value counts, and duplicate-row counts.
- **Cleaning:** drop rows with missing values, fill numeric missing values with column means, remove duplicates, or print potential outliers with absolute population z-scores greater than 3.
- **Statistics:** descriptive summaries, a column mean, numeric Spearman correlations, and one-way ANOVA using a categorical grouping column.
- **Visualization:** scatter, box, violin, and histogram plots, plus a numeric Pearson correlation heatmap.
- **MySQL:** save a new table, display query results, optionally export them, and optionally use them as the current dataset.

## Setup

Install Python with virtual-environment support, then run these commands from the repository root:

```powershell
git clone https://github.com/dylanf32/Datacat.git
cd Datacat
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux, activate the environment with `source .venv/bin/activate` instead. Dependencies are not version-pinned; the repository does not currently specify a tested Python version or automated test suite.

### Configure the data folders

Before running the app, edit the two folder paths in [Datacat/ingestion.py](Datacat/ingestion.py). They currently point to the author's local Windows directory. For a portable checkout, use these expressions:

```python
# Module-level input folder:
folder = Path(__file__).resolve().parents[1] / "data" / "get_data"

# Output folder inside processed():
folder = Path(__file__).resolve().parents[1] / "data" / "processed_data"
```

Place input files in `data/get_data/`. The repository includes `Order_delivery.csv` as an example. The files in `config/` are placeholders and do not configure the application.

## Usage

```powershell
python main.py
```

Enter a filename including its extension, such as `Order_delivery.csv`, then select an option:

| Option | Action |
| --- | --- |
| 1 | Profile the current dataset |
| 2 | Clean data or inspect outliers |
| 3 | Save processed data |
| 4 | Run statistical analysis |
| 5 | Create a plot |
| 6 | Connect to MySQL |
| 0 | Exit |

Cleaning updates the dataset held in memory. Choose option 3 to write it to disk. Outlier inspection only prints flagged values; it does not remove rows. Mean filling leaves non-numeric missing values unchanged, and an entirely missing numeric column remains missing.

For an example workflow, load `Order_delivery.csv`, profile it, remove duplicates if needed, then use `Delivery_Duration_Minutes` for a histogram or `City` and `Delivery_Duration_Minutes` for one-way ANOVA. ANOVA results require appropriate assumptions and interpretation; the application does not check those assumptions automatically.

Plot windows open before the save prompt. Close the plot window to return to the menu and choose whether to save it.

### Saved files

| Output | Location |
| --- | --- |
| Processed dataset | Configured processed-data folder, as `<dataset>.csv` |
| Summary, correlation, or ANOVA table | `outputs/tables/<dataset>_<analysis>.csv` |
| Query results | `outputs/tables/<dataset>_query.csv` |
| Plot | `outputs/figures/<dataset>_<plot>.png` |

The app creates the output directories automatically. Repeating a save with the same dataset and output type overwrites the previous file. A column mean is printed only; it has no export prompt. Using SQL results as the current dataset keeps the original dataset name for subsequent exports.

## Optional MySQL setup

The database module connects to `localhost:3306` and expects an existing database named `datacat`. Install and start MySQL separately, then create the database using an account with the required privileges:

```sql
CREATE DATABASE IF NOT EXISTS datacat;
```

Select option 6 and enter your MySQL username and password. The password prompt hides input. Host, port, and database name are configured directly in [Datacat/database.py](Datacat/database.py).

Saving uses `if_exists="fail"`, so an existing table is not replaced. To read a table you created, choose the query option and enter, for example:

```sql
SELECT * FROM orders LIMIT 10;
```

The menu asks for a SELECT query, but the module passes the supplied SQL to SQLAlchemy without enforcing read-only statements. Use a database account with permissions appropriate to your work. Database connection and SQL errors may terminate the app because the menu does not catch all database exceptions.

## Repository layout

```text
Datacat/                 Reusable ingestion, profiling, cleaning, statistics,
                         visualization, and database modules
main.py                  Interactive menu and dataset state
data/get_data/           Input data and the example CSV
data/processed_data/     Intended processed-data directory
notebooks/               Exploratory notebooks; 02_profiling contains cells,
                         while the other notebooks are placeholders
config/                  Configuration placeholders
database/                SQL project and connection placeholder
Schema.png, schema_vs.png  Project diagrams
```

The `.sqlproj` file targets SQL Server tooling; it is not a MySQL initialization script and is not used by `main.py`. Statistical and plotting dependencies are imported when their menu options are selected, as are the database dependencies. The application reads Excel's default first sheet and does not offer sheet selection or automatic date parsing for CSV files.
