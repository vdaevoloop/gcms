import logging
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import seaborn as sns


def plot_any_scatter(
    dfs: list[pd.DataFrame] | tuple[pd.DataFrame],
    x: str = "retention_time",
    y: str = "intensity",
    labels: list[str] | tuple[str] | None = None,
    title: str = "DataFrames Scatter Plot",
    legend: bool = True,
    ax: Axes | None = None,
) -> Axes | None:
    # TODO:Finish documentation
    """Takes a list of DataFrames and plots all in one scatter plot

    Args:
        dfs: A list of pandas DataFrame. All frames must have the same columns for x and y (default for chromatograms: x='retention_time' and y='intensity')
        x: Name for x-axis
        y: Name for y-axis
    """
    if labels is not None:
        if len(dfs) != len(labels):
            raise ValueError("arg 'labels' must be of same length as 'dfs'")
    else:
        labels = [f"DF {i}" for i in range(len(dfs))]

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    try:
        for i, df in enumerate(dfs):
            if x not in df.columns or y not in df.columns:
                raise KeyError(f"DF {i} does not contain all colums: '{x}', '{y}'")

            sns.lineplot(data=df, x=x, y=y, label=labels[i])

    except Exception as e:
        logging.error(f"Error occured during plotting: {e}")
        raise

    ax.set_title(title)
    return ax
