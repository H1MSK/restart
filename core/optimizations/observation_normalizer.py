from .running_mean_std import RunningMeanStd
import numpy as np

class ObservationNormalizer:
    def __init__(self, shape, update_normalizer=True):
        self.running_ms = RunningMeanStd(shape=shape)
        self.update_normalizer=update_normalizer

    def __call__(self, x):
        x = np.asarray(x)
        # Whether to update the mean and std.
        # During evaluation,update=Flase
        if self.update_normalizer:  
            self.running_ms.update(x)
        x = (x - self.running_ms.mean) / (self.running_ms.std + 1e-8)

        x = np.clip(x, -5, +5)

        return x

    def save(self, file):
        return self.running_ms.save(file)

    def load(self, file):
        return self.running_ms.load(file)

class RecordedObservationNormalizer(ObservationNormalizer):
    def __init__(self, shape, update_normalizer=True):
        super().__init__(shape, update_normalizer)
        self.blk = np.zeros((524288, shape[0]))
        self.cnt = 0
        self.file_cnt = 0

    def __call__(self, x):
        self.blk[self.cnt] = x
        self.cnt += 1
        if self.cnt == self.blk.shape[0]:
            np.savez_compressed(f"obs.sav.{self.file_cnt}", x=self.blk)
            self.blk = np.zeros(self.blk.shape)
            self.cnt = 0
            self.file_cnt += 1
        if self.cnt % 32768 == 0:
            print(f"#{self.file_cnt}: {self.cnt} data")

        return super().__call__(x)
