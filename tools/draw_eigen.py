from sys import argv
import numpy as np
from matplotlib import pyplot

def draw_eigen(data: np.ndarray, center=True):
    """Draw eigen diagram

    Args:
        data (np.ndarray): (n, m) matrix of data, with n representing count and m representing feature dimensions
        center (bool, optional): Whether to center the given data. Defaults to True.
    """
    if center:
        data -= data.mean(axis=0)
    covMat = np.matmul(data.T, data)
    eigenValues, eigenVectors = np.linalg.eig(covMat)
    sortedIndexes = np.argsort(eigenValues)[::-1]
    assert(abs(eigenValues.imag).max() < 1e-6)
    sortedValues = eigenValues[sortedIndexes].real
    cumSum = np.cumsum(sortedValues)
    indicies = np.arange(len(sortedValues))
    ax1 = pyplot.subplot(1, 2, 1)
    for i, n in enumerate(cumSum/cumSum[-1]):
        print(f"{i}: {n}")
    # ax1.set_yscale('log')
    pyplot.plot(indicies, sortedValues / cumSum[-1])
    pyplot.subplot(1, 2, 2, sharey=ax1)
    pyplot.plot(indicies, cumSum / cumSum[-1])
    pyplot.show()

if __name__ == '__main__':
    f = np.load(argv[1])
    x = f['x']
    draw_eigen(x)
