from gcms import DataReader


class ChromatogramProcessor:
    """Main class that handles the data processing including data import, peak finder, peak area integration.

    Fields:
        reader: Data reader of type DataReader.ChromDataReader
        peak_finder: Peak finder of type PeakFinder.ChromPeakFinder
        filter: Filter of type Processor.ChromFilter
        integrator: Integrator calculates peak area of type Processor.ChromIntegrator
    """

    def __init__(self) -> None:
        self.reader = None
        self.peak_finder = None
        self.filter = None
        self.integrator = None
        return

    def set_reader(self, reader: DataReader.ChromDataReader) -> None:
        self.reader = reader
        return


class ChromatogramDF:
    """Data class to hold DataFrames of original chromatogram, filtered chrom, peaks with borders, peak_area
    Fields:
        chromatogram_og: original data as a pd.DataFrame[['index', 'retention_rate', 'intensity']]
        chromatogram_filtered: filtered chromatogram as pd.DataFrame[['index', 'retention_rate', 'intensity']]
        peaks: peaks of a chromatogram as pd.DataFrame[['index', 'retention_rate', 'intensity', 'left_border', 'right_border', 'area']]
        count_filter_iterations: Number of timex how often a filter was applied to chromatogram_filtered
    """

    def __init__(self) -> None:
        self.chromatogram_og = None
        self.chromatogram_filtered = None
        self.peaks = None
        self.count_filter_iterations = 0
