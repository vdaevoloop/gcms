from pathlib import Path
from gcms import DataReader, PeakFinder, Integrator
import logging
import pandas as pd
from icecream import ic
import numpy as np
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
            self.df.init_chromatogram(self.reader.read_data(file_path))
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
        if self.df.chromatogram is None or self.df.peaks is None:
            raise ValueError(
                f"Error finding peak borders with 'chromatogram': {self.df.chromatogram} and 'peaks': {self.df.peaks}\n Must not be None."
            )
        self.df.peaks = PeakFinder.find_peak_borders(
            self.df.chromatogram, self.df.peaks
        )

    def create_peak_border_df(self) -> pd.DataFrame:
        """Create a DataFrame from peak borders to be plotted"""
        border_rt = []
        border_intensity = []
        if self.df.peaks is None or self.df.chromatogram is None:
            raise ValueError(
                f"Error creating peak border DataFrame for plotting: chrom is {type(self.df.chromatogram)}, peaks is {type(self.df.peaks)}"
            )
        for i in self.df.peaks.index:
            m = self.df.chromatogram.iloc[self.df.peaks["left_border"].iloc[i]]
            n = self.df.chromatogram.iloc[self.df.peaks["right_border"].iloc[i]]
            border_rt.append(m["retention_time"])
            border_intensity.append(m["intensity"])
            border_rt.append(n["retention_time"])
            border_intensity.append(n["intensity"])
        return pd.DataFrame(
            {"retention_time": border_rt, "intensity": border_intensity}
        )

    def integrate_peak_area(self) -> None:
        """Calculates area beneath peaks and saves areas to df.peaks"""
        if (
            self.integrator is None
            or self.df.chromatogram is None
            or self.df.peaks is None
        ):
            logging.error(
                f"Error integrating peak area. Check if objects are not initialized: integrator: {type(self.integrator)}, chromatogram: {type(self.df.chromatogram)}, peaks: {type(self.df.peaks)}"
            )
            return
        self.integrator.integrate(self.df.chromatogram, self.df.peaks)
        return

    def normalize_integral(self) -> None:
        if self.integrator is None or self.df.peaks is None:
            logging.error(
                f"Error integrating peak area. Check if objects are not initialized: integrator: {type(self.integrator)},  peaks: {type(self.df.peaks)}"
            )
            return
        self.integrator.norm_area(self.df.peaks)
        return

    # HACK:
    def filter_savgol(self) -> None:
        """Apply Savgol and replace df.chromatogram"""
        intensity_filtered = scipy.signal.savgol_filter(
            self.df.chromatogram["intensity"], 5, 2
        )
        self.df.chromatogram["intensity"] = intensity_filtered


class ChromatogramDF:
    """Data class to hold DataFrames of original chromatogram, filtered chrom, peaks with borders, peak_area

    Fields:
        chromatogram_og: original data as a pd.DataFrame[['index', 'retention_time', 'intensity']]
        chromatogram: filtered chromatogram as pd.DataFrame[['index', 'retention_time', 'intensity']]
        peaks: peaks of a chromatogram as pd.DataFrame[['retention_time', 'intensity', 'left_border', 'right_border', 'area']]
        count_filter_iterations: Number of timex how often a filter was applied to chromatogram_filtered
    """

    def __init__(self) -> None:
        self.chromatogram_og: pd.DataFrame | None = None
        self.chromatogram: pd.DataFrame | None = None
        self.peaks: pd.DataFrame | None = None
        self.count_filter_iterations: int = 0
        self.post_processed: None | pd.DataFrame = None
        return

    def init_chromatogram(self, df):
        self.chromatogram_og = df
        self.chromatogram = df


# TODO:
def calc_ratio_total_area(cdf: ChromatogramDF):
    """Takes the largest 70 peaks and calculates the ratio of each peaks area compqared to the total area of largest peaks."""
    pass


def get_sample(cdf: ChromatogramDF, skip_largest: bool = True) -> pd.DataFrame | None:
    """Get the basis for recursion"""

    if cdf.peaks is None:
        logging.error("Error getting samples for recursion: peaks DF is none")
        return None
    peaks = cdf.peaks.copy(deep=True)
    if peaks is cdf.peaks:
        raise AssertionError("Same object")

    if skip_largest:
        peaks = peaks.drop(index=peaks["intensity"].idxmax())

    intensities = peaks["intensity"]
    threshold = (intensities.max() + intensities.min()) / 2
    index = []
    intensity = []
    rt = []

    for i in peaks.index:
        if peaks.at[i, "intensity"] > threshold:
            index.append(cdf.peaks.at[i, "index"])
            intensity.append(cdf.peaks.at[i, "intensity"])
            rt.append(cdf.peaks.at[i, "retention_time"])
    df = pd.DataFrame({"index": index, "intensity": intensity, "retention_time": rt})
    return df


def func(x, a1, a2, a3, a4, a5) -> int:
    """Polynomial function"""
    return a1 * x**4 + a2 * x**3 + a3 * x**2 + a4 * x + a5


def fit_model(x, y) -> np.ndarray:
    """Returns parameters"""
    rt = x.to_list()
    intensity = y.to_list()

    popt, _ = scipy.optimize.curve_fit(func, rt, intensity)
    return popt


def calc_predict(x: float, a: np.ndarray) -> int:
    """Calc intensity with parameter array a"""
    return func(x, a[0], a[1], a[2], a[3], a[4])
