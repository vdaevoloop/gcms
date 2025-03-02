from icecream import ic
import logging
import pandas as pd
from pathlib import Path
import re
from scipy import signal
import seaborn as sns
import sys
from scipy.signal import find_peaks_cwt


class GC_CSV_Reader:
    def __init__(
        self,
        root_data="/Users/duc/Developer/aevoloop/gcms/data/csv_graph_files",
        file="HT_R81_est_2_out.csv",
    ) -> None:
        self.root_data = Path(root_data)
        self.file = file
        self.df = self.csv2dataframe()

    def csv2dataframe(self) -> pd.DataFrame | None:
        """
        Reads a csv file and returns a DataFrame. Csv must contain the columns 'X(Minutes)' and 'Y(Counts)'.
        Columns are renamed to 'minutes' and 'counts'. Rows containing non-numeric values are removed.
        Return:
            pandas.DataFrame with "minutes", "counts" columns or None if error occurs
        """
        path = self.root_data / self.file
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

    def plot_gc(self):
        sns.relplot(data=self.df, x="minutes", y="counts", kind="line")
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

    def find_peak(self) -> pd.Series | None:
        """Finds peak in GC data.

        Return:
            Series where peak values are taken from data frame but rest is set to 0.
        """
        if self.df is None:
            logging.error("Dataframe is None")
            return None
        peak_indices = find_peaks_cwt(self.df["counts"], widths=13)
        return pd.Series()


def replace_second_comma(
    root_path="/Users/duc/Developer/aevoloop/gcms/data/csv_graph_files",
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
                if len(inds) < 2:
                    raise ValueError(f"Line {i} expects at least 2 commas.")
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
