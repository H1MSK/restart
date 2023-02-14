import numpy as np
import os

class ObservationCut:
    def __init__(self, cut_start, cut_end) -> None:
        self.cut_start = cut_start
        self.cut_end = cut_end

    def __call__(self, x):
        x = np.asarray(x)
        return x[..., self.cut_start:self.cut_end]

    def save(self, file):
        np.savez(file, start=self.cut_start, end=self.cut_end)

    def load(self, file):
        if os.path.exists(file):
            npzfile = np.load(file)
            self.cut_start = npzfile['cut_start']
            self.cut_end = npzfile['cut_end']
            npzfile.close()
