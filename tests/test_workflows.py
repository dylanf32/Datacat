from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import matplotlib
matplotlib.use("Agg")
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from Datacat import ingestion, statistic
from main import main

ROOT = Path(__file__).resolve().parents[1]


def uploaded_csv():
    upload = BytesIO(b"group,x,y\na,1,2\na,2,4\nb,3,5\nb,4,8\nb,,10\n")
    upload.name = "sample.csv"
    return upload


def run_dashboard(app):
    # Supply the uploaded bytes at the UI boundary; execute the real app script.
    with patch("streamlit.file_uploader", return_value=uploaded_csv()):
        app.run(timeout=30)
    assert not app.exception
    return app


def test_dashboard_empty_state():
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    assert not app.exception
    assert "Choose a CSV" in app.info[0].value


def test_dashboard_clean_reset_and_export():
    app = run_dashboard(AppTest.from_file(str(ROOT / "app.py")))
    assert len(app.dataframe) == 2
    app.sidebar.radio[0].set_value("Clean data")
    run_dashboard(app)
    next(button for button in app.button if button.label == "Apply cleaning").click()
    run_dashboard(app)
    assert len(app.session_state.working_df) == 4
    app.sidebar.button[0].click()
    run_dashboard(app)
    assert len(app.session_state.working_df) == 5
    app.sidebar.radio[0].set_value("Export")
    run_dashboard(app)
    assert len(app.get("download_button")) == 1


@pytest.mark.parametrize("analysis", ["Summary statistics", "Column mean", "Spearman correlation", "One-way ANOVA"])
def test_dashboard_statistics(analysis):
    app = run_dashboard(AppTest.from_file(str(ROOT / "app.py")))
    app.sidebar.radio[0].set_value("Statistical analysis")
    run_dashboard(app)
    app.selectbox[0].set_value(analysis)
    run_dashboard(app)
    if analysis == "One-way ANOVA":
        next(button for button in app.button if button.label == "Run ANOVA").click()
        run_dashboard(app)
    assert not app.error
    assert len(app.dataframe) == 1
    assert len(app.get("download_button")) == 1


@pytest.mark.parametrize("plot", ["Histogram", "Box plot", "Violin plot", "Scatter plot", "Correlation heatmap"])
def test_dashboard_plots(plot):
    app = run_dashboard(AppTest.from_file(str(ROOT / "app.py")))
    app.sidebar.radio[0].set_value("Visualization")
    run_dashboard(app)
    app.selectbox[0].set_value(plot)
    run_dashboard(app)
    assert not app.error
    assert len(app.get("download_button")) == 1


def test_ingestion_csv_excel_and_export(tmp_path, monkeypatch):
    frame = pd.DataFrame({"x": [1, 2], "group": ["a", "b"]})
    monkeypatch.setattr(ingestion, "folder", tmp_path)
    frame.to_csv(tmp_path / "sample.csv", index=False)
    frame.to_excel(tmp_path / "sample.xlsx", index=False)
    for name in ("sample.csv", "sample.xlsx"):
        loaded, _ = ingestion.get_data(name)
        pd.testing.assert_frame_equal(loaded, frame)
    # Redirect the module's repository root without writing generated data to source.
    monkeypatch.setattr(ingestion, "__file__", str(tmp_path / "Datacat" / "ingestion.py"))
    output = ingestion.processed(frame, "result")
    pd.testing.assert_frame_equal(pd.read_csv(output / "result.csv"), frame)


def test_terminal_profile_and_correlation(monkeypatch, capsys):
    frame = pd.DataFrame({"x": [1, 2, 4], "y": [4, 3, 1]})
    monkeypatch.setattr(ingestion, "get_data", lambda name: (frame, name))
    answers = iter(["sample.csv", "1", "4", "3", "n", "0"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    main()
    assert "Missing values per column" in capsys.readouterr().out
    pd.testing.assert_frame_equal(statistic.correlation(frame), frame.corr(method="spearman"))
    pd.testing.assert_frame_equal(statistic.correlation_pearson(frame), frame.corr(method="pearson"))
