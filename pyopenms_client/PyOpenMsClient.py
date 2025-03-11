import pyopenms as oms
import logging
import pathlib


class Exp:
    """Adapter to MSExperiment to read and write mzML files.
    Argument:
        mzml_file: Must be the absolute path to the file.
    """

    TESTDATA = ".data/test_mzml/PS_R667_EST_3.mzML"

    def __init__(
        self, mzml_file: str | None = None, testdata: bool = True, selfinit: bool = True
    ) -> None:
        self.exp = oms.MSExperiment()

        if mzml_file is None and testdata is True:
            try:
                self.mzml_file = pathlib.Path(TESTDATA)
            except Exception as e:
                raise ValueError(f"Error reading path '{TESTDATA}': {e}")
        elif mzml_file is None and testdata is False:
            self.mzml_file = None
        else:
            self.mzml_file = mzml_file

        if self.mzml_file is not None and selfinit is True:
            self.set_dataset(str(self.mzml_file))

        return

    def set_dataset(self, file: str) -> None:
        """Reads a mzML file into an Exp object"""
        try:
            oms.MzMLFile().load(file, self.exp)
        except Exception as e:
            raise FileNotFoundError(f"Error while importing mzML file '{file}': {e}")

    def extract_chrom(self) -> oms.MSChromatogram | None:
        """Extracts a TIC (total intensity current)."""
        if self.exp.getNrChromatograms() != 1:
            logging.error(
                f"Number of chromatograms contained in mzML file: {self.exp.getNrChromatograms()}"
            )
            return None

        # TODO:
        return oms.MSChromatogram()


class Chrom:
    """Adapter to MSChromatogram
    Extract a single chromatogram from a mzML file.
    Do peak-finding and peak-integration work."""

    def __init__(self, mzml_file: str | None = None) -> None:
        self.chrom = None
