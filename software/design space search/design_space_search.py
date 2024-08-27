# design_space_search, program for design space exploration of 2-share 
# Keccak-f[1600].
# Copyright (C) 2024, Cankun Zhao, Leibo Liu. All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTERS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT INCLUDING NEGLIGENCE OR OTHERWISE ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Please see LICENSE and README for license and further instructions.
#
# Contact: zhaock97@gmail.com

from tqdm import tqdm
import multiprocessing
from copy import deepcopy
import json

n_cores = 10

W = 64
RHO_OFFSET = [[0,  36,   3, 105, 210],
              [1, 300,  10,  45,  66],
              [190,   6, 171,  15, 253],
              [28,  55, 153,  21, 120],
              [91, 276, 231, 136,  78]]

# glitch_list_gen

def chi_before_reg(state_array, state_in, config):
    PXT, PX0, PX1, PX0I, PX1I, X0, X1, OFF = config
    # PXT: Protect X-coordinate Theta, x-coordinate of theta input used as
    #      randomness
    # PX0: Protect X-coordinate no.0, first chi input protected by COTG
    # PX1: Protect X-coordinate no.1, second chi input protected by COTG
    # PX0I: Protect X-coordinate no.0 xored with Inner-domain products (=1) or
    #       cross-domain products (=0)
    # PX1I: Protect X-coordinate no.1 xored with Inner-domain products (=1) or
    #       cross-domain products (=0)
    # X0: X-coordinate no.0 of chi input used as randomness (COTG)
    # X1: X-coordinate no.1 of chi input used as randomness (COTG)
    # OFF: OFFset of COTG
    A = deepcopy(state_array)
    I = deepcopy(state_in)
    # DOM-based 1st-order chi
    state_array = [[[[
        A[(x + 1) % 5][y][z][0] + A[(x + 2) % 5][y][z][0],
        A[x][y][z][0] + A[(x + 1) % 5][y][z][0] + A[(x + 2) % 5][y][z][1],
        A[x][y][z][1] + A[(x + 1) % 5][y][z][1] + A[(x + 2) % 5][y][z][0],
        A[(x + 1) % 5][y][z][1] + A[(x + 2) % 5][y][z][1]] for z in range(W)]
                                                           for y in range(5)]
                                                           for x in range(5)]
    # Additional parts to be designed
    for y in range(5):
        for z in range(W):
            # Changing Of The Guard (COTG)
            j = W * y + z
            if (j > 0):
                jj = (j - OFF) % (5 * W)
                yy = jj // W
                zz = jj % W
                state_array[PX0][y][z][1 ^ PX0I] += A[X0][yy][zz][0]
                state_array[PX0][y][z][2 ^ PX0I] += A[X0][yy][zz][0]
                state_array[PX1][y][z][1 ^ PX1I] += A[X1][yy][zz][0]
                state_array[PX1][y][z][2 ^ PX1I] += A[X1][yy][zz][0]
            # Use theta inputs as pseudo-randomness
            state_array[PXT][y][z][0] += I[PXT][y][z][0]
            state_array[PXT][y][z][1] += I[PXT][y][z][0]
            state_array[PXT][y][z][2] += I[PXT][y][z][1]
            state_array[PXT][y][z][3] += I[PXT][y][z][1]
    return state_array


def init_state():
    return [[[[[(x, y, z, share)] for share in range(2)]
                                  for z in range(W)]
                                  for y in range(5)]
                                  for x in range(5)]


def theta(state_array):
    A = deepcopy(state_array)
    C = [[[A[x][0][z][s] + A[x][1][z][s] + A[x][2][z][s]
                         + A[x][3][z][s] + A[x][4][z][s] for s in range(2)]
                                                         for z in range(W)]
                                                         for x in range(5)]
    D = [[[C[(x - 1) % 5][z][s] + C[(x + 1) % 5][(z - 1) % W][s]
                                                         for s in range(2)]
                                                         for z in range(W)]
                                                         for x in range(5)]
    return [[[[A[x][y][z][s] + D[x][z][s] for s in range(2)]
                                          for z in range(W)]
                                          for y in range(5)]
                                          for x in range(5)]


def rho(state_array):
    A = deepcopy(state_array)
    return [[[[A[x][y][(z - RHO_OFFSET[x][y]) % W][s] for s in range(2)]
                                                      for z in range(W)]
                                                      for y in range(5)]
                                                      for x in range(5)]


def pi(state_array):
    A = deepcopy(state_array)
    return [[[[A[(x + 3 * y) % 5][x][z][s] for s in range(2)]
                                           for z in range(W)]
                                           for y in range(5)]
                                           for x in range(5)]


def glitch_list_gen(config, file_name=None):
    state_array = init_state()
    state_in = init_state()
    state_array = theta(state_array)
    state_array = rho(state_array)
    state_in = rho(state_in)
    state_array = pi(state_array)
    state_in = pi(state_in)
    state_array = chi_before_reg(state_array, state_in, config)
    if file_name != None:
        with open(file_name, 'w') as file:
            json.dump(state_array, file)
    return state_array


# glitch_partition_subsets

def related_indices(index, config):
    PXT, PX0, PX1, PX0I, PX1I, X0, X1, OFF = config
    # Input the index of a register, output indices of related registers that
    # use common chi inputs with the input register.
    # NOTE: each index in the output corresponds to two registers
    # (x, y, z, s) -> d_{2s}[x, y, z], d_{2s+1}[x, y, z]
    x, y, z, s = index
    # chi_list: chi inputs used in calculating this register
    chi_list = [(x, y, z),
                ((x + 1) % 5, y, z),
                ((x + 2) % 5, y, z)]
    # chi inputs used in Changing Of The Guard (COTG)
    j = W * y + z
    if j > 0:
        jj = (j - OFF) % (5 * W)
        yy = jj // W
        zz = jj % W
        if x == PX0:
            chi_list.append((X0, yy, zz))
        if x == PX1:
            chi_list.append((X1, yy, zz))
    # find indices of registers which use chi inputs in chi_list
    index_list = []
    for xx, yy, zz in chi_list:
        # each index corresponds to two registers
        # (x, y, z, s) -> d_{2s}[x, y, z], d_{2s+1}[x, y, z]
        index_list += [(xx, yy, zz, 0), (xx, yy, zz, 1),
                       ((xx - 1) % 5, yy, zz, 0), ((xx - 1) % 5, yy, zz, 1),
                       ((xx - 2) % 5, yy, zz, 0), ((xx - 2) % 5, yy, zz, 1)]
        # COTG
        jj = W * yy + zz
        j = (jj + OFF) % (5 * W)
        if j > 0:
            y = j // W
            z = j % W
            if xx == X0:
                index_list += [(PX0, y, z, 0), (PX0, y, z, 1)]
            if xx == X1:
                index_list += [(PX1, y, z, 0), (PX1, y, z, 1)]

    # Remove duplicate indices
    index_list = list(set(index_list))
    # Remove index itself from index_list
    index_list.remove(index)
    return index_list


def partition_subsets(index_list, config):
    # Input a list of register indices, partition these registers into subsets
    # based on whether they share chi inputs.

    subsets = []  # list of subsets
    checked = []  # checked indices in index_list
    tbc = []     # index list to be checked
    for index in index_list:
        if index in checked:  # index already checked
            continue
        subset = [index] # add `index` to a new subset
        checked.append(index)
        tbc = related_indices(index, config)
        # Check if the indices in TBC exist in the index_list
        while len(tbc) > 0:
            c = tbc.pop(0) # currently checking chi input
            checked.append(c)
            if c in index_list:  # potential leak found
                subset.append(c)
                # handle related indices of c
                for c_rel in related_indices(c, config):
                    if c_rel in checked:  # c_rel already checked
                        continue
                    elif c_rel in tbc:  # c_rel already in checking list
                        continue
                    else:  # add c_rel to the checking list
                        tbc.append(c_rel)
        if len(subset) > 1:
            subsets.append(subset)
    return subsets


def glitch_partition_subsets(state_array, config, show=False):
    # Find all subsets for all glitch-extended probes
    subsets = []
    for x, sheet in enumerate(state_array):
        for y, lane in enumerate(sheet):
            for z, state in enumerate(lane):
                for s, index_list in enumerate(state):
                    subsets += partition_subsets(index_list, config)

    # Classify potential leaks for ease of reading and analysis
    classified_subsets = []
    for subset in subsets:
        # save their (j, x, s), where j is saved in relative terms
        j_min = min([W*y+z for x, y, z, s in subset])
        char = tuple(sorted([(W*y+z-j_min, x, s) for x, y, z, s in subset]))
        if char not in classified_subsets:
            classified_subsets.append(char)

    # Show classified potential subsets
    if show:
        for i, subset in enumerate(classified_subsets):
            print(subset)

    # Save classified subsets
    return classified_subsets


# glitch_independence_check

def input_names_gen(index, config):
    # Input: Index of a register
    # Output: Names of inputs used in chi_pr operation before the register
    PXT, PX0, PX1, PX0I, PX1I, X0, X1, OFF = config
    j, x, s = index
    names = []
    # DOM-based 1st-order chi
    if s == 0:
        names.append(f'a{(x + 1)%5}_{j}')
        names.append(f'a{(x + 2)%5}_{j}')
    elif s == 1:
        names.append(f'a{(x + 1)%5}_{j}')
        names.append(f'b{(x + 2)%5}_{j}')
        names.append(f'a{x}_{j}')
    elif s == 2:
        names.append(f'b{(x + 1)%5}_{j}')
        names.append(f'a{(x + 2)%5}_{j}')
        names.append(f'b{x}_{j}')
    else:  # s == 3
        names.append(f'b{(x + 1)%5}_{j}')
        names.append(f'b{(x + 2)%5}_{j}')
    # Additional parts to be designed
    # COTG
    if x == PX0:
        if s == (1 ^ PX0I) or s == (2 ^ PX0I):
            names.append(f'a{X0}_{(j-OFF)%(5*W)}')
    elif x == PX1:
        if s == (1 ^ PX1I) or s == (2 ^ PX1I):
            names.append(f'a{X1}_{(j-OFF)%(5*W)}')
    # theta inputs as pseudorandomness
    if x == PXT:
        if s == 0 or s == 1:
            names.append(f'a{x}_{j}theta')
        if s == 2 or s == 3:
            names.append(f'b{x}_{j}theta')
    return names


def f_o_gen(index, input_indices, config):
    # Input: Index of a register
    # Output: Mapping function from inputs to the output (register)
    PXT, PX0, PX1, PX0I, PX1I, X0, X1, OFF = config
    j, x, s = index
    xs = input_indices
    if x == PX0:
        if PX0I == 1:
            if s == 0 or s == 3:
                f = not_and_xor_gen(xs[0], xs[1], xs[2])
            else:
                f = and_xor_gen(xs[0], xs[1], xs[2])
        else:
            if s == 0 or s == 3:
                f = not_and_gen(xs[0], xs[1])
            else:
                f = and_xor2_gen(xs[0], xs[1], xs[2], xs[3])
    elif x == PX1:
        if PX1I == 1:
            if s == 0 or s == 3:
                f = not_and_xor_gen(xs[0], xs[1], xs[2])
            else:
                f = and_xor_gen(xs[0], xs[1], xs[2])
        else:
            if s == 0 or s == 3:
                f = not_and_gen(xs[0], xs[1])
            else:
                f = and_xor2_gen(xs[0], xs[1], xs[2], xs[3])
    else:
        if s == 0 or s == 3:
            f = not_and_gen(xs[0], xs[1])
        else:
            f = and_xor_gen(xs[0], xs[1], xs[2])
    if x == PXT:
        return f_xor_gen(f, xs[-1])
    else:
        return f


class check():
    # Truth table generation and check

    def __init__(self, n_i, n_o, n_s, f_o, f_s):
        self.n_i = n_i # Number of inputs (inputs of chi_pr)
        self.n_o = n_o # Number of outputs (registers)
        self.n_s = n_s # Number of secrets (unshared inputs)
        self.f_o = f_o # Mapping functions from inputs to outputs
        self.f_s = f_s # Mapping functions from inputs to secrets
        assert len(f_o) == n_o
        assert len(f_s) == n_s
        # Generate all posible input vectors
        self.input_table = [[((n >> i) & 1) == 1 for i in range(n_i)]
                                                 for n in range(2**n_i)]
        # Calculate corresponding outputs and secrets
        self.output_table = [[f(inp) for f in f_o] for inp in self.input_table]
        self.secret_table = [[f(inp) for f in f_s] for inp in self.input_table]

    def analyze(self):
        leak_list = []
        self.dis_list = []
        # Analyze every possible output pattern
        for o_i in range(2**self.n_o):
            # Currently analyzed output, converted to list format
            o_ref = [((o_i >> i) & 1) == 1 for i in range(self.n_o)]
            # Search input vectors whose output = o_ref, and save their indices
            # in `index_list`
            index_list = []
            for index, out in enumerate(self.output_table):
                if o_ref == out:
                    index_list.append(index)
            # Analyze corresponding secrect distribution. uniform or not
            dis = [0 for i in range(2**self.n_s)]
            dis_ref = len(index_list)//(2**self.n_s)
            for index in index_list:
                secret = self.secret_table[index]
                s_index = sum([secret[i] * (2**i) for i in range(len(secret))])
                dis[s_index] += 1
            for d in dis:
                if d != dis_ref:
                    leak_list.append(o_ref)
                    self.dis_list.append(dis)
                    break
        return leak_list

# Generators for all possible mapping functions
# Input: indices in the name list of the function's inputs
# Output: a mapping function from inputs to outputs/secrets
def f_xor_gen(f, xxt):
    def f_xor(in_list):
        if 0 <= xxt < len(in_list):
            return f(in_list) ^ in_list[xxt]
        else:
            raise
    return f_xor


def xor_gen(xx1, xx2):
    def xor(in_list):
        if (0 <= xx1 < len(in_list) and 0 <= xx2 < len(in_list)):
            return in_list[xx1] ^ in_list[xx2]
        else:
            raise
    return xor


def not_and_gen(nx1, ax2):
    def not_and(in_list):
        if (0 <= nx1 < len(in_list) and 0 <= ax2 < len(in_list)):
            return not in_list[nx1] and in_list[ax2]
        else:
            raise
    return not_and


def not_and_xor_gen(nx1, ax2, xx3):
    def not_and_xor(in_list):
        if (0 <= nx1 < len(in_list) and 0 <= ax2 < len(in_list)
                and 0 <= xx3 < len(in_list)):
            return (not in_list[nx1] and in_list[ax2]) ^ in_list[xx3]
        else:
            raise
    return not_and_xor


def not_and_xor2_gen(nx1, ax2, xx3, xx4):
    def not_and_xor2(in_list):
        if (0 <= nx1 < len(in_list) and 0 <= ax2 < len(in_list)
            and 0 <= xx3 < len(in_list)
                and 0 <= xx4 < len(in_list)):
            return ((not in_list[nx1] and in_list[ax2]) ^ in_list[xx3]
                                                        ^ in_list[xx4])
        else:
            raise
    return not_and_xor2


def and_xor_gen(ax1, ax2, xx3):
    def and_xor(in_list):
        if (0 <= ax1 < len(in_list) and 0 <= ax2 < len(in_list)
                and 0 <= xx3 < len(in_list)):
            return (in_list[ax1] and in_list[ax2]) ^ in_list[xx3]
        else:
            raise
    return and_xor


def and_xor2_gen(ax1, ax2, xx3, xx4):
    def and_xor2(in_list):
        if (0 <= ax1 < len(in_list) and 0 <= ax2 < len(in_list)
            and 0 <= xx3 < len(in_list)
                and 0 <= xx4 < len(in_list)):
            return ((in_list[ax1] and in_list[ax2]) ^ in_list[xx3]
                                                    ^ in_list[xx4])
        else:
            raise
    return and_xor2


def checker_gen(index_list, config):
    # Input: index list of a subset
    # Output: a checker for this subset
    PXT, PX0, PX1, PX0I, PX1I, X0, X1, OFF = config
    if len(index_list[0]) == 2:
        index_list = [(0, x, s) for x, s in index_list]
    input_list = [] # Name list of the inputs of this subset
    f_o = [] # Mapping functions from inputs to the outputs (registers)
    f_s = [] # Mapping functions from inputs to the secrets (unshared inputs)
    for j, x, s in index_list:
        # each index in the subset corresponds to two registers
        # (j, x, s) -> d_{2s}[x, j], d_{2s+1}[x, j]
        for i in range(2):
            # generate input names of the register d_{2s+i}[x, j]
            names = input_names_gen((j, x, 2*s+i), config)
            # indices of the input name in `input_list`
            indices = []
            for name in names:
                if name not in input_list:
                    input_list.append(name)
                indices.append(input_list.index(name))

            f_o.append(f_o_gen((j, x, 2*s+i), indices, config))
    # check whether secret exists (both shares are in the input list)
    secret_list = []
    for name in input_list:
        if name in secret_list:
            continue
        # generate the name of the other share
        if name[0] == 'a':
            share = 'b' + name[1:]
        else:
            share = 'a' + name[1:]

        if share in input_list:
            f_s.append(xor_gen(input_list.index(
                name), input_list.index(share)))
            secret_list.append(name)
            secret_list.append(share)

    n_i = len(input_list)
    n_o = len(f_o)
    n_s = len(f_s)
    return check(n_i, n_o, n_s, f_o, f_s), input_list, secret_list


def glitch_independence_check(classified_subsets, config, show=False):
    results = []
    for i, subset in enumerate(classified_subsets):
        checker, i_list, s_list = checker_gen(subset, config)
        if show:
            print(f'Checking {subset}:')
            print(f'- Input list: {i_list}')
            print(f'- Secret list: {s_list}')
            print(f'- subset list: {checker.analyze()}')
        else:
            results.append((subset, checker.analyze()))
    if not show:
        return results


# glitch_first_round_non_completeness

def glitch_first_round_non_completeness(state_array):
    # Search for non-completeness violations in the first round
    leak_list = [] # Used to save found violations
    # For each register (glitch-robust probe) and corresponding list
    for x, sheet in enumerate(state_array):
        for y, lane in enumerate(sheet):
            for z, state in enumerate(lane):
                for s, index_list in enumerate(state):
                    leak = []
                    # For each index in the list
                    for index in set(index_list):
                        # Generate the index of the other share
                        index_leak = [index[0], index[1],     # (x, y,
                                      index[2], 1 - index[3]] #  z, share)
                        # Check if the other share is in the list
                        # (violation of non-completeness)
                        if index_leak in index_list:
                            leak.append(index)
                    # If violation exists
                    if len(leak) > 0:
                        leak_list.append([(x, y, z, s), leak])

    return len(leak_list)


# glitch_ct_uniform_check

def index_forwards(index):
    # Input index before rho, output index after rho and pi
    x, y, z = index
    return (y, (2*x+3*y) % 5, (z+RHO_OFFSET[x][y]) % W)


def index_backwards(index):
    # Input index after pi, output index before pi and rho
    x, y, z = index
    xx = (x + 3*y) % 5
    yy = x
    zz = (z - RHO_OFFSET[xx][yy]) % W
    return (xx, yy, zz)


def chi_theta_inputs(index, config):
    # Input index of a register, output indices of chi inputs and theta inputs
    # used in computing the register's value in chi_pr
    # Note: the output index is after pi (not before rho)
    PXT, PX0, PX1, PX0I, PX1I, X0, X1, OFF = config

    x, y, z, _ = index # the index of the register

    # chi inputs used in calculating the register's value in chi_pr
    chi_list = [(x, y, z),
                ((x + 1) % 5, y, z),
                ((x + 2) % 5, y, z)]

    # Changing Of The Guard (COTG)
    j = W * y + z
    if j > 0:
        jj = (j - OFF) % (5 * W)
        yy = jj // W
        zz = jj % W
        if x == PX0:
            chi_list.append((X0, yy, zz))
        if x == PX1:
            chi_list.append((X1, yy, zz))

    # theta inputs used in calculating the register's value in chi_pr
    theta_list = []
    if x == PXT:
        theta_list.append((PXT, y, z))

    return chi_list, theta_list

# BEGIN: Deprecated version, do not use for security verification, only for
# preliminary searching here.
def related_indices_t(index):
    # Indices of related registers which use common chi inputs with `index`
    xx, yy, zz = index_backwards(index)

    # find index of chi inputs which uses this
    chi_list_origin = ([(xx, yy, zz)]
                       + [((xx - 1) % 5, y_, zz) for y_ in range(5)]
                       + [((xx + 1) % 5, y_, (zz - 1) % W) for y_ in range(5)])

    chi_list = [index_forwards(index) for index in chi_list_origin]
    return chi_list


def related_indices_c(index):
    # Indices of related registers which use common chi inputs with `index`
    xx, yy, zz = index_backwards(index)

    # find index of theta inputs which uses this or its share
    theta_list_origin = ([(xx, yy, zz)]
                         + [((xx - 1) % 5, y_, zz) for y_ in range(5)]
                         + [((xx + 1) % 5, y_, (zz - 1) % W)
                            for y_ in range(5)])

    theta_list = [index_forwards(index) for index in theta_list_origin]

    # find index of chi inputs which uses this
    chi_list_origin = ([(xx, y_, zz) for y_ in range(5) if y_ != yy]
                       + [((xx - 1) % 5, y_, zz) for y_ in range(5)]
                       + [((xx - 2) % 5, y_, (zz + 1) % W) for y_ in range(5)]
                       + [((xx + 1) % 5, y_, (zz - 1) % W) for y_ in range(5)]
                       + [((xx + 2) % 5, y_, (zz - 1) % W) for y_ in range(5)])

    chi_list = [index_forwards(index) for index in chi_list_origin]
    return chi_list, theta_list


def potential_leaks_theta(chi_list, theta_list):
    # Potential leaks in `index_list` whose chi inputs are not independent
    results = []  # list of potential leaks
    for theta in theta_list:
        checked_chi = []
        checked_theta = []
        tbc_chi = []
        tbc_theta = []
        leaks = [theta, [], []]
        checked_theta.append(theta)
        tbc_chi = related_indices_t(theta)

        while len(tbc_chi) + len(tbc_theta) > 0:
            if len(tbc_chi) > 0:
                c = tbc_chi.pop(0)
                checked_chi.append(c)
                if c in chi_list:
                    leaks[1].append(c)
                    c_rel_chi, c_rel_theta = related_indices_c(c)
                    for cc in c_rel_chi:
                        if cc in checked_chi:
                            continue
                        elif cc in tbc_chi:
                            continue
                        else:
                            tbc_chi.append(cc)
                    for ct in c_rel_theta:
                        if ct in checked_theta:
                            continue
                        elif ct in tbc_theta:
                            continue
                        else:
                            tbc_theta.append(ct)
            if len(tbc_theta) > 0:
                t = tbc_theta.pop(0)
                checked_theta.append(t)
                if t in theta_list:
                    leaks[2].append(t)
                    t_rel_chi = related_indices_t(t)
                    for tc in t_rel_chi:
                        if tc in checked_chi:
                            continue
                        elif tc in tbc_chi:
                            continue
                        else:
                            tbc_chi.append(tc)
        results.append(leaks)
    return results


def check_leak(index, chi_list, theta_list):
    chi_list = list(deepcopy(chi_list))
    theta_list = list(deepcopy(theta_list))
    while True:
        theta_count = {}
        for t in theta_list:
            theta_count[t] = 1
        for cx, cy, cz in chi_list:
            ct_list = ([(cx, cy, cz)]
                       + [((cx - 1) % 5, y_, cz) for y_ in range(5)]
                       + [((cx + 1) % 5, y_, (cz - 1) % W) for y_ in range(5)])
            for ct in ct_list:
                if ct in theta_count:
                    theta_count[ct] += 1
                else:
                    theta_count[ct] = 1
        if index not in theta_count:
            return []
        else:
            theta_count[index] += 1
        # find keys whose value in `theta_count` equals 1
        tbr_chi = []
        tbr_theta = []
        for k, v in theta_count.items():
            if v > 1:
                continue
            elif k in theta_list:
                tbr_theta.append(k)
            else:
                cx, cy, cz = k
                c_list = ([(cx, cy, cz)]
                          + [((cx + 1) % 5, y_, cz) for y_ in range(5)]
                          + [((cx - 1) % 5, y_, (cz + 1) % W)
                             for y_ in range(5)])
                for c in c_list:
                    if c in chi_list:
                        tbr_chi.append(c)

        if len(tbr_chi) + len(tbr_theta) == 0:
            return [index, chi_list, theta_list]
        else:
            for c in set(tbr_chi):
                chi_list.remove(c)
            for t in tbr_theta:
                theta_list.remove(t)


def glitch_ct_uniform_check(state_array, config, show=False):
    # Iterate through each probe list
    results = []
    for x, sheet in enumerate(state_array):
        for y, lane in enumerate(sheet):
            for z, state in enumerate(lane):
                for s, index_list in enumerate(state):
                    # Generate all chi inputs and all theta inputs
                    # used by registers in index_list
                    chi_list = []
                    theta_list = []
                    for index in set(index_list):
                        c, t = chi_theta_inputs(index, config)
                        chi_list += c
                        theta_list += t
                    chi_list = list(set(chi_list))
                    theta_list = list(set(theta_list))

                    # Iterate through each theta input and
                    # find all related inputs
                    results += potential_leaks_theta(chi_list, theta_list)

    # To visually inspect the results, run the following code.
    if show:
        # Classify potential leaks for ease of reading and analysis
        classified_results = [[]]
        for result in results:
            # How many elements are involved
            num = len(result[1]+result[2])
            while num > len(classified_results):
                classified_results.append([])

            x0, y0, z0 = index_backwards(result[0])
            chi_origin = [index_backwards(index) for index in result[1]]
            theta_origin = [index_backwards(index) for index in result[2]]
            chi_relative = tuple(
                sorted([((x - x0) % 5, (y - y0) % 5, (z - z0) % W)
                        for x, y, z in chi_origin]))
            theta_relative = tuple(
                sorted([((x - x0) % 5, (y - y0) % 5, (z - z0) % W)
                        for x, y, z in theta_origin]))
            char = ((0, 0, 0), chi_relative, theta_relative)
            if char not in classified_results[num-1]:
                classified_results[num-1].append(char)

        # Show classified potential leaks
        for i, leaks in enumerate(classified_results):
            print(f'***** num = {i+1}, num_leak_type = {len(leaks)} *****')
            for leak in leaks:
                print(leak)

        # Check leaks in classified results
        check_result_list = []
        for leaks in classified_results:
            for leak in leaks:
                check_result = check_leak(leak[0], leak[1], leak[2])
                if len(check_result) > 0:
                    check_result_list.append(check_result)
        print(len(check_result_list))
        for result in check_result_list:
            print(result)

    # Check leaks in results
    check_result_list = []
    for result in results:
        index_origin = index_backwards(result[0])
        chi_origin = [index_backwards(index) for index in result[1]]
        theta_origin = [index_backwards(index) for index in result[2]]
        check_result = check_leak(index_origin, chi_origin, theta_origin)
        if len(check_result) > 0:
            check_result_list.append(check_result)
    return len(check_result_list)
# END: Deprecated version, do not use for security verification, only for
# preliminary searching here.


# Main
# NOTE: For performance reason, only checked security under glitch-robust
#       model. Please execute all checks in folder `security verification` to
#       ensure comprehensive security.


# (PXT, PX0, PX1, PX0I, PX1I)
# PXT: Protect X-coordinate Theta, x-coordinate of theta input used as 
#      randomness
# PX0: Protect X-coordinate no.0, first chi input protected by COTG
# PX1: Protect X-coordinate no.1, second chi input protected by COTG
# PX0I: Protect X-coordinate no.0 xored with Inner-domain products (=1) or
#       cross-domain products (=0)
# PX1I: Protect X-coordinate no.1 xored with Inner-domain products (=1) or
#       cross-domain products (=0)
PLIST = [(0, 0, 1, 1, 1), (0, 0, 1, 0, 1), (1, 0, 1, 0, 1), (1, 0, 1, 0, 0),
         (3, 0, 1, 0, 1), (3, 0, 1, 0, 0),
         (3, 3, 2, 0, 0), (3, 3, 2, 0, 1), (3, 3, 2, 1, 0), (3, 3, 2, 1, 1),
         (3, 3, 4, 0, 0), (3, 3, 4, 0, 1), (3, 3, 4, 1, 0), (3, 3, 4, 1, 1)]

TESTLIST = []
# OFF: OFFset of COTG
for off in [1, 2, 3, 6, 7, 9, 11, 13, 14, 17, 18, 19, 21, 22, 23, 26, 27, 29,
            31, 33]:
    for pxt, px0, px1, px0i, px1i in PLIST:
        TESTLIST.append((pxt, px0, px1, px0i, px1i, px0, px1, off))
        TESTLIST.append((pxt, px0, px1, px0i, px1i, px1, px0, off))

l = len(TESTLIST) // n_cores
config_lists = [TESTLIST[i * l: i * l + l] for i in range(n_cores)]
progress_bars = [tqdm(config_lists[i]) for i in range(n_cores)]


def task(i):
    with open(f'search_results.log{i}', 'w') as f:
        progress_bar = progress_bars[i]
        for config in progress_bar:
            PXT, PX0, PX1, PX0I, PX1I, X0, X1, OFF = config
            # X0: X-coordinate no.0 of chi input used as randomness (COTG)
            # X1: X-coordinate no.1 of chi input used as randomness (COTG)
            f.flush()
            progress_bar.set_description(f'Task {i} Generating Glitch List   ')
            state_array = glitch_list_gen(config)
            progress_bar.set_description(f'Task {i} Checking First Round     ')
            n_leak_first = glitch_first_round_non_completeness(state_array)
            progress_bar.set_description(f'Task {i} Complete Round Subsets   ')
            classified_leaks = glitch_partition_subsets(state_array, config)
            if len(classified_leaks) > 50:
                f.write(f'{PXT}\t{PX0}\t{PX1}\t{PX0I}\t {PX1I}\t  {X0}\t ' +
                        f'{X1}\t{OFF}\t{n_leak_first}\t' +
                        f'TM:{len(classified_leaks)}\n')
                continue
            if max([len(leak) for leak in classified_leaks]) > 5:
                l = max([len(leak) for leak in classified_leaks])
                f.write(f'{PXT}\t{PX0}\t{PX1}\t{PX0I}\t {PX1I}\t  {X0}\t ' +
                        f'{X1}\t{OFF}\t{n_leak_first}\tTL:{l}\n')
                continue
            progress_bar.set_description(f'Task {i} Checking Complete Round  ')
            results = glitch_independence_check(classified_leaks, config)
            n_leak_comp = 0
            for leak, leak_list in results:
                if len(leak_list) > 0:
                    n_leak_comp += 1
            progress_bar.set_description(f'Task {i} Complete Round CT Uniform')
            n_leak_theta = glitch_ct_uniform_check(state_array, config)
            f.write(f'{PXT}\t{PX0}\t{PX1}\t{PX0I}\t {PX1I}\t  {X0}\t {X1}\t' +
                    f'{OFF}\t{n_leak_first}\t{n_leak_comp}\t{n_leak_theta}\n')


def merge_files(input_files, output_file):
    with open(output_file, 'w') as outfile:
        outfile.write('NOTE: For performance reason, only checked security' +
            ' under glitch-robust model.\nNOTE: Please execute all checks in' +
            ' folder `security verification` to ensure comprehensive' +
            ' security.\n\nPXT: Protect X-coordinate Theta, x-coordinate' +
            ' of theta input used as randomness\nPX0: Protect X-coordinate' +
            ' no.0, first chi input protected by COTG\nPX1: Protect' +
            ' X-coordinate no.1, second chi input protected by COTG\nPX0I:' +
            ' Protect X-coordinate no.0 xored with Inner-domain products' +
            ' (=1) or cross-domain products (=0)\nPX1I: Protect X-coordinate' +
            ' no.1 xored with Inner-domain products (=1) or cross-domain' +
            ' products (=0)\nX0: X-coordinate no.0 of chi input used as' +
            ' randomness (COTG)\nX1: X-coordinate no.1 of chi input used as' +
            ' randomness (COTG)\nOFF: OFFset of COTG\nFIR: Number of leaks' +
            ' in the FIRst round\nCOM: Number of leaks in the COMplete round' +
            '\nCT: Number of non-uniform regarding Chi input and Theta input' +
            '\nTM: Too Many leaks\nTL: Too Long leak list to check\n\n' +
            'PXT PX0 PX1 PX0I PX1I X0 X1 OFF\tFIR\tCOM\tCT\n')
        for input_file in input_files:
            with open(input_file, 'r') as infile:
                outfile.write(infile.read())


if __name__ == '__main__':
    multiprocessing.freeze_support()
    with multiprocessing.Pool(n_cores) as p:
        p.map(task, [i for i in range(n_cores)])

    input_files = [f'search_results.log{i}' for i in range(n_cores)]
    output_file = 'search_results.log'
    merge_files(input_files, output_file)

    import os
    for i in range(n_cores):
        os.remove(f'search_results.log{i}')

    for progress_bar in progress_bars:
        progress_bar.close()
