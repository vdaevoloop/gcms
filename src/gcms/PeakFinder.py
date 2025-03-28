from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import pyopenms as oms
from .pyopenms_client import PyOpenMsClient as omsc
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

        peak_df = omsc.export_df(
            chrom=chrom_adapter.chrom, peaks=chrom_adapter.picked_peaks
        )[1]

        rt_corr = []
        index_corr = []
        intensity_corr = []

        chrom_len = len(chrom) - 1

        for k in peak_df.index:
            i = int(peak_df.at[k, "index"])
            max_intensity = chrom.at[i, "intensity"]
            max_index = i

            for j in range(-2, 3):
                check_idx = max(0, min(chrom_len, i + j))
                check_intensity = chrom.at[check_idx, "intensity"]
                if check_intensity > max_intensity:
                    max_intensity = check_intensity
                    max_index = check_idx

            rt_corr.append(chrom.at[max_index, "retention_time"])
            index_corr.append(max_index)
            intensity_corr.append(max_intensity)

        if len(rt_corr) != len(peak_df["retention_time"]):
            raise AssertionError(
                f"Error checking for local max between found peaks and original chrom: length found peaks:{len(peak_df['retention_time'])}, corrected peaks: {len(rt_corr)}"
            )
        return pd.DataFrame(
            {
                "index": index_corr,
                "retention_time": rt_corr,
                "intensity": intensity_corr,
            }
        )


def find_peak_borders(chrom: pd.DataFrame, peaks: pd.DataFrame) -> pd.DataFrame:
    """Using scipy.signal.peak_width to find the peak borders
    Args:
        signal: DataFrame that contains the signal. Must have columns 'retention_time', 'intensity'
        peaks: DataFrame that contains peaks of the same signal. Must have columns 'retention_time', 'intensity', 'border_left', 'border_right'

    Returns:
        The found borders are added to 'peaks'. The modified 'peaks' DataFrame is returned.

    """
    widths, _, _, _ = scipy.signal.peak_widths(
        chrom["intensity"], peaks["index"], rel_height=1.0, wlen=11
    )

    if len(widths) != len(peaks["index"]):
        raise AssertionError(
            f"Error finding peak borders. width: {len(widths)} und peaks: {len(peaks['index'])} are of different length"
        )

    for i in peaks.index:
        for k in [-1, 1]:
            adjust_neighbor(chrom, peaks, i, k)

    widths, width_heights, left, right = scipy.signal.peak_widths(
        chrom["intensity"], peaks["index"], rel_height=1.0, wlen=11
    )

    for i in peaks.index:
        if widths[i] == 0:
            logging.error(
                f"Width with value 0 at retention time: {peaks['retention_time'].iloc[i]}"
            )

    left_border = []
    right_border = []
    for i in peaks.index:
        left_border.append(int(np.floor(left[i])))
        right_border.append(int(np.ceil(right[i])))
    peaks["width"] = widths
    peaks["width_height"] = width_heights
    peaks["left_border"] = left_border
    peaks["right_border"] = right_border
    return peaks


def adjust_neighbor(chrom: pd.DataFrame, peaks: pd.DataFrame, i: int, k: int) -> None:
    """Adjusts the intensity of a chromatogram next to a peak for the scipy algorithm to calculate a non-zero prominence"""
    ind = int(peaks.at[i, "index"])
    neighbor_indx = max(0, min(len(chrom) - 1, ind + k))
    diff = chrom.at[ind, "intensity"] - chrom.at[neighbor_indx, "intensity"]

    if diff <= 0.2 * peaks.at[i, "intensity"]:
        if neighbor_indx == 0 or neighbor_indx == len(chrom) - 1:
            chrom.at[neighbor_indx, "intensity"] = peaks.at[i, "intensity"] / 2
        else:
            next_indx = neighbor_indx + k
            chrom.at[neighbor_indx, "intensity"] = (
                chrom.at[neighbor_indx, "intensity"] + chrom.at[next_indx, "intensity"]
            ) / 2
