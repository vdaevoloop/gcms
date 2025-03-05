from gcms.readfile import GC_CSV_Reader


def main():
    r = GC_CSV_Reader()
    r.set_df_peaks(1.0)


if __name__ == "__main__":
    main()
