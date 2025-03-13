import pyopenms as oms
from icecream import ic
from pathlib import Path
import logging
import pandas as pd
import matplotlib.pyplot as plt
from pyopenms_client import PyOpenMsClient as omsc
from plotting import ChromPlotting as cp


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
    dfs = (omsc.get_df(chrom1.chrom), omsc.get_df(chrom1.picked_peaks))

    cp.plot_any_scatter(dfs)
    plt.show()

    # for i, peak in enumerate(chrom1.picked_peaks):
    #     if i == 1:
    #         ic(peak)

    return


if __name__ == "__main__":
    greetings()
    testclient()
