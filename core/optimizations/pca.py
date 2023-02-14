from sys import argv
import numpy as np
import os

class PrincipalComponentProjection:
    def __init__(self, input_dimension: int, output_dimension: int):
        assert(input_dimension >= output_dimension)
        self.input_dimension = input_dimension
        self.output_dimension = output_dimension
        self.projection = np.eye(self.input_dimension, self.output_dimension)
        # self.weights = np.ones((self.input_dimension, )) / self.input_dimension

    def __call__(self, obs) -> np.ndarray:
        obs = np.asarray(obs)
        return np.dot(obs.T, self.projection[:, :self.output_dimension])

    def load(self, file):
        if os.path.exists(file):
            npzfile = np.load(file)
            self.projection = npzfile['p']
            npzfile.close()
        assert(self.input_dimension == self.projection.shape[0] and
               self.output_dimension <= self.projection.shape[1])

    def save(self, file):
        np.savez(file, p = self.projection)

    def from_samples(self, sample_data: np.ndarray, center=True):
        assert(sample_data.shape[1] == self.input_dimension)
        if center:
            sample_data -= sample_data.mean(axis=0)
        cov_mat = 1/(len(sample_data)-1) * np.matmul(sample_data.T, sample_data)
        eigen_values, eigen_vectors = np.linalg.eig(cov_mat)
        assert(abs(eigen_vectors.imag).max() < 1e-5)
        sorted_indexes = np.argsort(eigen_values)[::-1]

        # Use .copy() to unref local variables
        # Do not cut matrix to output_dimension to support changing the latter
        # especially when different session will use different output dimensions.
        # This way they can use a single data save
        self.projection = eigen_vectors[sorted_indexes].T.copy()
        # self.weights = eigen_values[sorted_indexes].copy()

if __name__ == '__main__':
    # Load argv[2:] as npz samples, extract projection matrix,
    # and save to argv[1]
    samples = []
    with np.load(argv[2]) as npz:
        samples.append(npz['x'])
    input_size = samples[0].shape[1]

    for file in argv[3:]:
        with np.load(file) as npz:
            s = npz['x']
            assert(s.shape[1] == input_size)
            samples.append(s)

    samples = np.concatenate(samples, axis=0)
    pcp = PrincipalComponentProjection(input_size, input_size)
    pcp.from_samples(samples)
    pcp.save(argv[1])
