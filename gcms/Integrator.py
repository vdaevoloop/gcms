from abc import ABC, abstractmethod
import pandas as pd
import scipy
import logging
from icecream import ic


class ChromIntegrator(ABC):
    """Interface for peak area integrator"""

    @abstractmethod
    def integrate(self, chrom: pd.Series | pd.DataFrame, peaks: pd.DataFrame):
        """Integrates the area between left and right borders of a peak
        Args:
            chrom: Chromatogram data as a pandas Series or DataFrame. Must include column 'intensity'
            peaks: Peaks data ad Series or DataFrame. Must include peak borders

        Returns:
            None. Integrals are added to peaks object.

        Raises:
            ValueError: If peak borders are not included.
                        If intensity is not included in chrom.
        """
        pass

    def norm_area(self, peaks: pd.DataFrame) -> None:
        """Noramlize peak areas relative to max peak area"""
        if "area" not in peaks.columns:
            raise ValueError(
                "Error normalizing peak areas. Areas not in peaks DataFrame"
            )

        max_area = peaks["area"].max()
        area_norm = []
        for a in peaks["area"]:
            area_norm.append(a / max_area)
        peaks["area_norm"] = area_norm


class ChromTrapezoidIntegrator(ChromIntegrator):
    """Using trapezoid method to calculate are beneath peaks"""

    def integrate(self, chrom: pd.Series | pd.DataFrame, peaks: pd.DataFrame):
        if "intensity" not in chrom.columns:
            raise ValueError(
                "Error integrating peak area: chromatogram does not contain intensity column"
            )
        to_check = ["left_border", "right_border"]
        if not all(value in peaks.columns for value in to_check):
            raise ValueError("error integrating peak area: peak borders are missing")

        lb = peaks["left_border"]
        rb = peaks["right_border"]
        area = []
        for i in peaks.index:
            y = []
            for intensity in chrom["intensity"].iloc[
                peaks.at[i, "left_border"] : peaks.at[i, "right_border"] + 1
            ]:
                y.append(intensity)
            try:
                area.append(scipy.integrate.trapezoid(y))
            except Exception as e:
                logging.error(
                    f"Error integrating peak area at peak index: {i}, intensity: {peaks['intensity'].iloc[i]}, left border: {peaks['left_border'].iloc[i]}, right border: {peaks['right_border'].iloc[i]}"
                )
                raise e

        peaks["area"] = area
