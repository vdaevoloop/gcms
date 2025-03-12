import pyopenms as oms
from icecream import ic
from pathlib import Path
import logging
import pandas as pd
from pyopenms_client import PyOpenMsClient as omsc


def main():
    print("Hello from gcms!")


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

    chrom1.apply_pickChromatogram()
    chrom1.plot(chrom1.picker_chrom)
    return


if __name__ == "__main__":
    main()
    testclient()
