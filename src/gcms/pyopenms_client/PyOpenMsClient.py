from decimal import ExtendedContext
from matplotlib.pyplot import axis
from pandas import DataFrame
import pandas as pd
import numpy as np
from pyopenms import (
    MSChromatogram,
    plotting,
    MSExperiment,
    MzMLFile,
    PeakPickerChromatogram,
)
import logging
import pathlib
from icecream import ic


class Exp:
    """Adapter to MSExperiment to read and write mzML files.
    Argument:
        mzml_file: Must be the absolute path to the file.
    """

    TESTDATA = ".data/test_mzml/PS_R667_EST_3.mzML"

    def __init__(
        self,
        mzml_file: pathlib.Path | None = None,
        testdata: bool = True,
        selfinit: bool = True,
    ) -> None:
        self.exp = MSExperiment()
        self.mzml_file = None

        if mzml_file is None and testdata is True:
            try:
                self.mzml_file = pathlib.Path(self.__class__.TESTDATA)
            except Exception as e:
                raise ValueError(f"Error reading path '{self.__class__.TESTDATA}': {e}")
        elif mzml_file is None and testdata is False:
            pass
        else:
            try:
                self.mzml_file = mzml_file
            except Exception as e:
                logging.error(
                    f"Error while converting path string to pathlib.Path: {e}"
                )
                raise

        if self.mzml_file is not None and selfinit is True:
            self.set_dataset(str(self.mzml_file))

        return

    def set_dataset(self, file: str) -> None:
        """Reads a mzML file into an Exp object"""
        try:
            MzMLFile().load(file, self.exp)
        except Exception as e:
            raise FileNotFoundError(f"Error while importing mzML file '{file}': {e}")

    def extract_chrom(self) -> MSChromatogram | None:
        """Extracts a TIC (total intensity current)."""
        if self.mzml_file is None:
            return None
        if self.exp.getNrChromatograms() != 1:
            raise ValueError(
                f"Number of chromatograms contained in mzML file: {self.exp.getNrChromatograms()}"
            )

        return self.exp.getChromatogram(0)


class Chrom:
    """Adapter to MSChromatogram

    Extract a single chromatogram from a mzML file.
    Do peak-finding and peak-integration work."""

    def __init__(
        self,
        mzml_file: pathlib.Path | None = None,
        selfinit: bool = True,
        testdata: bool = True,
    ) -> None:
        self.chrom: MSChromatogram = Exp(
            mzml_file, testdata=testdata, selfinit=selfinit
        ).extract_chrom()
        self.picked_peaks = MSChromatogram()
        self.picker = PeakPickerChromatogram()
        return

    def plot(self, chrom=None) -> None:
        if chrom is None:
            chrom = self.chrom
        plotting.plot_chromatogram(chrom)
        return

    def find_peaks(self) -> None:
        """Find peaks inside a MSChromatogram and save peaks to separate MSChromatogram"""
        params = self.picker.getParameters()
        params.setValue(b"sgolay_frame_length", 5)
        params.setValue(b"sgolay_polynomial_order", 2)
        params.setValue(b"use_gauss", "false")
        params.setValue(b"signal_to_noise", 0.8)
        self.picker.setParameters(params)

        try:
            self.picker.pickChromatogram(
                self.chrom,
                self.picked_peaks,
            )
            logging.info("Peak picker finished successfully")
        except Exception as e:
            raise ValueError(f"Error finding peaks: {e}")
        return

    def import_df(self, df: DataFrame) -> None:
        """Converts a DF to a MSChromatogram
        Args:
            df: pandas DataFrame with columns 'retention_time', 'intensity'
        Retuns:
            None; MSChromatogram is stored in self.chrom
        Raises:
            ValueError: If df does not contain the two necessary columns
        """
        if "retention_time" not in df.columns or "intensity" not in df.columns:
            raise ValueError(
                "DataFrame does not contain the right columns 'retention_time', 'intensity'"
            )
        mschrom = MSChromatogram()
        mschrom.set_peaks([df["retention_time"], df["intensity"]])
        self.chrom = mschrom


def export_df(chrom: MSChromatogram, peaks: MSChromatogram | None) -> list[DataFrame]:
    """Extract retention time and intensity and return as DataFrame"""

    df = []
    chrom_df = read_peaks_to_df(chrom)
    chrom_df["index"] = chrom_df.index
    df.append(chrom_df)

    if peaks is not None:
        peaks_df = read_peaks_to_df(peaks)
        time_step = (
            chrom_df["retention_time"].iloc[0] - chrom_df["retention_time"].iloc[2]
        ) / 2
        peak_indices = []
        current_peak = 0
        last_peak = len(peaks_df["retention_time"])
        last_chrom_point = len(chrom_df["retention_time"])
        for i, chrom_rt in enumerate(chrom_df["retention_time"]):
            if current_peak == last_chrom_point or current_peak == last_peak:
                break
            if (
                chrom_rt
                >= peaks_df["retention_time"].iloc[current_peak] - time_step / 2
            ):
                peak_indices.append(chrom_df["index"].iloc[i])
                current_peak += 1

        if len(peak_indices) != len(peaks_df["retention_time"]):
            raise AssertionError(
                f"Error indexing peaks DataFrame: length of indices:{len(peak_indices)} and retention time:{len(peaks_df['retention_time'])}"
            )
        peaks_df["index"] = peak_indices
        df.append(peaks_df)

    return df


def read_peaks_to_df(mschrom: MSChromatogram) -> DataFrame:
    """Reads retention time and intensity to a DataFrame"""
    try:
        rt, intensities = mschrom.get_peaks()
    except Exception as e:
        logging.error(f"Error getting DataFrame from '{mschrom}': {e}")
        raise
    return DataFrame(
        {
            "retention_time": rt,
            "intensity": intensities,
        }
    )
