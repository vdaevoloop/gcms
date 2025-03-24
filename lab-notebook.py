import pyopenms as oms
from icecream import ic
from pathlib import Path
import logging
import pandas as pd
import matplotlib.pyplot as plt
from pyopenms_client import PyOpenMsClient as omsc
from plotting import ChromPlotting as cp
from gcms import DataReader, Processor, PeakFinder, Integrator
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
        ".data/test_mzml/PS_R667_EST_3.mzML"
    )
    p.filter_savgol()
    p.set_peak_finder(PeakFinder.PyopenmsChromPeakFinder())
    p.find_peaks(p.df.chromatogram_og)
    p.find_peak_borders()
    p.integral()
    border_df = p.create_peak_border_df()
    dfs = (
        (p.df.chromatogram_og, "line"),
        (p.df.peaks, "scatter"),
        (border_df, "scatter"),
    )

    max_area = p.df.peaks["area"].max()
    area_norm = pd.DataFrame(
        {
            "retention_time": p.df.peaks["retention_time"],
            "area_normed": p.df.peaks["area"] / max_area,
        }
    )
    # area_norm.to_csv("out.csv")
    # for i in p.df.peaks.index:
    #     if p.df.peaks["width"].iloc[i] == 0:
    #         ic(
    #             p.df.peaks["retention_time"].iloc[i],
    #             p.df.peaks["intensity"].iloc[max(0, i - 1)],
    #             p.df.peaks["intensity"].iloc[i],
    #             p.df.peaks["intensity"].iloc[min(i + 1, len(p.df.peaks["intensity"]))],
    #         )
    # cp.plot_any_df(dfs)
    # plt.show()
    p.set_integrator(Integrator.ChromTrapezoidIntegrator())



def add_indices():
    a = pd.Series({"index": np.arange(100)})
    ic(len(a["index"]))
    return


if __name__ == "__main__":
    greetings()
    # testclient()
    demo()
