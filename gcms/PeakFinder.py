from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
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

        peak_df = omsc.export_df(
            chrom=chrom_adapter.chrom, peaks=chrom_adapter.picked_peaks
        )[1]

        rt_corr = []
        index_corr = []
        intensity_corr = []

        for k in peak_df.index:
            i = peak_df["index"].iloc[k]
            max_intensity = 0  # peak_df["intensity"].iloc[k]
            max_index = i
            for j in range(2):
                if chrom["intensity"].iloc[max(0, i - 2 + j)] > max_intensity:
                    max_intensity = chrom["intensity"].iloc[max(0, i - 2 + j)]
                    max_index = max(0, i - 2 + j)
                if (
                    chrom["intensity"].iloc[min(len(chrom["intensity"] - 1), i + 2 - j)]
                    > max_intensity
                ):
                    max_intensity = chrom["intensity"].iloc[
                        min(len(chrom["intensity"] - 1), i + 2 - j)
                    ]
                    max_index = min(len(chrom["intensity"] - 1), i + 2 - j)
            rt_corr.append(chrom["retention_time"].iloc[max_index])
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
    chrom_intensity = chrom["intensity"]
    widths, _, _, _ = scipy.signal.peak_widths(
        chrom_intensity, peaks["index"], rel_height=1.0, wlen=11
    )

    if len(widths) != len(peaks["index"]):
        raise AssertionError(
            f"Error finding peak borders. width: {len(widths)} und peaks: {len(peaks['index'])} are of different length"
        )

    for i in peaks.index:
        for k in [-1, 1]:
            adjust_neighbor(chrom_intensity, peaks, i, k)

    widths, width_heights, left, right = scipy.signal.peak_widths(
        chrom_intensity, peaks["index"], rel_height=1.0, wlen=11
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


def adjust_neighbor(
    chrom: pd.DataFrame | pd.Series, peaks: pd.DataFrame, i: int, k: int
) -> None:
    """Adjusts the intensity of a chromatogram next to a peak for the scipy algorithm to calculate a non-zero prominence"""
    ind = peaks["index"].iloc[i]
    if k == -1:
        diff = chrom.iloc[ind] - chrom.iloc[max(0, ind + k)]
    else:
        diff = (
            chrom.iloc[ind]
            - chrom.iloc[
                min(
                    len(peaks["intensity"]),
                    ind + k,
                )
            ]
        )
    # HACK:
    # if diff < 0:
    #     raise ValueError(
    #         f"Error adjusting peak neighbor. Neighbor is larger than peak at retention time: {peaks['retention_time'].iloc[i]}"
    #     )
    if diff <= peaks["intensity"].iloc[i] * 0.2:
        if ind + k == 0 or ind + k == len(peaks.index) - 1:
            chrom.iloc[ind + k] = peaks["intensity"].iloc[i] / 2
        else:
            chrom.iloc[ind + k] = (chrom.iloc[ind + k] + chrom.iloc[ind + 2 * k]) / 2
