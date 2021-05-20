import numpy as np
from tsp import get_cost
import random
from collections import deque


def tnm_selection(pop, costs, max_tnm):  # tournament selection
    selection_ix = np.random.randint(len(pop))  # [0, len(pop)-1]
    for _ in np.random.randint(0, len(pop), max_tnm - 1):  # [0, len(pop)-1]
        # check if better (e.g. perform a tournament)
        if costs[_] < costs[selection_ix]:
            selection_ix = _
    return pop[selection_ix]


def rw_selection(pop, costs, _):  # roulette-wheel selection
    costs = [max(costs) - x for x in costs]  # avoid negative scores
    sum_score = sum(costs)
    return pop[np.random.choice(len(pop), p=[x / sum_score for x in costs])]
    # # naive implementation
    # sum_score = sum(scores)
    # pick = random.uniform(0, sum_score)  # [low, high)
    # current = 0
    # for i in range(len(pop)):
    #     current += scores[i]
    #     if current > pick:
    #         return pop[i]


def elt_selection(pop, costs, _):  # elitism
    return pop[np.argmin(costs)]


def crossover(p_1, p_2, r_cross):
    """
    order 1 crossover / OX / order crossover
    :param p_1: parent 1
    :param p_2: parent 2
    :param r_cross: rate of crossover
    """
    if random.random() < r_cross:
        c1, c2 = p_1.copy(), p_2.copy()
        pt_1 = random.randint(0, len(p_1)-1)
        pt_2 = random.randint(0, len(p_2)-1)
        while pt_1 == pt_2:
            pt_2 = random.randint(0, len(p_2)-1)  # let pt_1 != pt_2
        pt_1, pt_2 = (pt_1, pt_2) if pt_1 < pt_2 else(pt_2, pt_1)  # let pt_1 < pt_2
        for _ in range(pt_2 - pt_1):
            c1.remove(p_2[pt_1 + _])
            c2.remove(p_1[pt_1 + _])
        return [c1[:pt_1] + p_2[pt_1:pt_2] + c1[pt_1:], c2[:pt_1] + p_1[pt_1:pt_2] + c2[pt_1:]]
    else:
        return [p_1, p_2]


def mutation(p, r_mut):
    """
    center inverse mutation / CIM
    :param p: parent
    :param r_mut: rate of mutation
    """
    if random.random() < r_mut:
        pt = random.randint(0, len(p)-1)
        return p[:pt][::-1] + p[pt:][::-1]
    else:
        return p


def ga(n, adj_mat, n_pop, r_cross, r_mut, selection_md, max_tnm, term_count):
    pop = [random.sample(range(n), n) for _ in range(n_pop)]
    best_sol, best_cost = pop[0], get_cost(n, adj_mat, pop[0])  # randomly initialize best!
    data = {'cost': deque([]), 'best_cost': deque([])}  # cost means avg_cost
    count = 0
    # select parents
    if selection_md == 'tnm':
        selection_fnc = tnm_selection
    elif selection_md == 'rw':
        selection_fnc = rw_selection
    elif selection_md == 'elt':
        selection_fnc = elt_selection
    else:
        assert 0, 'unknown selection function'
    while True:
        costs = [get_cost(n, adj_mat, _) for _ in pop]
        last_best_cost = best_cost
        for i in range(n_pop):
            if costs[i] < best_cost:
                best_sol, best_cost = pop[i], costs[i]
        if last_best_cost == best_cost:  # best_cost not change
            count += 1
        else:  # best_cost change
            count = 0
        data['cost'].append(np.mean(costs))
        data['best_cost'].append(best_cost)
        if count > term_count:
            return best_sol, best_cost, data
        selected = [selection_fnc(pop, costs, max_tnm=max_tnm) for _ in range(n_pop)]
        # create the next generation
        children = list()
        for i in range(0, n_pop, 2):
            p1, p2 = selected[i], selected[i+1]  # get selected parents in pairs
            for c in crossover(p1, p2, r_cross):  # crossover and mutation
                children.append(mutation(c, r_mut))  # store for next generation
        pop = children  # replace population
