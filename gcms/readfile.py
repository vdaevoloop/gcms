from icecream import ic
import logging
import numpy as np
import pandas as pd
from pathlib import Path
import re
from scipy import signal
import seaborn as sns
import sys


class MS_CSV_Reader:
    def __init__(
        self,
        root_data="/Users/duc/Developer/aevoloop/gcms/data/csv_graph_files",
        file="HT_R81_est_2_out.csv",
    ) -> None:
        self.root_data = Path(root_data)
        self.file = file
        self.df = self.csv2dataframe()

    def replace_second_comma(self):
        """
        v1.0
        Replace the second comma with a point. This comma is meant to be separator between seconts and ms.
        """
        # Get all indices from second comma. Skip first two lines
        p = r","
        path = self.root_data / self.file
        i = 0
        try:
            with (
                open(path, "r") as f,
                open(
                    self.root_data / re.sub(".csv", "_out.csv", self.file), "w"
                ) as out,
            ):
                for line in f:
                    if i < 2:
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

    def csv2dataframe(self) -> pd.Series | pd.DataFrame:
        """
        csv file must be of format:
            #Point,X(Minutes),Y(Counts)
            0,7.093,11364
            ...
            --> important is that the head contains X(Minutes) and Y(Counts)

        return: pd.DataFrame where non number values are removed
        """
        path = self.root_data / self.file
        r = pd.read_csv(path)
        logging.info("This is the csv import:")
        logging.info(r.head())
        logging.info(r.shape)
        logging.info("\nThis is the returned data frame:")
        logging.info(r[["X(Minutes)", "Y(Counts)"]])
        return r[["X(Minutes)", "Y(Counts)"]].dropna()

    def plot_ms(self):
        sns.relplot(data=self.df, x="X(Minutes)", y="Y(Counts)", kind="line")
        return
