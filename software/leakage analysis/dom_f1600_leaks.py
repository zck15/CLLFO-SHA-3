# dom_f1600_leaks, program for analyzing glitch-induced side-channel leakage in
# DOM-Keccak-f[1600].
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

from copy import deepcopy
import json

W = 64
RHO_OFFSET = [[0,   36,  3,   105, 210],
              [1,   300, 10,  45,  66],
              [190, 6,   171, 15,  253],
              [28,  55,  153, 21,  120],
              [91,  276, 231, 136, 78]]

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

def chi_before_reg(state_array):
    A = deepcopy(state_array)
    state_array = [[[[
        A[(x + 1) % 5][y][z][0] + A[(x + 2) % 5][y][z][0],
        A[x][y][z][0] + A[(x + 1) % 5][y][z][0] + A[(x + 2) % 5][y][z][1],
        A[x][y][z][1] + A[(x + 1) % 5][y][z][1] + A[(x + 2) % 5][y][z][0],
        A[(x + 1) % 5][y][z][1] + A[(x + 2) % 5][y][z][1]] for z in range(W)]
                                                           for y in range(5)]
                                                           for x in range(5)]
    return state_array


def related_indices(index):
    # Input the index of a register, output indices of related registers that
    # use common chi inputs with the input register.
    # NOTE: each index in the output corresponds to two registers
    # (x, y, z, s) -> d_{2s}[x, y, z], d_{2s+1}[x, y, z]

    x, y, z, s = index

    # chi_list: chi inputs used in calculating this register
    chi_list = [(x, y, z), ((x + 1) % 5, y, z), ((x + 2) % 5, y, z)]

    # find indices of registers which use chi inputs in chi_list
    index_list = []
    for xx, yy, zz in chi_list:
        # each index corresponds to two registers
        # (x, y, z, s) -> d_{2s}[x, y, z], d_{2s+1}[x, y, z]
        index_list += [(xx, yy, zz, 0), (xx, yy, zz, 1),
                       ((xx - 1) % 5, yy, zz, 0), ((xx - 1) % 5, yy, zz, 1),
                       ((xx - 2) % 5, yy, zz, 0), ((xx - 2) % 5, yy, zz, 1)]
    
    # Remove duplicate indices
    index_list = list(set(index_list))
    # Remove index itself from index_list
    index_list.remove(index)
    return index_list

def potential_leaks(index_list):
    # Input a list of register indices, picking out registers that share chi 
    # inputs.

    results = []  # list of potential leaks (registers that share chi inputs)
    checked = []  # checked indices in index_list
    tbc = []      # index list to be checked
    for index in index_list:
        if index in checked:  # index already checked
            continue
        leaks = [index]
        checked.append(index)
        tbc = related_indices(index)
        # Check if the indices in TBC exist in the index_list
        while len(tbc) > 0:
            c = tbc.pop(0) # currently checking chi input
            checked.append(c)
            if c in index_list:  # potential leak found
                leaks.append(c)
                for c_rel in related_indices(c): # handle related indices of c
                    if c_rel in checked:  # c_rel already checked
                        continue
                    elif c_rel in tbc:  # c_rel already in checking list
                        continue
                    else:  # add c_rel to the checking list
                        tbc.append(c_rel)
        if len(leaks) > 1:
            results.append(leaks)
    return results

# Main
state_array = init_state() # Initialize index list for theta inputs
state_array = theta(state_array)
state_array = rho(state_array)
state_array = pi(state_array)
state_array = chi_before_reg(state_array)

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
                    # Generate the index of the other share (x, y, z, share)
                    index_leak = (index[0], index[1], index[2], 1 - index[3])
                    # Check if the other share is in the list (violation of 
                    # non-completeness)
                    if index_leak in index_list:
                        leak.append(index)
                # If violation exists
                if len(leak) > 0:
                    leak_list.append([(x, y, z, s), leak])

print(f'The Number of glitch-extended probes violating non-completeness: ' +
      f'{len(leak_list)}')
# for leak in leak_list:
#     print(leak)

# Find all new potential leaks for all glitch-extended probes
leak_list = []
subsets = []
for x, sheet in enumerate(state_array):
    for y, lane in enumerate(sheet):
        for z, state in enumerate(lane):
            for s, index_list in enumerate(state):
                leak = potential_leaks(index_list)
                if len(leak) > 0:
                    leak_list.append([(x, y, z, s), leak])
                    subsets += leak

print(f'New leakage: {len(leak_list)}\n' +
      f'Probe index, ' +
      f'indices of related inputs using common chi inputs in previous round ' +
      f'(x, y, z, share)')
for leak in leak_list:
    print(leak)

# Classify subsets for ease of reading and analysis
classified_subsets = []
for subset in subsets:
    # Only one row, save just their (x, s)
    char = tuple(sorted([(x, s) for x, y, z, s in subset]))
    if char not in classified_subsets:
        classified_subsets.append(char)

classified_subsets.sort()

# Show classified subsets
print(f'Number of subsets: {len(classified_subsets)}')
for subset in classified_subsets:
    print(subset)

# Save subsets
with open('glitch_subsets.json', 'w') as file2:
    json.dump(classified_subsets, file2)
