# Copyright (C) 2022 Sunnybrook Research Institute
# This file is part of src <https://github.com/DWALab/Phindr3D>.
#
# src is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# src is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with src.  If not, see <http://www.gnu.org/licenses/>.
from .Clustering_Functions import *
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA, KernelPCA
from sklearn.preprocessing import StandardScaler

class Clustering:

    def plot_type(X, dim, plot):

        if plot=="PCA":
            func='linear'
            sc = StandardScaler()
            X_show = sc.fit_transform(X)
            pca = KernelPCA(n_components=dim, kernel=func)
            P = pca.fit(X_show).transform(X_show)
            return('PCA plot', 'PCA 1', 'PCA 2', P)
        elif plot =="t-SNE":
            T = TSNE(n_components=dim, init='pca', learning_rate='auto').fit_transform(X)
            return('t-SNE plot', 't-SNE 1', 't-SNE 2', T)
        elif plot =="Sammon":
            S, E = sammon(X, dim)
            return('Sammon plot', 'Sammon 1', 'Sammon 2', S)
        else:
            raise Exception("Invalid plot")

    def clusterest(X):
        eps = np.finfo(np.float64).eps
        realmin = np.finfo(np.float64).tiny
        realmax = np.finfo(np.float64).max
        estimateNumClusters(X, eps, realmin, realmax)

# end class ClusterStuff
if __name__ == '__main__':
    """Not sure what this will do yet"""

    pass





# end main