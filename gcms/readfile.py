import pandas as pd
import numpy as np
import re
import sys
from pathlib import Path
from icecream import ic
from scipy import signal


class MS_CSV_Reader:
    def __init__(
        self, root_data="./../data/csv_graph_files/", file="HT_R81_est_2_out.csv"
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
        p = r"(,)"
        path = self.root_data / self.file
        i = 0
        with open(path, "r") as f:
            with open(
                self.root_data / re.sub(".csv", "_out.csv", self.file), "w"
            ) as out:
                for line in f:
                    if i < 2:
                        out.write(line)
                        i += 1
                        continue
                    inds = [m.start() for m in re.finditer(p, line.strip())]
                    assert len(inds) > 1, f"Only one comma found in line {i}"
                    out.write(line[: inds[1]] + "." + line[inds[1] + 1 :])
                    i += 1
        print("Finished sucessfully")
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
        print("This is the csv import:")
        print(r.head())
        print(r.shape)
        print("\nThis is the returned table:")
        print(r[["X(Minutes)", "Y(Counts)"]])
        return r[["X(Minutes)", "Y(Counts)"]].dropna()

    def plot_ms(self):
        self.df.plot(x="X(Minutes)", y="Y(Counts)", kind="line")
        return
