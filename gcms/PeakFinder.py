from abc import ABC, abstractmethod
import pandas as pd
import pyopenms as oms
from pyopenms_client import PyOpenMsClient as omsc
import logging
from icecream import ic
import scipy


class ChromPeakFinder(ABC):
    """Interface for peak finders that are specialized for chromatograms"""

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def find_peaks(self, chrom: pd.DataFrame) -> pd.DataFrame:
        """Takes a chromatogram and finds the find_peaks
        Returns:
            pandas DataFrame with 'retention_time' and 'intensity'
        """
        pass


class PyopenmsChromPeakFinder(ChromPeakFinder):
    """Using the peak finder implementations in PyOpenMs"""

    def __init__(self) -> None:
        super().__init__()

    def find_peaks(self, chrom: pd.DataFrame) -> pd.DataFrame:
        chrom_adapter = omsc.Chrom(testdata=False)
        chrom_adapter.import_df(chrom)
        chrom_adapter.find_peaks()

        return omsc.export_df(
            chrom=chrom_adapter.chrom, peaks=chrom_adapter.picked_peaks
        )[1]


def find_peak_borders(chrom: pd.DataFrame, peaks: pd.DataFrame) -> pd.DataFrame:
    """Using scipy.signal.peak_width to find the peak borders
    Args:
        signal: DataFrame that contains the signal. Must have columns 'retention_time', 'intensity'
        peaks: DataFrame that contains peaks of the same signal. Must have columns 'retention_time', 'intensity', 'border_left', 'border_right'

    Returns:
        The found borders are added to 'peaks'. The modified 'peaks' DataFrame is returned.

    """
    ic(chrom)
    ic(peaks)
    # widths, width_heights, left, right = scipy.signal.peak_widths(
    #     chrom["intensity"], peaks["intensity"]
    # )
    # return pd.DataFrame(
    #     {
    #         "retention_time": signal["retention_time"],
    #         "intensity": signal["intensity"],
    #         "width_heights": width_heights,
    #         "left_border": left,
    #         "right_border": right,
    #     }
    # )
