from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA
from sklearn.metrics import mutual_info_score
import numpy as np

from itertools import cycle

import matplotlib.pyplot as plt

# plt.style.use('ggplot')

def load_wlc_data(prefix, num_runs = 3):
    spikes_t_arr = []
    spikes_i_arr = []
    I_arr = []
    trace_V_arr = []
    trace_t_arr = []
    for i in range(num_runs):
        spikes_t_arr.append(np.load(prefix+'spikes_t_'+str(i)+'.npy'))
        spikes_i_arr.append(np.load(prefix+'spikes_i_'+str(i)+'.npy'))
        I_arr.append(np.load(prefix+'I_'+str(i)+'.npy'))
        trace_V_arr.append(np.load(prefix+'trace_V_'+str(i)+'.npy'))
        trace_t_arr.append(np.load(prefix+'trace_t_'+str(i)+'.npy'))
    return spikes_t_arr, spikes_i_arr, I_arr, trace_V_arr, trace_t_arr

def doPCA(trace_V_arr, k = 3, n = 3):

    length = len(trace_V_arr[0][0])

    data = np.hstack(trace_V_arr)

    # svd decomposition and extract eigen-values/vectors
    pca = PCA(n_components=k)
    pca.fit(data.T)
    # wk = pca.explained_variance_
    # vk = pca.components_
    # print(wk)

    # Save the pca data into each odor/conc
    Xk = pca.transform(data.T)

    pca_arr = []
    for i in range(n):
        pca_arr.append(Xk[length*i:length*(i+1)])

    return pca_arr

def plotPCA(PCAdata, N, title, el = 30, az = 30, skip = 1, start = 50):

    #Plot PCA
    # cycol = cycle(['#f10c45','#069af3','#02590f','#ab33ff','#ff8c00','#ffd700'])
    # marker = cycle(['^','o','s','p'])


    fig = plt.figure(figsize = (10,7))
    ax = fig.gca(projection='3d')
    # c = next(cycol)
    # m = next(marker)

    # Turn off tick labels
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_zticklabels([])

    ax.grid(False)

    for j in range(len(PCAdata)):
        ax.scatter(PCAdata[j][start:,0][::skip],
                   PCAdata[j][start:,1][::skip],
                   PCAdata[j][start:,2][::skip],
                   s=10)
        # c = next(cycol)
        # m = next(marker)

    # fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    # plt.tight_layout()

    # plt.axis('off')
    plt.title(title, fontsize = 22)
    ax.view_init(elev = el, azim = az)
    ax.figure.savefig(title + '.pdf', bbox_inches = 'tight')
    # ax.figure.savefig('PCA_' + str(N) + '.png', bbox_inches = 'tight', dpi = 400)
    # plt.show()

def getMIM(trace_V_arr):
    #Information component analysis
    # length = len(trace_V_arr[0][0])
    data = np.hstack(trace_V_arr).T

    N = np.shape(data)[1]

    bins = int(np.round(np.log2(N)+1)) #Sturges' formula

    matMI = np.zeros((N, N))

    for ix in np.arange(N):
        if ix%10 == 0: print(ix)
        for jx in np.arange(ix,N):
            matMI[ix,jx] = calc_MI(data[:,ix], data[:,jx], bins)
            #symmetric matrix
            matMI[jx, ix] = matMI[ix,jx]

    np.save('MIM', matMI)

def doInCA(MIM, data, length, skip, k = 3):

    w,v = np.linalg.eig(MIM)

    vk = v[:, :k]

    # # Save the InCA data into each odor/conc
    Xk = vk.T.dot(data.T).T[::skip]

    inca1 = Xk[0:length]
    inca2 = Xk[length:2*length]
    inca3 = Xk[2*length:3*length]

    return [inca1, inca2, inca3]

def plotInCA(InCAData, N, start = 400):
    inca1, inca2, inca3 = InCAData


    # cycol = cycle(['#f10c45','#069af3','#02590f','#ab33ff','#ff8c00','#ffd700'])
    # marker = cycle(['^','o','s','p'])

    fig = plt.figure(figsize = (10,7))
    ax = fig.gca(projection='3d')
    # c = next(cycol)
    # m = next(marker)

    # Turn off tick labels
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_zticklabels([])

    ax.grid(False)

    name = [inca1, inca2, inca3]
    for j in range(3):
        ax.scatter(name[j][start:,0], name[j][start:,1], name[j][start:,2],
                   s=10)#, 
                   # color = c,
                   # marker = m)
        # c = next(cycol)
        # m = next(marker)

    plt.title('InCA ' + str(N) + ' HH neuron', fontsize = 22)
    ax.view_init(0, 0)
    # plt.tight_layout()
    ax.figure.savefig('InCA_' + str(N) + '.pdf', bbox_inches = 'tight')

def calc_MI(X, Y, bins):
    c_xy = np.histogram2d(X, Y, bins)[0]
    MI = mutual_info_score(None, None, contingency=c_xy)
    return MI

