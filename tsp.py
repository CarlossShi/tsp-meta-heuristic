def get_cost(n, adj_mat, sol):
    """
    :param n: number of vertices, e.g. 2
    :param adj_mat: adjacency matrix, e.g. [[0,1], [1,0]]
    :param sol: solution, e.g. [1,0]
    """
    return sum([adj_mat[sol[_]][sol[(_ + 1) % n]] for _ in range(n)])


def get_delta_swap(n, adj_mat, sol, i, j):
    # bef: [..., i-1, i, i+1, ..., j-1, j, j+1] / [...,i-1, i, j, j+1, ...]
    # aft: [..., i-1, j, i+1, ..., j-1, i, j+1] / [...,i-1, j, i, j+1, ...]
    # the latter case, 2 * adj_mat(i, j) is extra deducted!
    delta = adj_mat[sol[i - 1]][sol[j]] + adj_mat[sol[j]][sol[(i + 1) % n]] + \
            adj_mat[sol[j - 1]][sol[i]] + adj_mat[sol[i]][sol[(j + 1) % n]] - \
            adj_mat[sol[i - 1]][sol[i]] - adj_mat[sol[i]][sol[(i + 1) % n]] - \
            adj_mat[sol[j - 1]][sol[j]] - adj_mat[sol[j]][sol[(j + 1) % n]]
    if j - i == 1 or i == 0 and j == n - 1:
        delta += 2 * adj_mat[sol[i]][sol[j]]  # symmetrical TSP
    return delta


def get_new_sol_swap(sol, i, j):
    new_sol = sol.copy()
    new_sol[i], new_sol[j] = new_sol[j], new_sol[i]
    return new_sol


def get_delta_2opt(n, adj_mat, sol, i, j):
    # bef: [..., i-1, i, i+1, ..., j-1, j, j+1] / [...,i-1, i, j, j+1, ...] / [i, i+1, ..., j-1, j]
    # aft: [..., i-1, j, j-1, ..., i+1, i, j+1] / [...,i-1, j, i, j+1, ...] / [j, i+1, ..., j-1, i]
    # the latter case, 2 * adj_mat(i, j) is extra deducted!
    delta = adj_mat[sol[i - 1]][sol[j]] + adj_mat[sol[i]][sol[(j + 1) % n]] - \
            adj_mat[sol[i - 1]][sol[i]] - adj_mat[sol[j]][sol[(j + 1) % n]]
    if i == 0 and j == n - 1:  # the first two value == 0, while others < 0
        delta = 0
    return delta


def get_new_sol_2opt(sol, i, j):
    new_sol = sol.copy()
    new_sol[i:j+1] = new_sol[i:j+1][::-1]  # notice index + 1 !
    return new_sol
