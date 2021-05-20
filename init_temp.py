# https://link.springer.com/article/10.1023/B:COAP.0000044187.23143.bd

import random
from tsp import *
import math
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

def init_temp(n, adj_mat, mut_md, s, chi_0, t_1, p, epsilon):
    get_new_sol = mut_md[0]
    get_delta = mut_md[1]
    pop = [random.sample(range(n), n) for _ in range(s)]
    e_max = [get_cost(n, adj_mat, _) for _ in pop]
    e_min = [0] * s
    for _ in range(s):
        while True:
            i, j = random.sample(range(n), 2)  # randomly select two indexes
            i, j = (i, j) if i < j else (j, i)  # let i < j
            delta = get_delta(n, adj_mat, pop[_], i, j)
            if delta < 0:
                break
        e_min[_] = e_max[_] + delta
    t = t_1
    while True:
        chi = sum([math.exp(-_ / t) for _ in e_max]) / sum([math.exp(-_ / t) for _ in e_min])
        if abs(chi - chi_0) < epsilon:
            return t
        else:
            t = t * math.pow(math.log(chi) / math.log(chi_0), 1/p)

pos = [[float(x) for x in s.split()[1:]] for s in open('data/dj38.txt').readlines()]

n = len(pos)
# calculate adjacency matrix
adj_mat = np.zeros([n, n])
for i in range(n):
    for j in range(i, n):
        adj_mat[i][j] = adj_mat[j][i] = np.linalg.norm(np.subtract(pos[i], pos[j]))

t_list = []
try:
    for _ in tqdm(range(100)):
        t_list.append(init_temp(n, adj_mat, [get_new_sol_2opt, get_delta_2opt], 2500, 0.7, 100, 2, 1e-5))
except:
    pass

print(min(t_list), max(t_list))
print(np.mean(t_list))
plt.plot(t_list)
plt.show()
