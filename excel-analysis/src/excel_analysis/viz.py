"""Simple plotting helpers using Plotly"""
import plotly.express as px
import pandas as pd


def plot_histogram(df: pd.DataFrame, column: str):
    return px.histogram(df, x=column)


from typing import Optional

def plot_scatter(df: pd.DataFrame, x: str, y: str, color: Optional[str] = None):
    return px.scatter(df, x=x, y=y, color=color)


def plot_corr_heatmap(df: pd.DataFrame, numeric_only: bool = True):
    num = df.select_dtypes(include=["number"]) if numeric_only else df
    corr = num.corr()
    return px.imshow(corr, text_auto=True)


def plot_supplier_totals(agg_df: pd.DataFrame, group_col: str = "Supplier", value_col: str = "value"):
    """Plot a bar chart of supplier totals from an aggregated dataframe.

    Expects a dataframe with columns [group_col, value_col] or [group_col, 'value'].
    """
    if group_col not in agg_df.columns:
        # try to find the first column to treat as group
        group_col = agg_df.columns[0]
    if value_col not in agg_df.columns and "value" in agg_df.columns:
        value_col = "value"
    fig = px.bar(agg_df, x=group_col, y=value_col, color=value_col, labels={group_col: group_col, value_col: "Total"})
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    return fig
