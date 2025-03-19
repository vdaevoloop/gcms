from abc import ABC, abstractmethod
import pandas as pd
import pyopenms as oms
from pyopenms_client import PyOpenMsClient as omsc
import logging
from icecream import ic


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
