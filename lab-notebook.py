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
from scipy.optimize import curve_fit


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

    return


def demo():
    p = Processor.ChromatogramProcessor()
    p.set_reader(DataReader.PyomenmsReader())
    p.read_to_df(".data/test_mzml/Ak_35_EtOH-ext_2x_recryst_Et_est_IS.mzML")
    p.filter_savgol()
    p.set_peak_finder(PeakFinder.PyopenmsChromPeakFinder())
    p.find_peaks(p.df.chromatogram)
    p.find_peak_borders()
    border_df = p.create_peak_border_df()
    dfs = (
        (p.df.chromatogram, "line"),
        (p.df.peaks, "scatter"),
        (border_df, "scatter"),
    )

    # max_area = p.df.peaks["area"].max()
    # area_norm = pd.DataFrame(
    #     {
    #         "retention_time": p.df.peaks["retention_time"],
    #         "area_normed": p.df.peaks["area"] / max_area,
    #     }
    # )
    # area_norm.to_csv("out.csv")
    # for i in p.df.peaks.index:
    #     if p.df.peaks["width"].iloc[i] == 0:
    #         ic(
    #             p.df.peaks["retention_time"].iloc[i],
    #             p.df.peaks["intensity"].iloc[max(0, i - 1)],
    #             p.df.peaks["intensity"].iloc[i],
    #             p.df.peaks["intensity"].iloc[min(i + 1, len(p.df.peaks["intensity"]))],
    #         )
    p.set_integrator(Integrator.ChromTrapezoidIntegrator())
    p.integrate_peak_area()
    p.normalize_integral()

    Processor.get_sample(p.df)
    cp.plot_any_df(dfs)
    plt.show()


def add_indices():
    a = pd.Series({"index": np.arange(100)})
    ic(len(a["index"]))
    return


def func(x, a, b, c, d, e):
    return a * x**4 + b * x**3 + c * x**2 + d * x + e


def calc_poly():
    data = {
        "rt": [
            463,
            508,
            548,
            583,
            613,
            680,
            736,
            763,
            789,
            815,
            890,
            965,
            1045,
            1153,
            1303,
            1398,
            1514,
        ],
        "intensity": [
            119000,
            223000,
            330000,
            340000,
            390000,
            480000,
            745000,
            785000,
            775000,
            730000,
            600000,
            530000,
            490000,
            398000,
            204000,
            140000,
            98000,
        ],
    }

    popt, pcov = curve_fit(func, data["rt"], data["intensity"])
    ic(popt)


if __name__ == "__main__":
    greetings()
    # testclient()
    # demo()
    calc_poly()
