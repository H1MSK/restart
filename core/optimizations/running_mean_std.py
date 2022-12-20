import os
import numpy as np

class RunningMeanStd:
    # Dynamically calculate mean and std
    def __init__(self, shape):  # shape:the dimension of input data
        self.n = 0
        self.mean = np.zeros(shape)
        self.S = np.zeros(shape)
        self.std = np.zeros(shape)

    def update(self, x):
        x = np.asarray(x)
        self.n += 1
        if self.n == 1:
            self.mean = x
            self.std = x
        else:
            old_mean = self.mean.copy()
            self.mean = old_mean + (x - old_mean) / self.n
            self.S = self.S + (x - old_mean) * (x - self.mean)
            self.std = np.sqrt(self.S / (self.n - 1))

    def load(self, file):
        if os.path.exists(file):
            npzfile = np.load(file)
            self.n = npzfile['n']
            self.mean = npzfile['mean']
            self.S = npzfile['S']
            self.std = npzfile['std']
            npzfile.close()

    def save(self, file):
        np.savez(file, n=self.n, mean=self.mean, S=self.S, std=self.std)
