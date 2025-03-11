import pyopenms as oms
import pathlib


class Exp:
    """Adapter to MSExperiment to read and write mzML files.
    Argument:
        mzml_file: Must be the absolute path to the file.

    """

    CLASS_TESTDATA= ".data/test_mzml/PS_R667_EST_3.mzML"


    def __init__(self, mzml_file: str|None =None, testdata:bool=True):
        self.exp = oms.MSExperiment()
        if mzml_file is None and testdata is True:
            self.mzml_file = pathlib.Path(CLASS_TESTDATA)


    def import_mzml(self, file) -> None:
        """Reads a mzML file into an Exp object"""
        oms.MzMLFile().load(file, self.exp)

    def extract_chrom(self) -> oms.MSChromatogram
        """Extracts a TIC (total intensity current)."""



class Chrom:
    """Adapter to MSChromatogram
    Extract a single chromatogram from a mzML file.
    Do peak-finding and peak-integration work."""

    def __init__(self, mzml_file=None) -> None:
        self.chrom = None
        self.exp = 

