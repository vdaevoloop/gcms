import pyopenms as oms
from icecream import ic
from pathlib import Path
import logging
import pandas as pd
import matplotlib.pyplot as plt
from pyopenms_client import PyOpenMsClient as omsc
from plotting import ChromPlotting as cp
from gcms import DataReader, Processor, PeakFinder
import numpy as np


def greetings():
    print("Hello from the lab notebook")


def first_look_at_data():
    testfile = Path(".data/test_mzml/PS_R667_EST_3.mzML")
    exp = oms.MSExperiment()
    oms.MzMLFile().load(str(testfile), exp)
    lchroms = exp.getChromatograms()
    if len(lchroms) != 1:
        logging.error("More than 1 chromatogram")
        return
    chrom = lchroms[0]

    retention_times = []
    intensities = []

    size = chrom.size()

    for i in range(size):
        ip = chrom[i]
        rt, intensity = ip.getRT(), ip.getIntensity()
        retention_times.append(rt)
        intensities.append(intensity)

    df = pd.DataFrame({"retention_time": retention_times, "intensity": intensities})
    print(df)
    return


def testclient():
    chrom1 = omsc.Chrom()
    chrom1.find_peaks()
    exp = omsc.export_df(chrom1.chrom, chrom1.picked_peaks)
    chrom_df = exp[0]
    peaks_df = exp[1]
    dfs = (
        (chrom_df, "line"),
        (peaks_df, "scatter"),
    )

    cp.plot_any_df(dfs, x="index")
    plt.show()

    # for i, peak in enumerate(chrom1.picked_peaks):
    #     if i == 1:
    #         ic(peak)

    return


def demo():
    p = Processor.ChromatogramProcessor()
    p.set_reader(DataReader.PyomenmsReader())
    p.read_to_df(
        "/Users/duc/Developer/aevoloop/gcms/.data/test_mzml/PS_R667_EST_3.mzML"
    )
    p.set_peak_finder(PeakFinder.PyopenmsChromPeakFinder())
    p.find_peaks(p.df.chromatogram_og)
    p.find_peak_borders()
    border_df = p.create_peak_border_df()
    dfs = (
        (p.df.chromatogram_og, "line"),
        (p.df.peaks, "scatter"),
        (border_df, "scatter"),
    )
    # cp.plot_any_df(dfs)
    # plt.show()
    ic(p.df.chromatogram_og)
    ic(p.df.peaks)
    ic(border_df)

    ic(p.df.chromatogram_og.iloc[42])
    ic(p.df.chromatogram_og.iloc[43])
    ic(p.df.chromatogram_og.iloc[44])
    ic(p.df.chromatogram_og.iloc[45])
    ic(p.df.chromatogram_og.iloc[46])
    ic(p.df.chromatogram_og.iloc[47])


def add_indices():
    a = pd.Series({"index": np.arange(100)})
    ic(len(a["index"]))
    return


if __name__ == "__main__":
    greetings()
    # testclient()
    demo()
