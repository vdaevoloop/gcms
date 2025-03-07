from gcms.readfile import GC_CSV_Reader


def main():
    r = GC_CSV_Reader()
    r.set_savgol_df()
    r.set_df_peaks()


if __name__ == "__main__":
    main()
