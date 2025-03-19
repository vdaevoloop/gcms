from abc import ABC, abstractmethod
import pandas as pd
import pyopenms as oms
from pyopenms_client import PyOpenMsClient as omsc
import logging
from icecream import ic
from scipy import signal


class ChromPeakFinder(ABC):
    """Interface for peak finders that are specialized for chromatograms"""

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def find_peaks(
        self, chrom: pd.DataFrame | oms.MSChromatogram | None = None
    ) -> pd.DataFrame:
        """Takes a chromatogram and finds the find_peaks
        Returns:
            pandas DataFrame with 'retention_time' and 'intensity'
        """
        pass


class PyopenmsChromPeakFinder(ChromPeakFinder):
    """Using the peak finder implementations in PyOpenMs"""

    def __init__(self) -> None:
        super().__init__()

    def find_peaks(
        self, chrom: pd.DataFrame | oms.MSChromatogram | None = None
    ) -> pd.DataFrame:
        mschrom = omsc.Chrom(testdata=False)
        mschrom.import_df(chrom)
        mschrom.find_peaks()

        return omsc.export_df(mschrom.picked_peaks)


def find_peak_borders(signal: pd.DataFrame, peaks: pd.DataFrame) -> pd.DataFrame:
    """Using scipy.signal.peak_width to find the peak borders
    Args:
        signal: DataFrame that contains the signal. Must have columns 'retention_time', 'intensity'
        peaks: DataFrame that contains peaks of the same signal. Must have columns 'retention_time', 'intensity', 'border_left', 'border_right'

    Returns:
        The found borders are added to 'peaks'. The modified 'peaks' DataFrame is returned.

    Raises:
        ValueError: If columns can not be found.
    """

    widths, width_heights, left, right = signal.peak_width(signal, peaks)
