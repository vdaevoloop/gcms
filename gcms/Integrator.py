from abc import ABC, abstractmethod
import pandas as pd
import scipy
import logging


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
        for i in peaks.index:
            y = []
            for intensity in chrom["intensity"].iloc[lb.iloc[i] : rb.iloc[i] + 1]:
                y.append(intensity)
                try:
                    peaks["area"].iloc[i] = scipy.integrate.trapezoid(y)
                except Exception as e:
                    logging.error(
                        f"Error integrating peak area at peak index: {i}, intensity: {peaks["intensity"].iloc[i]}, left border: {peaks["left_border"].iloc[i]}, right border: {peaks["right_border"].iloc[i]}"
                    )
                    raise e
