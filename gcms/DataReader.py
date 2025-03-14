from abc import ABC, abstractmethod
import pandas as pd
import pathlib


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
    def get_supported_extensions(self) -> list[str]:
        """List of supported file extensions

        Returns:
            List of supported file extensions (e.g. [".csv", "mzML"])
        """
        pass
