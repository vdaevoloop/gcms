import pyopenms as oms
from icecream import ic
from pathlib import Path
import logging
import pandas as pd
import matplotlib.pyplot as plt
from src.gcms import DataReader, Processor, PeakFinder, Integrator
from src.gcms.pyopenms_client import PyOpenMsClient as omsc
from src.gcms.plotting import ChromPlotting as cp
import numpy as np
import scipy
from scipy.optimize import curve_fit

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

    p.set_integrator(Integrator.ChromTrapezoidIntegrator())
    p.integrate_peak_area()
    p.normalize_integral()

    df = Processor.get_sample(p.df)
    popt = Processor.fit_model(df["retention_time"], df["intensity"])

    # para_df, _ = curve_fit(func_three, df["retention_time"], df["intensity"])
    # para_test, _ = curve_fit(func_three, data["rt"], data["intensity"])
    # ic(para_df)
    # ic(para_test)

    # fig, ax = plt.subplots()
    # sns.lineplot(data=data, x="rt", y="intensity")
    # sns.lineplot(data=df, x="retention_time", y="intensity")
    # plt.show()

    # cp.plot_any_df(dfs)
    # plt.show()

    data_skew = scipy.stats.skewnorm.rvs(a=4, loc=50, scale=15, size=200)
    ic(data_skew)


def add_indices():
    a = pd.Series({"index": np.arange(100)})
    ic(len(a["index"]))
    return


def func(x, a, b, c, d, e):
    return a * x**4 + b * x**3 + c * x**2 + d * x + e


def func_three(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d


def func_quad(x, a, b, c):
    return a * x**2 + b * x + c


def func_five(x, a1, a2, a3, a4, a5, a6):
    return a1 * x**5 + a2 * x**4 + a3 * x**3 + a4 * x**2 + a5 * x + a6


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


if __name__ == "__main__":
    greetings()
    # testclient()
    demo()
    calc_poly()
