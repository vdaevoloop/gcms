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
        self.df_savgol = None

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

    def plots(self, choice: str):
        """Set plot option"""
        if self.df is None:
            logging.error("No dataframe available")
            return

        match choice:
            case "single":
                self.plot_single_df(self.df)
                return
            case "single-index":
                self.plot_single_df(self.df, x="index")
                return
            case "df-peaks":
                try:
                    if self.peaks is None:
                        self.set_df_peaks()
                    if self.peaks is None:
                        raise ValueError("Not able to set peaks df")
                except Exception as e:
                    logging.error(f"Failed to find peaks: {e}")
                    return
                self.plot_df_peaks(self.df, self.peaks)
                return
            case "savgol-single":
                try:
                    if self.df_savgol is None:
                        self.set_savgol_df()
                    if self.df_savgol is None:
                        raise ValueError("Failed to apply savgol filter")
                except Exception as e:
                    logging.error(f"Failed to apply savgol filter: {e}")
                    return
                self.plot_single_df(self.df_savgol)

    def plot_single_df(self, df: pd.DataFrame, x: str = "minutes", y: str = "counts"):
        """Plot single DF"""
        sns.relplot(data=df, x=x, y=y, kind="line")
        plt.title(self.file)
        return

    def plot_df_peaks(
        self,
        df: pd.DataFrame,
        peaks: pd.DataFrame,
        x: str = "minutes",
        y: str = "counts",
    ):
        """Plots data as lines and peaks as scatter plot"""
        _, ax = plt.subplots()

        sns.lineplot(data=df, x=x, y=y, label="GC", ax=ax)
        sns.scatterplot(
            data=peaks,
            x=x,
            y=y,
            marker="x",
            s=100,
            color="red",
            label="peaks",
            ax=ax,
        )
        plt.title(self.file)
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

    def set_df_peaks(self):
        """Sets objects peak data frame."""
        try:
            result = self.find_peaks()
            if result is None:
                raise ValueError("find_peaks returned None")
            self.peaks, self.peak_props, self.peaks_cwt = result

        except Exception as e:
            logging.error(f"Error while setting peak: {e}")
            raise e

        return

    def find_peaks(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame] | None:
        """Finds peak in GC data.

        Return:
            DataFrame of minutes and count values of peaks.
        """
        if self.df is None:
            logging.error("Dataframe is None")
            return None
        peak_indices, props = find_peaks(self.df["counts"], height=10000)

        prominences, left_bases, right_bases = peak_prominences(
            self.df["counts"], peak_indices
        )

        peak_indices_cwt = find_peaks_cwt(self.df["counts"], widths=10)

        if (
            peak_indices[-1] > self.df["index"].size
            or peak_indices_cwt[-1] > self.df["index"].size
        ):
            logging.error(f"Last peak at index {peak_indices[-1]} out of bound.")
            return None

        j = 0
        peak_series = {"index": [], "minutes": [], "counts": [], "prominence": []}
        for i in self.df["index"]:
            try:
                if i == peak_indices[j]:
                    peak_series["minutes"].append(self.df["minutes"].iloc[i])
                    peak_series["counts"].append(self.df["counts"].iloc[i])
                    peak_series["prominence"].append(prominences[j])
                    peak_series["index"].append((i))

                    j += 1
            except IndexError:
                break

        k = 0
        peak_series_cwt = {"index": [], "minutes": [], "counts": []}
        for i in self.df["index"]:
            try:
                if i == peak_indices_cwt[k]:
                    peak_series_cwt["minutes"].append(self.df["minutes"].iloc[i])
                    peak_series_cwt["counts"].append(self.df["counts"].iloc[i])
                    peak_series["index"].append((i))

                    k += 1
            except IndexError:
                break

        return (
            pd.DataFrame(peak_series),
            pd.DataFrame(props),
            pd.DataFrame(peak_series_cwt),
        )

    def set_savgol_df(self, wl: int = 3, poly: int = 2) -> pd.DataFrame | None:
        """Applies Savitzky-Golay-Filter on 'Counts'
        Parameters:
          wl: window length. Considered data points for filter/smoothing. Must be an odd number.
          poly: Highest order of polynom in equation to fit the curve. Should be less than wl.

        Return:
          Returns a new dataframe with smoothed 'Counts' data.
        """
        try:
            filtered = DF_filtered(self.df, wl, poly)
            self.df_savgol = filtered.get_df()
        except Exception as e:
            logging.error(f"Error applying savgol: {e}")

        return None


class DF_filtered:
    """GC data that is smoothed using the savgol filter."""

    def __init__(self, df, wl: int, poly: int):
        self.df = self.set_df(df, wl, poly)

    def set_df(self, df: pd.DataFrame, wl: int, poly: int) -> pd.DataFrame | None:
        """Apply savgol filter"""

        if "minutes" not in df.columns or "counts" not in df.columns:
            raise ValueError("Coulumns not matching")

        try:
            counts_savgol = signal.savgol_filter(df["counts"].to_numpy(), wl, poly)
        except Exception as e:
            raise ValueError(f"Could not process data: {e}")

        try:
            df_savgol = pd.DataFrame(
                {"minutes": df["minutes"], "counts": counts_savgol}
            )
        except Exception:
            raise ValueError(f"Could not process data: {df}")

        return df_savgol

    def get_df(self) -> pd.DataFrame | None:
        return self.df


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
