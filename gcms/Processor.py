from pathlib import Path
from gcms import DataReader, PeakFinder
import logging
import pandas as pd


class ChromatogramProcessor:
    """Main class that handles the data processing including data import, peak finder, peak area integration.

    Fields:
        reader: Data reader of type DataReader.ChromDataReader
        peak_finder: Peak finder of type PeakFinder.ChromPeakFinder
        filter: Filter of type Processor.ChromFilter
        integrator: Integrator calculates peak area of type Processor.ChromIntegrator
    """

    def __init__(self) -> None:
        self.df = ChromatogramDF()
        self.reader = None
        self.peak_finder = None
        self.filter = None
        self.integrator = None
        return

    def set_reader(self, reader: DataReader.ChromDataReader) -> None:
        self.reader = reader
        return

    def read_to_df(self, file_path: str | Path) -> None:
        """Using the reader to import chromatogram to df.chromatogram_og"""

        if self.reader is not None:
            self.df.set_chromatogram_og(self.reader.read_data(file_path))
        else:
            logging.error(
                f"A reader must be set in {self.__class__} using read_to_df()"
            )
        return

    def set_peak_finder(self, peak_finder: PeakFinder.ChromPeakFinder) -> None:
        """Dependency injection of a peak finder"""
        self.peak_finder = peak_finder
        return

    def find_peaks(self, chrom: pd.DataFrame | None) -> None:
        """Use dependency to peak finder to find peaks in the chromatogram"""
        if chrom is None:
            logging.error("Error in Processor.find_peaks(chrom): chrom is None")
            return
        if self.peak_finder is not None:
            self.peak_finder.find_peaks(chrom)
        else:
            logging.error("No ChromPeakFinder set, yet")
        return


class ChromatogramDF:
    """Data class to hold DataFrames of original chromatogram, filtered chrom, peaks with borders, peak_area

    Fields:
        chromatogram_og: original data as a pd.DataFrame[['index', 'retention_rate', 'intensity']]
        chromatogram_filtered: filtered chromatogram as pd.DataFrame[['index', 'retention_rate', 'intensity']]
        peaks: peaks of a chromatogram as pd.DataFrame[['index', 'retention_rate', 'intensity', 'left_border', 'right_border', 'area']]
        count_filter_iterations: Number of timex how often a filter was applied to chromatogram_filtered
    """

    def __init__(self) -> None:
        self.chromatogram_og: pd.DataFrame | None = None
        self.chromatogram_filtered: pd.DataFrame | None = None
        self.peaks: pd.DataFrame | None = None
        self.count_filter_iterations: int = 0
        return

    def set_chromatogram_og(self, df):
        self.chromatogram_og = df
