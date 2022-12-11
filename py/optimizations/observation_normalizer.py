from .running_mean_std import RunningMeanStd

class ObservationNormalizer:
    def __init__(self, shape, update_normalizer=True):
        self.running_ms = RunningMeanStd(shape=shape)
        self.update_normalizer=update_normalizer

    def __call__(self, x):
        # Whether to update the mean and std,during the evaluating,update=Flase
        if self.update_normalizer:  
            self.running_ms.update(x)
        x = (x - self.running_ms.mean) / (self.running_ms.std + 1e-8)

        return x

    def save(self, file):
        return self.running_ms.save(file)

    def load(self, file):
        return self.running_ms.load(file)
