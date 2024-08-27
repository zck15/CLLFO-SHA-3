# dom_independence_check, program for statistical analysis of the correlation
# between register values and secret value distribution in DOM-Keccak-f[200].
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

import json

W = 64


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
                                                 for n in range(2 ** n_i)]
        # Calculate corresponding outputs and secrets
        self.output_table = [[f(inp) for f in f_o] for inp in self.input_table]
        self.secret_table = [[f(inp) for f in f_s] for inp in self.input_table]

    def analyze(self):
        leak_list = []
        self.dis_list = []
        # Analyze every possible output pattern
        for o_i in range(2 ** self.n_o):
            # Currently analyzed output, converted to list format
            o_ref = [((o_i >> i) & 1) == 1 for i in range(self.n_o)]
            # Search input vectors whose output = o_ref, and save their indices
            # in `index_list`
            index_list = []
            for index, out in enumerate(self.output_table):
                if o_ref == out:
                    index_list.append(index)
            # Analyze corresponding secrect distribution. uniform or not
            dis = [0 for i in range(2 ** self.n_s)]
            dis_ref = len(index_list) // (2 ** self.n_s)
            for index in index_list:
                secret = self.secret_table[index]
                s_index = sum([secret[i] * (2 ** i) 
                                for i in range(len(secret))])
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
def and_gen(ax1, ax2):
    def _and(in_list):
        if (0 <= ax1 < len(in_list) and 0 <= ax2 < len(in_list)):
            return in_list[ax1] and in_list[ax2]
        else:
            raise
    return _and

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

def input_names_gen(index):
    # Input: Index of a register
    # Output: Names of inputs used in chi_pr operation before the register
    j, x, s = index
    names = []
    if s == 0:
        names.append(f'v_0[{(x+1)%5}, {j}]')
        names.append(f'v_0[{(x+2)%5}, {j}]')
    elif s == 1:
        names.append(f'v_0[{(x+1)%5}, {j}]')
        names.append(f'v_1[{(x+2)%5}, {j}]')
        names.append(f'v_0[{x}, {j}]')
    elif s == 2:
        names.append(f'v_1[{(x+1)%5}, {j}]')
        names.append(f'v_0[{(x+2)%5}, {j}]')
        names.append(f'v_1[{x}, {j}]')
    else:  # s == 3
        names.append(f'v_1[{(x+1)%5}, {j}]')
        names.append(f'v_1[{(x+2)%5}, {j}]')
    return names

def f_o_gen(index, input_indices):
    # Input: Index of a register
    # Output: Mapping function from inputs to the output (register)
    j, x, s = index
    xs = input_indices
    if s == 0:
        return not_and_gen(xs[0], xs[1])
    elif s == 1:
        return not_and_xor_gen(xs[0], xs[1], xs[2])
    elif s == 2:
        return and_xor_gen(xs[0], xs[1], xs[2])
    else:
        return and_gen(xs[0], xs[1])

def checker_gen(index_list):
    # Input: index list of a subset
    # Output: a checker for this subset
    if len(index_list[0]) == 2: # One-row subset
        index_list = [(0, x, s) for x, s in index_list]
    input_list = [] # Name list of the inputs of this subset
    f_o = [] # Mapping functions from inputs to the outputs (registers)
    f_s = [] # Mapping functions from inputs to the secrets (unshared inputs)
    for j, x, s in index_list:
        # each index in the subset corresponds to two registers
        # (j, x, s) -> d_{2s}[x, j], d_{2s+1}[x, j]
        for i in range(2):
            # generate input names of the register d_{2s+i}[x, j]
            names = input_names_gen((j, x, 2 * s + i))
            # indices of the input name in `input_list`
            indices = []
            for name in names:
                if name not in input_list:
                    input_list.append(name)
                indices.append(input_list.index(name))

            f_o.append(f_o_gen((j, x, 2 * s + i), indices))
    # check whether secret exists (both shares are in the input list)
    secret_list = []
    for name in input_list:
        if name in secret_list:
            continue
        # generate the name of the other share
        if name[0:3] == 'v_0':
            share = 'v_1' + name[3:]
        else:
            share = 'v_0' + name[3:]

        if share in input_list:
            f_s.append(xor_gen(input_list.index(name),
                               input_list.index(share)))
            secret_list.append(name)
            secret_list.append(share)

    n_i = len(input_list)
    n_o = len(f_o)
    n_s = len(f_s)
    return check(n_i, n_o, n_s, f_o, f_s), input_list, secret_list

# Main
# Read result file generated by 'dom_f1600_leaks.py'
with open('glitch_subsets.json', 'r') as file:
    classified_subsets = json.load(file)
    print(f'Number of subsets: {len(classified_subsets)}')
    for subset in classified_subsets:
        print(f'- Checking probe subset (x, share): ' +
              f'{[tuple(p) for p in subset]}')
        checker, i_list, s_list = checker_gen(subset)
        print(f'  - Number of inputs = {checker.n_i},' +
              f' number of outputs = {checker.n_o},' +
              f' number of secrets = {checker.n_s}')
        print(f'  - Input list: {i_list}')
        o_list = []
        for p in subset:
            o_list += [f'd_{2*p[1]}[{p[0]}, 0]', f'd_{2*p[1]+1}[{p[0]}, 0]']
        print(f'  - Output list: {o_list}')
        s_list = ['v' + s_list[2*i][3:] for i in range(len(s_list) // 2)]
        print(f'  - Secet list: {s_list}')
        reg_values = checker.analyze()
        if len(reg_values) > 0:
            print(f'  - Fail! Number of non-independent register values: ' +
                  f'{len(reg_values)}')
        else:
            print(f'  - Pass.')
