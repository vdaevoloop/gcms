import pyopenms as oms


class Exp:
    def __init__(self):
        self.exp = oms.MSExperiment()
        self.Chromato = None

    def import_mzml(self, file):
        oms.MzMLFile().load(file, self.exp)
