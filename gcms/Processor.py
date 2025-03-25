from pathlib import Path
from gcms import DataReader, PeakFinder, Integrator
import logging
import pandas as pd
from icecream import ic
import scipy


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

    def set_peak_finder(self, peak_finder: PeakFinder.ChromPeakFinder) -> None:
        """Dependency injection of a peak finder"""
        self.peak_finder = peak_finder
        return

    def set_integrator(self, integrator: Integrator.ChromIntegrator) -> None:
        self.integrator = integrator

    def read_to_df(self, file_path: str | Path) -> None:
        """Using the reader to import chromatogram to df.chromatogram_og"""

        if self.reader is not None:
            self.df.set_chromatogram_og(self.reader.read_data(file_path))
        else:
            logging.error(
                f"A reader must be set in {self.__class__} using read_to_df()"
            )
        return

    def find_peaks(self, chrom: pd.DataFrame | None) -> None:
        """Use dependency to peak finder to find peaks in the chromatogram"""
        if chrom is None:
            logging.error("Error in Processor.find_peaks(chrom): chrom is None")
            return
        if self.peak_finder is not None:
            self.df.peaks = self.peak_finder.find_peaks(chrom)
        else:
            logging.error("No ChromPeakFinder set, yet")
        return

    def find_peak_borders(self) -> None:
        """Add peak borders to df.peaks

        Raises:
            ValueError: If columns can not be found.
        """
        if self.df.chromatogram_og is None or self.df.peaks is None:
            raise ValueError(
                f"Error finding peak borders with 'chromatogram': {self.df.chromatogram_og} and 'peaks': {self.df.peaks}\n Must not be None."
            )
        self.df.peaks = PeakFinder.find_peak_borders(
            self.df.chromatogram_og, self.df.peaks
        )

    def create_peak_border_df(self) -> pd.DataFrame:
        """Create a DataFrame from peak borders to be plotted"""
        border_rt = []
        border_intensity = []
        if self.df.peaks is None or self.df.chromatogram_og is None:
            raise ValueError(
                f"Error creating peak border DataFrame for plotting: chrom is {type(self.df.chromatogram_og)}, peaks is {type(self.df.peaks)}"
            )
        for i in self.df.peaks.index:
            m = self.df.chromatogram_og.iloc[self.df.peaks["left_border"].iloc[i]]
            n = self.df.chromatogram_og.iloc[self.df.peaks["right_border"].iloc[i]]
            border_rt.append(m["retention_time"])
            border_intensity.append(m["intensity"])
            border_rt.append(n["retention_time"])
            border_intensity.append(n["intensity"])
        return pd.DataFrame(
            {"retention_time": border_rt, "intensity": border_intensity}
        )

    def integrate_peak_area(self) -> None:
        """Calculates area beneath peaks and saves areas to df.peaks"""
        if self.integrator is None:
            logging.error("Must initialize integrator first")
            return
        self.integrator.integrate(self.df.chromatogram_og, self.df.peaks)
        return

    def normalize_integral(self) -> None:
        if self.integrator is None:
            logging.error("Must initialize integrator first")
            return
        self.integrator.norm_area(self.df.peaks)
        return

    # HACK:
    def filter_savgol(self) -> None:
        """Apply Savgol and replace df.chromatogram_og"""
        intensity_filtered = scipy.signal.savgol_filter(
            self.df.chromatogram_og["intensity"], 5, 2
        )
        self.df.chromatogram_og["intensity"] = intensity_filtered


class ChromatogramDF:
    """Data class to hold DataFrames of original chromatogram, filtered chrom, peaks with borders, peak_area

    Fields:
        chromatogram_og: original data as a pd.DataFrame[['index', 'retention_time', 'intensity']]
        chromatogram_filtered: filtered chromatogram as pd.DataFrame[['index', 'retention_time', 'intensity']]
        peaks: peaks of a chromatogram as pd.DataFrame[['retention_time', 'intensity', 'left_border', 'right_border', 'area']]
        count_filter_iterations: Number of timex how often a filter was applied to chromatogram_filtered
    """

    def __init__(self) -> None:
        self.chromatogram_og: pd.DataFrame | None = None
        self.chromatogram_filtered: pd.DataFrame | None = None
        self.peaks: pd.DataFrame | None = None
        self.count_filter_iterations: int = 0
        self.post_processed: None | pd.DataFrame = None
        return

    def set_chromatogram_og(self, df):
        self.chromatogram_og = df


class PostProcessing:
    """Collection of post processing methods"""
