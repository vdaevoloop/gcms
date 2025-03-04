from icecream import ic
import logging
from numpy import ndarray
import pandas as pd
from pathlib import Path
import re
from scipy import signal
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from scipy.signal import find_peaks, find_peaks_cwt, peak_prominences


class GC_CSV_Reader:
    def __init__(
        self,
        root_data="/Users/duc/Developer/aevoloop/data/csv_graph_files",
        file="HT_R81_est_2_out.csv",
    ) -> None:
        self.root_data = Path(root_data)
        self.file = file
        self.df = self.csv2dataframe()
        self.peaks_cwt = None
        self.peaks = None
        self.peak_props = None

    def csv2dataframe(self) -> pd.DataFrame | None:
        """
        Reads a csv file and returns a DataFrame. Csv must contain the columns 'X(Minutes)' and 'Y(Counts)'.
        Columns are renamed to 'minutes' and 'counts'. Rows containing non-numeric values are removed.
        Return:
            pandas.DataFrame with "minutes", "counts" columns or None if error occurs
        """
        path: Path = self.root_data / self.file
        if not path.exists():
            logging.error(f"File at '{path}' does not exists.")
            return None
        try:
            df = pd.read_csv(
                path, usecols=["#Point", "X(Minutes)", "Y(Counts)"]
            ).rename(
                columns={
                    "#Point": "index",
                    "X(Minutes)": "minutes",
                    "Y(Counts)": "counts",
                }
            )
            if not pd.api.types.is_numeric_dtype(df["minutes"]):
                df["minutes"] = pd.to_numeric(df["minutes"], errors="coerce")
                logging.warning(
                    "Column 'minutes' contained non-numeric values, converted to NaN"
                )
            if not pd.api.types.is_numeric_dtype(df["counts"]):
                df["counts"] = pd.to_numeric(df["counts"], errors="coerce")
                logging.warning(
                    "Column 'counts' contained non-numeric values, converted to NaN"
                )
            if not pd.api.types.is_numeric_dtype(df["index"]):
                df["index"] = pd.to_numeric(df["index"], errors="coerce")
                logging.warning(
                    "Column 'index' contained non-numeric values, converted to NaN"
                )
            df = df.dropna()
            logging.info("removed all NaN rows from table")

            logging.info("File '{path}' converted sucessfully")
            logging.debug(df.head())
            logging.debug(df.shape)
            return df
        except Exception as e:
            logging.error(f"Error while reading file '{path}': {e}")
            return None

    def plot_df(self, df=0) -> None:
        if df == 0:
            if self.df is None:
                logging.error("dataframes must be initialized")
            sns.relplot(data=self.df, x="minutes", y="counts", kind="line")
        if df == 1:
            if self.peaks is None:
                logging.error("dataframes peaks must be initialized")
            sns.relplot(data=self.peaks, x="minutes", y="counts", kind="scatter")

        if df == 2:
            if self.df is None or self.peaks is None:
                logging.error("both dataframes must be initialized")
                return None

            fig, ax = plt.subplots()

            sns.lineplot(data=self.df, x="minutes", y="counts", label="GC", ax=ax)
            sns.scatterplot(
                data=self.peaks,
                x="minutes",
                y="counts",
                marker="x",
                s=100,
                color="red",
                label="peaks",
                ax=ax,
            )
        if df == 3:
            if self.df is None or self.peaks is None:
                logging.error("both dataframes must be initialized")
                return None

            fig, ax = plt.subplots()

            sns.lineplot(data=self.df, x="minutes", y="counts", label="GC", ax=ax)
            sns.scatterplot(
                data=self.peaks,
                x="minutes",
                y="counts",
                marker="x",
                s=100,
                color="red",
                label="peaks",
                ax=ax,
            )
            sns.scatterplot(
                data=self.peaks_cwt,
                x="minutes",
                y="counts",
                marker="o",
                s=100,
                color="orange",
                label="peaks_cwt",
                ax=ax,
            )

        plt.plot()

        return

    def width(self, start: float, end: float) -> int | None:
        """Counts how many datapoints are between two time points (retention time)."""
        if self.df is None:
            logging.error("Dataframe not initialized, yet.")
            return None
        if end < start:
            logging.error("start must come before end")
            return None
        width = self.df["minutes"].between(start, end)
        return width.sum()

    def set_df_peaks(self, range: float) -> None:
        """Sets objects peak data frame.
        Arguments:
          range [0, 1]:  Percent of largest peaks that should be included.
                  1.0 -> All peaks
                  0.1 -> 10 % of largest
        """
        try:
            result = self.find_peaks()
            if result is None:
                raise ValueError("find_peaks returned None")
            self.peaks, self.peak_props, self.peaks_cwt = result

        except Exception as e:
            logging.error(f"Error initializing peaks dataframe: {e}")

        # TODO:
        return

    def find_peaks(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame] | None:
        """Finds peak in GC data.

        Return:
            DataFrame of minutes and count values of peaks.
        """
        if self.df is None:
            logging.error("Dataframe is None")
            return None
        peak_indices, props = find_peaks(
            self.df["counts"], height=20000, threshold=1500, distance=4
        )

        prominences = peak_prominences(self.df["counts"], peak_indices)

        peak_indices_cwt = find_peaks_cwt(self.df["counts"], widths=10)

        if (
            peak_indices[-1] > self.df["index"].size
            or peak_indices_cwt[-1] > self.df["index"].size
        ):
            logging.error(f"Last peak at index {peak_indices[-1]} out of bound.")
            return None

        j = 0
        peak_series = {"minutes": [], "counts": [], "prominence": []}
        for i in self.df["index"]:
            try:
                if i == peak_indices[j]:
                    peak_series["minutes"].append(self.df["minutes"].iloc[i])
                    peak_series["counts"].append(self.df["counts"].iloc[i])
                    peak_series["prominence"].append(prominences[j])

                    j += 1
            except IndexError:
                break

        k = 0
        peak_series_cwt = {"minutes": [], "counts": []}
        for i in self.df["index"]:
            try:
                if i == peak_indices_cwt[k]:
                    peak_series_cwt["minutes"].append(self.df["minutes"].iloc[i])
                    peak_series_cwt["counts"].append(self.df["counts"].iloc[i])

                    k += 1
            except IndexError:
                break

        return (
            pd.DataFrame(peak_series),
            pd.DataFrame(props),
            pd.DataFrame(peak_series_cwt),
        )


def replace_second_comma(
    root_path="/Users/duc/Developer/aevoloop/data/csv_graph_files",
    file="HT_R81_est_2.csv",
):
    """
    v1.0
    Replace the second comma with a point. This comma is meant to be separator between seconts and ms.
    """
    # Get all indices from second comma. Skip first two lines
    p = r","
    root_data = Path(root_path)
    path = root_data / file
    i = 0
    try:
        with (
            open(path, "r") as f,
            open(root_data / re.sub(".csv", "_out.csv", file), "w") as out,
        ):
            for line in f:
                if i == 0:
                    i += 1
                    continue
                if i == 1:
                    out.write(line)
                    i += 1
                    continue
                inds = [m.start() for m in re.finditer(p, line.strip())]
                assert len(inds) > 1, f"Only one comma found in line {i}"
                out.write(line[: inds[1]] + "." + line[inds[1] + 1 :])
                i += 1
    except FileNotFoundError:
        logging.error(f"Input file '{path}' not found.")
    except ValueError as e:
        logging.error(str(e))
    except re.error as e:
        logging.error(f"Regular expression error: {e}")
    except IOError as e:
        logging.error(f"I/O error processing path '{path}': {e}")
    except Exception as e:
        logging.error(f"Unexpected error occured: {e}")
    logging.info("Finished sucessfully")
    return
