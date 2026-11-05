from pathlib import Path
from getpass import getpass

from Datacat import ingestion, profiling, cleaning


def main():

    base_folder = Path(__file__).resolve().parent
    tables_folder = base_folder / "outputs" / "tables"
    figures_folder = base_folder / "outputs" / "figures"

    tables_folder.mkdir(parents=True, exist_ok=True)
    figures_folder.mkdir(parents=True, exist_ok=True)

    filename = input("Enter the filename (including extension): ").strip()

    df, filename = ingestion.get_data(filename)
    dataset_name = Path(filename).stem

    while True:

        print("\nDatacat")
        print("1 - Profile data")
        print("2 - Clean data")
        print("3 - Save processed data")
        print("4 - Statistical analysis")
        print("5 - Visualization")
        print("6 - MySQL")
        print("0 - Exit")

        choice = input("Choose an option: ").strip()

        try:

            if choice == "1":

                profiling.overview(df)
                profiling.missing_val_drop(df)
                profiling.duplicates(df)

            elif choice == "2":

                print("\n1 - Drop rows with missing values")
                print("2 - Fill numeric missing values with means")
                print("3 - Remove duplicates")
                print("4 - Inspect outliers")

                action = input("Choose a cleaning option: ").strip()

                if action == "1":
                    df = cleaning.missing_val_drop(df)

                elif action == "2":
                    df = cleaning.fill_missing_val(df)
                    print("Non-numeric missing values remain unchanged.")

                elif action == "3":
                    df = cleaning.duplicates(df)

                elif action == "4":
                    cleaning.outliers(df)

                else:
                    print("Invalid option.")

            elif choice == "3":

                saved_folder = ingestion.processed(df, dataset_name)
                print(f"Saved to: {saved_folder / f'{dataset_name}.csv'}")

            elif choice == "4":

                from Datacat import statistic

                print("\n1 - Summary statistics")
                print("2 - Column mean")
                print("3 - Spearman correlation")
                print("4 - One-way ANOVA")

                action = input("Choose an analysis: ").strip()
                print("Available columns:", df.columns.tolist())

                if action == "1":
                    results = statistic.describe_data(df)
                    report_name = "summary"

                elif action == "2":
                    column = input("Numeric column: ").strip()
                    statistic.mean(df, column)
                    continue

                elif action == "3":
                    results = statistic.correlation(df)
                    report_name = "correlation"

                elif action == "4":
                    x = input("Grouping column: ").strip()
                    y = input("Numeric response column: ").strip()

                    results = statistic.anova_table(df, x, y)
                    report_name = "anova"

                else:
                    print("Invalid option.")
                    continue

                if input("Save results? (y/n): ").strip().lower() == "y":
                    output_path = (
                        tables_folder / f"{dataset_name}_{report_name}.csv"
                    )
                    results.to_csv(output_path, index=True)
                    print(f"Saved to: {output_path}")

            elif choice == "5":

                from Datacat import visualization
                import matplotlib.pyplot as plt

                print("\n1 - Scatter plot")
                print("2 - Box plot")
                print("3 - Violin plot")
                print("4 - Histogram")
                print("5 - Correlation heatmap")

                action = input("Choose a plot: ").strip()
                print("Available columns:", df.columns.tolist())

                if action in ("1", "2", "3", "4"):
                    x = input("Column to plot (numeric): ").strip()

                if action == "1":
                    y = input("Second numeric column: ").strip()
                    fig = visualization.scatterplot(df, x, y)
                    plot_name = "scatter"

                elif action == "2":
                    fig = visualization.boxplot(df, x)
                    plot_name = "box"

                elif action == "3":
                    fig = visualization.violin_plot(df, x)
                    plot_name = "violin"

                elif action == "4":
                    fig = visualization.histogram_plot(df, x)
                    plot_name = "histogram"

                elif action == "5":
                    fig = visualization.heatmap_plot(df)
                    plot_name = "heatmap"

                else:
                    print("Invalid option.")
                    continue

                try:
                    if input("Save plot? (y/n): ").strip().lower() == "y":
                        output_path = (
                            figures_folder / f"{dataset_name}_{plot_name}.png"
                        )
                        fig.savefig(output_path, bbox_inches="tight")
                        print(f"Saved to: {output_path}")
                finally:
                    plt.close(fig)

            elif choice == "6":

                from Datacat import database

                username = input("MySQL username: ").strip()
                password = getpass("MySQL password: ")

                engine = database.get_engine(username, password)

                try:
                    print("\n1 - Save current data as a new table")
                    print("2 - Run a SELECT query")

                    action = input("Choose an option: ").strip()

                    if action == "1":
                        table_name = input("New table name: ").strip()
                        database.save_to_database(df, table_name, engine)
                        print(f"Saved to table: {table_name}")

                    elif action == "2":
                        query = input("Enter your SELECT query: ").strip()
                        results = database.run_query(query, engine)
                        print(results)

                        if input("Save results? (y/n): ").strip().lower() == "y":
                            output_path = (
                                tables_folder / f"{dataset_name}_query.csv"
                            )
                            results.to_csv(output_path, index=False)
                            print(f"Saved to: {output_path}")

                        if input(
                            "Use results as the current dataset? (y/n): "
                        ).strip().lower() == "y":
                            df = results

                    else:
                        print("Invalid option.")

                finally:
                    engine.dispose()

            elif choice == "0":
                break

            else:
                print("Invalid option.")

        except (ImportError, OSError, ValueError, KeyError, TypeError) as error:
            print(f"Could not complete this option: {error}")


if __name__ == "__main__":
    main()

