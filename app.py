from hashlib import sha256
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from Datacat import cleaning, profiling, statistic, visualization


# --------------------------------------------------
# Page settings
# --------------------------------------------------
st.set_page_config(
    page_title="Datacat",
    page_icon=":material/analytics:",
    layout="wide",
)


# --------------------------------------------------
# Sidebar: upload and navigation
# --------------------------------------------------
with st.sidebar:
    st.title("Datacat")
    st.caption("Explore, clean, and understand your data.")

    uploaded_file = st.file_uploader(
        "Upload a dataset",
        type=["csv", "xlsx"],
        help="Upload a CSV or an Excel workbook. Excel uses the first sheet.",
    )

    st.divider()

    section = st.radio(
        "Workspace",
        [
            "Overview",
            "Clean data",
            "Statistical analysis",
            "Visualization",
            "Export",
        ],
        key="workspace",
    )


# --------------------------------------------------
# Load the file and preserve the working dataset
# --------------------------------------------------
if uploaded_file is None:
    st.title("Understand your data")
    st.write(
        "Upload a dataset using the sidebar, then explore its quality, "
        "clean missing values, run statistics, and create plots."
    )
    st.info("Choose a CSV or Excel file to get started.")
    st.stop()

file_bytes = uploaded_file.getvalue()
file_key = (uploaded_file.name, sha256(file_bytes).hexdigest())

if st.session_state.get("file_key") != file_key:
    try:
        if uploaded_file.name.lower().endswith(".xlsx"):
            original_df = pd.read_excel(BytesIO(file_bytes))
        else:
            original_df = pd.read_csv(BytesIO(file_bytes))

    except (ValueError, OSError, ImportError, UnicodeError) as error:
        st.error(f"Could not read this file: {error}")
        st.stop()

    st.session_state.file_key = file_key
    st.session_state.original_df = original_df.copy()
    st.session_state.working_df = original_df.copy()
    st.session_state.pop("cleaning_message", None)

with st.sidebar:
    st.divider()
    st.caption(f"Current file: {uploaded_file.name}")

    if st.button(
        "Reset to original data",
        icon=":material/restart_alt:",
        width="stretch",
    ):
        st.session_state.working_df = (
            st.session_state.original_df.copy()
        )
        st.session_state.pop("cleaning_message", None)

df = st.session_state.working_df
dataset_name = Path(uploaded_file.name).stem
numeric_columns = df.select_dtypes(include="number").columns.tolist()


# --------------------------------------------------
# Dataset header
# --------------------------------------------------
st.title(section)
st.caption(f"Dataset: {uploaded_file.name}")

rows, columns, missing, duplicates = st.columns(4)

rows.metric("Rows", f"{len(df):,}")
columns.metric("Columns", f"{len(df.columns):,}")
missing.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")
duplicates.metric("Duplicate rows", f"{int(df.duplicated().sum()):,}")

st.divider()

if df.empty:
    st.warning(
        "The working dataset is empty. You can export it or reset "
        "to the original data using the sidebar."
    )


# --------------------------------------------------
# Overview
# --------------------------------------------------
if section == "Overview":
    st.subheader("Data preview")
    st.dataframe(df.head(20), alt="First twenty dataset rows")
    st.caption("Showing up to 20 rows of the current working dataset.")

    st.subheader("Column profile")

    missing_counts = profiling.missing_val_drop(df)

    column_profile = pd.DataFrame(
        {
            "Data type": df.dtypes.astype(str),
            "Non-missing values": df.notna().sum(),
            "Missing values": missing_counts,
            "Missing (%)": (
                missing_counts / len(df) * 100
                if len(df)
                else float("nan")
            ),
            "Distinct values": df.nunique(),
        }
    )

    column_profile.index.name = "Column"

    st.dataframe(
        column_profile,
        alt="Column types, missing values, and distinct-value counts",
    )


# --------------------------------------------------
# Cleaning
# --------------------------------------------------
elif section == "Clean data":
    st.subheader("Prepare your dataset")
    st.caption(
        "Changes apply to your working dataset. "
        "Use the sidebar to restore the original."
    )

    choices = st.radio(
        "Cleaning operation",
        [
            "Drop rows with missing values",
            "Fill numeric missing values with mean",
            "Remove duplicates",
        ],
    )

    if choices == "Drop rows with missing values":
        st.info("Removes any row containing at least one missing value.")

    elif choices == "Fill numeric missing values with mean":
        st.info(
            "Fills numeric gaps using each column's mean. "
            "Non-numeric gaps and entirely missing columns remain missing."
        )

    else:
        st.info("Keeps the first occurrence of each duplicate row.")

    if st.button(
        "Apply cleaning",
        type="primary",
        icon=":material/cleaning_services:",
    ):
        rows_before = len(df)
        missing_before = int(df.isna().sum().sum())

        if choices == "Drop rows with missing values":
            cleaned_df = cleaning.missing_val_drop(df.copy())

        elif choices == "Fill numeric missing values with mean":
            cleaned_df = cleaning.fill_missing_val(df.copy())

        else:
            cleaned_df = cleaning.duplicates(df.copy())

        rows_removed = rows_before - len(cleaned_df)
        cells_filled = (
            missing_before - int(cleaned_df.isna().sum().sum())
        )

        st.session_state.working_df = cleaned_df
        st.session_state.cleaning_message = (
            f"Applied: {choices}. "
            f"Rows removed: {rows_removed:,}. "
            f"Missing cells filled: "
            f"{cells_filled if rows_removed == 0 else 0:,}."
        )

        st.rerun()

    if st.session_state.get("cleaning_message"):
        st.success(st.session_state.cleaning_message)

    st.subheader("Working data")
    st.dataframe(df, alt="Current dataset after cleaning")


# --------------------------------------------------
# Statistics
# --------------------------------------------------
elif section == "Statistical analysis":
    action = st.selectbox(
        "Analysis",
        [
            "Summary statistics",
            "Column mean",
            "Spearman correlation",
            "One-way ANOVA",
        ],
    )

    results = None
    report_name = ""

    try:
        if df.empty:
            st.info("This analysis needs a non-empty dataset.")

        elif action == "Summary statistics":
            results = statistic.describe_data(df)
            report_name = "summary"

        elif not numeric_columns:
            st.info("This analysis needs at least one numeric column.")

        elif action == "Column mean":
            column = st.selectbox("Numeric column", numeric_columns)

            results = pd.DataFrame(
                {
                    "Column": [column],
                    "Mean": [statistic.mean(df, column)],
                    "Valid observations": [df[column].count()],
                }
            )
            report_name = "mean"

        elif action == "Spearman correlation":
            if len(numeric_columns) < 2:
                st.info("Select a dataset with at least two numeric columns.")
            else:
                results = df.corr(
                    method="spearman",
                    numeric_only=True,
                )
                report_name = "spearman"
                st.caption(
                    "Measures monotonic association. "
                    "Correlation does not establish causation."
                )

        elif action == "One-way ANOVA":
            response = st.selectbox(
                "Numeric response",
                numeric_columns,
            )

            grouping_columns = [
                column for column in df.columns
                if column != response
            ]

            if not grouping_columns:
                st.info("ANOVA also needs a grouping column.")

            else:
                group = st.selectbox(
                    "Grouping column",
                    grouping_columns,
                    help="Choose a column identifying meaningful groups.",
                )

                st.caption(
                    "ANOVA compares group means. Check independence, "
                    "residual normality, and similar group variances."
                )

                if st.button("Run ANOVA", type="primary"):
                    analysis_df = df[[group, response]].dropna()
                    group_count = analysis_df[group].nunique()

                    if group_count < 2:
                        st.warning(
                            "At least two groups with valid observations "
                            "are required."
                        )

                    elif len(analysis_df) <= group_count:
                        st.warning(
                            "More observations than groups are needed "
                            "to estimate residual variation."
                        )

                    else:
                        results = statistic.anova_table(
                            analysis_df,
                            group,
                            response,
                        )
                        report_name = "anova"

        if results is not None:
            st.subheader("Results")
            st.dataframe(results, alt=f"{action} results")

            st.download_button(
                "Download results",
                data=results.to_csv(index=True).encode("utf-8"),
                file_name=f"{dataset_name}_{report_name}.csv",
                mime="text/csv",
                icon=":material/download:",
                on_click="ignore",
            )

    except (ValueError, TypeError, KeyError, ZeroDivisionError) as error:
        st.error(f"Could not complete analysis: {error}")


# --------------------------------------------------
# Visualization
# --------------------------------------------------
elif section == "Visualization":
    action = st.selectbox(
        "Plot type",
        [
            "Histogram",
            "Box plot",
            "Violin plot",
            "Scatter plot",
            "Correlation heatmap",
        ],
    )

    if df.empty or not numeric_columns:
        st.info("Plots need a non-empty dataset with numeric columns.")

    else:
        if action != "Correlation heatmap":
            x = st.selectbox(
                "Numeric column",
                numeric_columns,
                key="plot_x",
            )

        if action == "Scatter plot":
            y = st.selectbox(
                "Second numeric column",
                numeric_columns,
                index=min(1, len(numeric_columns) - 1),
                key="plot_y",
            )

        fig = None

        try:
            if action == "Histogram":
                fig = visualization.histogram_plot(df, x, show=False)

            elif action == "Box plot":
                fig = visualization.boxplot(df, x, show=False)

            elif action == "Violin plot":
                fig = visualization.violin_plot(df, x, show=False)

            elif action == "Scatter plot":
                fig = visualization.scatterplot(df, x, y, show=False)

            else:
                st.caption("This heatmap uses Pearson correlation.")
                fig = visualization.heatmap_plot(df, show=False)

            st.pyplot(
                fig,
                alt=f"{action} for the selected dataset columns",
            )

            image = BytesIO()
            fig.savefig(image, format="png", bbox_inches="tight")

            plot_name = action.lower().replace(" ", "_")

            st.download_button(
                "Download PNG",
                data=image.getvalue(),
                file_name=f"{dataset_name}_{plot_name}.png",
                mime="image/png",
                icon=":material/download:",
                on_click="ignore",
            )

        except (ValueError, TypeError, KeyError) as error:
            st.error(f"Could not create plot: {error}")

        finally:
            if fig is not None:
                plt.close(fig)


# --------------------------------------------------
# Export
# --------------------------------------------------
elif section == "Export":
    st.subheader("Download your working dataset")
    st.write(
        "The download includes all cleaning changes applied "
        "during this session."
    )

    st.download_button(
        "Download processed CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"{dataset_name}_processed.csv",
        mime="text/csv",
        icon=":material/download:",
        type="primary",
        on_click="ignore",
    )

    with st.expander("Preview exported data"):
        st.dataframe(df, alt="Dataset available for CSV export")
