"""Streamlit web UI for Excel analysis"""
import streamlit as st
import pandas as pd
from pathlib import Path
from excel_analysis.io import load_excel, to_excel_bytes
from excel_analysis.clean import (
    standardize_columns,
    drop_high_missing_columns,
    parse_date_columns,
    strip_column_whitespace,
    parse_percent_column,
    parse_conditions_column,
    coerce_numeric_columns,
)
from excel_analysis.analyse import summary_stats, missing_summary, aggregate_by, find_value_columns
from excel_analysis.viz import plot_histogram, plot_corr_heatmap, plot_supplier_totals
from excel_analysis.io import save_excel_report
from excel_analysis.ui import list_sample_workbooks, save_upload, list_reports
from excel_analysis.runner import read_status
from excel_analysis.report import generate

st.set_page_config(layout="wide")
st.title("Excel Analysis Web UI")

# Two tabs: Explore (existing) and Run & Reports (new)
explore_tab, run_tab = st.tabs(["Explore", "Run & Reports"])

with explore_tab:
    st.header("Data explorer")
    uploaded = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])
    if uploaded is not None:
        df = load_excel(uploaded)

        st.sidebar.header("Cleaning")
        if st.sidebar.checkbox("Strip column/value whitespace", value=True):
            df = strip_column_whitespace(df)

        if st.sidebar.checkbox("Standardize columns", value=True):
            df = standardize_columns(df)

        thresh = st.sidebar.slider("Min non-missing fraction per column", 0.0, 1.0, 0.1)
        df = drop_high_missing_columns(df, threshold=1 - thresh)

        # Auto-detect percent-like object columns
        percent_like_cols = [c for c in df.columns if df[c].dtype == object and df[c].astype(str).str.contains('%').any()]
        if percent_like_cols:
            if st.sidebar.checkbox("Parse percent-like columns", value=True):
                for c in percent_like_cols:
                    df = parse_percent_column(df, c, out_col=c, as_fraction=False)

        # Parse composite conditions column if present
        cond_col = "Conditions Not Applied Percentage"
        if cond_col in df.columns and st.sidebar.checkbox("Parse conditions column (split codes)", value=False):
            df = parse_conditions_column(df, cond_col, prefix="cond_")

        if st.sidebar.checkbox("Coerce numeric-like object columns", value=True):
            df = coerce_numeric_columns(df)

        st.header("Preview")
        st.dataframe(df.head())

        st.header("Summary stats")
        st.dataframe(summary_stats(df))

        st.header("Missing values")
        st.dataframe(missing_summary(df))

        st.header("Plots")
        numeric_cols = list(df.select_dtypes(include=["number"]).columns)
        if numeric_cols:
            col = st.selectbox("Choose numeric column for histogram", numeric_cols)
            fig = plot_histogram(df, col)
            st.plotly_chart(fig, use_container_width=True)

            if st.checkbox("Show correlation heatmap"):
                st.plotly_chart(plot_corr_heatmap(df), use_container_width=True)

        # --- Supplier aggregation & visualization ---
        st.header("Supplier aggregation")

        # detect supplier-like columns
        supplier_candidates = [c for c in df.columns if "supplier" in c.lower() or "vendor" in c.lower()]
        if not supplier_candidates:
            supplier_candidates = [c for c in df.columns if df[c].nunique() < 200 and df[c].dtype == object]

        value_candidates = find_value_columns(df)

        if supplier_candidates and value_candidates:
            group_col = st.selectbox("Group by (supplier) column", supplier_candidates)
            val_col = st.selectbox("Value column to aggregate", value_candidates)
            agg_func = st.selectbox("Aggregation", ["sum", "mean", "count", "median"], index=0)
            top_n = st.slider("Top N suppliers", min_value=5, max_value=100, value=20)
            asc = st.checkbox("Sort ascending (smallest first)", value=False)

            agg_df = aggregate_by(df, group_col=group_col, value_col=val_col, agg=agg_func, top_n=top_n, ascending=asc)
            st.subheader("Top suppliers by total")
            st.dataframe(agg_df)
            fig = plot_supplier_totals(agg_df, group_col=group_col, value_col="value")
            st.plotly_chart(fig, use_container_width=True)

            # Download cleaned dataframe as Excel
            st.download_button(
                "Download cleaned Excel",
                data=to_excel_bytes(df),
                file_name="cleaned.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.info("No supplier-like or value-like columns detected for aggregation")
    else:
        st.info("Upload an Excel file (xlsx/xls) to begin")

with run_tab:
    st.header("Run reports")
    st.write("Run vendor report on a selected or uploaded workbook and download the generated report.")

    sample_files = list_sample_workbooks()
    opts = ["Upload new workbook"] + [str(p) for p in sample_files]
    choice = st.selectbox("Select workbook", opts)

    workbook_path = None
    if choice == "Upload new workbook":
        up = st.file_uploader("Upload workbook to run report", type=["xlsx", "xls"] )
        if up is not None:
            saved = save_upload(up)
            st.success(f"Saved upload to: {saved}")
            workbook_path = saved
    else:
        workbook_path = Path(choice)

    run_now = st.button("Run report now")
    if run_now:
        if not workbook_path:
            st.error("Select or upload a workbook first")
        else:
            st.info("Generating report — this may take a few seconds")
            try:
                out = generate(Path(workbook_path))
                st.success(f"Report generated: {out}")
                with open(out, "rb") as fh:
                    st.download_button("Download report", data=fh.read(), file_name=Path(out).name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                st.error(f"Report generation failed: {e}")

    st.markdown("---")
    st.header("Recent reports")
    reports = list_reports()
    if reports:
        for r in reports:
            st.write(f"- {r.name}  (size: {r.stat().st_size} bytes)")
            with open(r, "rb") as fh:
                st.download_button(f"Download {r.name}", data=fh.read(), file_name=r.name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("No reports found in reports/exports/")

    st.markdown("---")
    st.header("Last run status")
    status = read_status()
    if status:
        st.json(status)
    else:
        st.info("No runs recorded yet")
