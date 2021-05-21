import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.animation as animation
import numpy as np
from pprint import pprint
import time
import math
from tqdm import tqdm

from tsp import *
import tb
import ga
import sa


# load data

pos = [[float(x) for x in s.split()[1:]] for s in open('data/dj38.txt').readlines()]
n = len(pos)


# calculate adjacency matrix

adj_mat = np.zeros([n, n])
for i in range(n):
    for j in range(i, n):
        adj_mat[i][j] = adj_mat[j][i] = np.linalg.norm(np.subtract(pos[i], pos[j]))


# initialization

opt_cost = 6659.439330623091  # get result from tsp_gurobi.py
num_tests = 100  # number of iid tests
result = {'best_sol': [], 'best_cost': math.inf, 'best_gap': math.inf,
          'cost': [0] * num_tests, 'time': [0] * num_tests,
          'avg_cost': math.inf, 'avg_gap': math.inf, 'cost_std': math.inf,
          'avg_time': math.inf, 'time_std': math.inf}
best_cost = math.inf
best_sol = []
data = {}


# set method

method = 'ts'  # tabu search
# method = 'ga'  # genetic algorithm
# method = 'sa'  # simulated annealing


# set mutation method

# mut_md = [get_new_sol_swap, get_delta_swap]
mut_md = [get_new_sol_2opt, get_delta_2opt]


# run and visualization

method_name = ''
for _ in tqdm(range(num_tests)):
    start = time.time()
    if method == 'ts':
        method_name = 'Tabu Search'
        best_sol, best_cost, data = tb.tb(n, adj_mat,
                                          tb_size=20,  # tabu solutions in tb_list
                                          max_tnm=100,  # how many candidates picked in tournament selection
                                          mut_md=mut_md,  # [get_sol, get delta], method of mutation, e.g. swap, 2-opt
                                          term_count=200  # terminate threshold if best_cost nor change
                                          )
    elif method == 'ga':
        method_name = 'Genetic Algorithm'
        best_sol, best_cost, data = ga.ga(n, adj_mat,
                                          n_pop=200,
                                          r_cross=0.5,
                                          r_mut=0.8,
                                          selection_md='tnm',  # 'rw' / 'tnm' / 'elt'
                                          max_tnm=3,
                                          term_count=200
                                          )
    elif method == 'sa':
        method_name = 'Simulated Annealing'
        best_sol, best_cost, data = sa.sa(n, adj_mat,
                                          tb_size=0,  # tabu solutions in tb_list
                                          max_tnm=20,  # how many candidates picked in tournament selection
                                          mut_md=mut_md,  # [get_sol, get delta], method of mutation, e.g. swap, 2-opt
                                          term_count_1=25,  # inner loop termination flag
                                          term_count_2=25,  # outer loop termination flag
                                          t_0=1200,  # starting temperature, calculated by init_temp.py
                                          alpha=0.9  # cooling parameter
                                          )
    else:
        assert 0, 'unknown method'
    end = time.time()
    result['time'][_] = end - start
    result['cost'][_] = best_cost
    if best_cost < result['best_cost']:
        result['best_sol'] = best_sol
        result['best_cost'] = best_cost
        result['best_gap'] = best_cost / opt_cost - 1
    plt.plot(range(len(data['cost'])), data['cost'], color='b', alpha=math.pow(num_tests, -0.75))
    plt.plot(range(len(data['cost'])), data['best_cost'], color='r', alpha=math.pow(num_tests, -0.75))


plt.title('Solving TSP with {}'.format(method_name))
plt.xlabel('Number of Iteration')
plt.ylabel('Cost')
plt.savefig('results/{}.png'.format(method))

# print results
result['avg_cost'] = np.mean(result['cost'])
result['avg_gap'] = result['avg_cost'] / opt_cost - 1
result['cost_std'] = np.std(result['cost'])
result['avg_time'] = np.mean(result['time'])
result['time_std'] = np.std(result['time'])
pprint(result)


# SA visualization
# https://matplotlib.org/stable/gallery/animation/dynamic_image.html
# https://stackoverflow.com/questions/49158604/matplotlib-animation-update-title-using-artistanimation
# https://stackoverflow.com/questions/17895698/updating-the-x-axis-values-using-matplotlib-animation
if num_tests == 1 and method == 'simulated annealing':
    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    plt.subplots_adjust(wspace=0.3)  # more interval between two axes

    xlim = [np.min(pos, 0)[0], np.max(pos, 0)[0]]
    ylim = [np.min(pos, 0)[1], np.max(pos, 0)[1]]
    ax[0].set(xlabel='X Axis', ylabel='Y Axis',
              xlim=xlim, ylim=ylim,
              title='Current and Optimal Tours')
    ax[1].set(xlabel='Number of Iteration', ylabel='Tour Length',
              title='Convergence Curve')
    ims = []
    for i in range(len(data['sol'])):
        im = []
        sol = data['sol'][i]
        best_sol = data['best_sol'][i]
        cost = list(data['cost'])[:i]
        best_cost = list(data['best_cost'])[:i]

        if i > 2 and cost[-1] == cost[-2]:
            continue

        # https://matplotlib.org/stable/gallery/shapes_and_collections/line_collection.html
        lines = [[pos[sol[_]], pos[sol[(_ + 1) % n]]] for _ in range(n)]
        line_segments = LineCollection(lines, color='b')
        im.append(ax[0].add_collection(line_segments))
        lines = [[pos[best_sol[_]], pos[best_sol[(_ + 1) % n]]] for _ in range(n)]
        line_segments = LineCollection(lines, color='r', alpha=0.5, linewidth=2)
        im.append(ax[0].add_collection(line_segments))

        # # plot directed tour, too slow
        # # https://stackoverflow.com/questions/46506375/creating-graphics-for-euclidean-instances-of-tsp
        # for j in range(n):
        #     start_pos = pos[sol[j]]
        #     end_pos = pos[sol[(j + 1) % n]]
        #     im.append(ax[0].annotate("",
        #                  xy=start_pos, xycoords='data',
        #                  xytext=end_pos, textcoords='data',
        #                  arrowprops=dict(arrowstyle='->',
        #                                  connectionstyle='arc3',
        #                                  alpha=1,
        #                                  color='b')))
        # for j in range(n):
        #     start_pos = pos[best_sol[j]]
        #     end_pos = pos[best_sol[(j + 1) % n]]
        #     im.append(ax[0].annotate("",
        #                  xy=start_pos, xycoords='data',
        #                  xytext=end_pos, textcoords='data',
        #                  arrowprops=dict(arrowstyle='->',
        #                                  connectionstyle='arc3',
        #                                  lw=2,
        #                                  alpha=0.5,
        #                                  color='r')))

        line1, = ax[1].plot(range(len(cost)), cost, color='b')
        line2, = ax[1].plot(range(len(best_cost)), best_cost, color='r')
        im.append(line1)
        im.append(line2)
        ims.append(im)

    ani = animation.ArtistAnimation(fig, ims, interval=10, blit=True,
                                    repeat_delay=1000)
    ani.save('results/sa.mp4')
