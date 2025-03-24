from abc import ABC, abstractmethod
import pandas as pd


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

        # TODO: Append all data points from left_border to right_border
        lb = peaks["left_border"]
        rb = peaks["right_border"]
        for i in peaks.index:
            y=[]
            for intens in chrom["intensity"].iloc[] 



