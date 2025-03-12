from icecream import ic
import logging
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import sys


class ChromPlotter:
    """Collection of plotting methods"""

    def plot_any_scatter(
        self,
        dfs: list[pd.DataFrame],
        x: str = "retention_time",
        y: str = "intensity",
        labels: list[str] | None = None,
        title: str = "DataFrames Scatter Plot",
        legend: bool = True,
    ) -> None:
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
            labels = [f"DF {i + 1}" for i in range(len(dfs))]
