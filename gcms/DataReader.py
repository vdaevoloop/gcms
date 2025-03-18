from abc import ABC, abstractmethod
import pandas as pd
import pathlib
from pyopenms_client import PyOpenMsClient as omsc


class ChromDataReader(ABC):
    """Interface for data importers that handle different chromatogram files"""

    @abstractmethod
    def is_compatible(self, file_path: str | pathlib.Path) -> bool:
        """Determine if this importer is is_compatible with the file type.

        Args:
            file_path: Path to the file

        Returns:
            True if importer can handle, False otherwise
        """
        pass

    @abstractmethod
    def read_data(self, file_path: str | pathlib.Path) -> pd.DataFrame:
        """Read data from specific file
        Args:
            file_path: Path to file

        Returns:
            pandas.DataFrame with columns 'index', 'retention_time', 'intensity'

        Raises:
            ValuesError: If the file cannot be importer
            FileNotFoundError: If file does not exist
        """
        pass

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """List of supported file extensions

        Returns:
            List of supported file extensions (e.g. [".csv", "mzML"])
        """
        pass


class PyomenmsReader(ChromDataReader):
    """Reads data from a mzML file using the PyOpenMS library."""

    def is_compatible(self, file_path: str | pathlib.Path) -> bool:
        path = pathlib.Path(file_path)
        return path.suffix.lower() in self.supported_extensions

    def read_data(self, file_path: str | pathlib.Path) -> pd.DataFrame:
        if not self.is_compatible(file_path):
            raise ValueError(
                f"file '{file_path} is not compatible with reader '{self.__class__}'"
            )
        chrom = omsc.Chrom(pathlib.Path(file_path))
        return omsc.export_df(chrom.chrom)

    @property
    def supported_extensions(self) -> list[str]:
        return [".mzml"]
