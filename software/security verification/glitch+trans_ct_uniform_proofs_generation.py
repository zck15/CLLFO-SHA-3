# glitch+trans_ct_uniform_proofs_generation, check uniformity of
# (\hat v^{n-1}[...], \hat s'^{n-1}[...]) for each
# glitch+transition-extended probe.
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


def index_forwards(index):
    # Input index before rho, output index after rho and pi
    x, y, z = index
    return (y, (2 * x + 3 * y) % 5, (z + RHO_OFFSET[x][y]) % W)


def index_backwards(index):
    # Input index after pi, output index before pi and rho
    x, y, z = index
    xx = (x + 3 * y) % 5
    yy = x
    zz = (z - RHO_OFFSET[xx][yy]) % W
    return (xx, yy, zz)


def chi_theta_inputs(index):
    # Input index of a register, output indices of chi inputs and theta inputs
    # used in computing the register's value in chi_pr
    # Note: the output index is after pi (not before rho)

    x, y, z, _ = index # the index of the register

    # chi inputs used in calculating the register's value in chi_pr
    chi_list = [(x, y, z),
                ((x + 1) % 5, y, z),
                ((x + 2) % 5, y, z)]

    # Changing Of The Guard (COTG)
    j = W * y + z
    if j > 0:
        jj = (j - 11) % (5 * W)
        yy = jj // W
        zz = jj % W
        if x == 0:
            chi_list.append((0, yy, zz))
        if x == 1:
            chi_list.append((1, yy, zz))

    # theta inputs used in calculating the register's value in chi_pr
    theta_list = []
    if x == 0:
        theta_list.append((0, y, z))
    return chi_list, theta_list


def proof_sequence_gen(chi_origin, theta_origin):
    # Purpose: To prove that a set of chi inputs and theta inputs satisfies
    #          uniformity.
    # Known:   The 1600-bit theta inputs as a whole satisfy uniformity.
    # Method:  First, the combination of theta inputs in the set satisfies
    #          uniformity, which we call UNIFORM SET. Next, a chi input equals
    #          the XOR of 11 theta inputs. If one of the 11 theta inputs is
    #          exclusive (independent of other elements in the UNIFORM SET),
    #          this theta input can ensure that the UNIFORM SET still satisfies
    #          uniformity after including this chi input into the UNIFORM SET.
    #          Note: The order of selecting elements to add to the UNIFORM SET
    #          is crucial (using the most greedy strategy may not necessarily
    #          succeed in generating such proof steps). Therefore, we generate
    #          proof steps in reverse order. We assume such proof steps exist
    #          (assuming the final UNIFORM SET includes all chi inputs and
    #          theta inputs), and we attempt to trace these steps backward from
    #          the end.
    # Input:   A set of chi inputs and theta inputs (indices before rho and pi)
    # Output:  A series of steps in reverse order, each using some theta inputs
    #          (independent of other elements in the UNIFORM SET), to add some
    #          chi inputs to the UNIFORM SET

    # seq_c[-i]: chi inputs added to the UNIFORM SET in the i-th step
    seq_c = []
    # seq_t[-i]: theta inputs whose independence is utilized in the i-th step
    seq_t = []
    # Since we are generating steps in reverse, we assume the UNIFORM SET
    # eventually includes all chi inputs.
    remaining_chi = [c for c in chi_origin]

    # When there are still chi inputs in the UNIFORM SET, whose step of being
    # added to the UNIFORM SET has yet to be found
    while len(remaining_chi) > 0:
        # A new step
        seq_c.append([])
        seq_t.append([])

        # Number of times the theta input is used by elements in the UNIFORM
        # SET; if used only once, the theta input is independent of other
        # elements in the UNIFORM SET (excluding the elements that use this
        # theta input).
        theta_count = {}
        for t in theta_origin:
            theta_count[t] = 1
        for cx, cy, cz in remaining_chi:
            ct_list = ([(cx, cy, cz)]
                       + [((cx-1) % 5, y_, cz) for y_ in range(5)]
                       + [((cx+1) % 5, y_, (cz-1) % W) for y_ in range(5)])
            for ct in ct_list:
                if ct in theta_count:
                    theta_count[ct] += 1
                else:
                    theta_count[ct] = 1

        # Find theta inputs used only once
        for k, v in theta_count.items():
            if v > 1: # used by multiple elements
                continue
            elif k in theta_origin: # used by theta, not chi input
                continue
            else: # used only once by chi (in remaining_chi)
                # all posible chi inputs that use this theta input
                cx, cy, cz = k
                c_list = ([(cx, cy, cz)]
                          + [((cx + 1) % 5, y_, cz) for y_ in range(5)]
                          + [((cx - 1) % 5, y_, (cz + 1) % W)
                             for y_ in range(5)])

                for c in c_list:
                    if c in seq_c[-1]: # already added in this step
                        continue
                    elif c in remaining_chi:
                        seq_c[-1].append(c)
                        seq_t[-1].append(k)

        # Return two empty lists if proof steps cannot be generated.
        if len(seq_c[-1]) == 0:
            return [], []

        # Remove these chi inputs from the UNIFORM SET. As we generate proof
        # steps in reverse order, this means that in the normal proof sequence,
        # we add these chi inputs to the UNIFORM SET at this step.
        for c in seq_c[-1]:
            remaining_chi.remove(c)
    return seq_c, seq_t

# Main
# Read result file generated by 'glitch_list_generation.py'
with open('glitch_list.json', 'r') as file:
    state_array = json.load(file)
    state_array = [[[[[tuple(index) for index in share]
                      for share in state]
                     for state in lane]
                    for lane in sheet]
                   for sheet in state_array]

    # Generate proofs for every probe and corresponding theta, chi inputs
    proofs = []
    leaks = []
    for x, sheet in enumerate(state_array):
        for y, lane in enumerate(sheet):
            for z, state in enumerate(lane):
                for s, index_list in enumerate(state):
                    # Generate all chi inputs and all theta inputs
                    # used by registers in index_list
                    chi_list = []
                    theta_list = []
                    for index in set(index_list+[(x, y, z, s // 2)]):
                        # (x, y, z, s // 2) represent domain (s // 2)
                        # at (x,y,z), which includes two registers
                        # (x,y,z,s) and (x,y,z,s^1).
                        # Here, we assume a stronger adversary who possesses
                        # knowledge of the values in both registers,
                        # in order to mitigate program modifications.
                        c, t = chi_theta_inputs(index)
                        chi_list += c
                        theta_list += t
                    chi_list = list(set(chi_list))
                    theta_list = list(set(theta_list))

                    # Indices before rho and pi
                    chi_origin = [index_backwards(index) for index in chi_list]
                    theta_origin = [index_backwards(
                        index) for index in theta_list]

                    # Generate proof
                    seq_c, seq_t = proof_sequence_gen(chi_origin, theta_origin)

                    if len(seq_c) == 0: # Generation failed
                        leaks.append(((x, y, z, s), chi_origin, theta_origin))
                    else: # Generation succeeded
                        proofs.append(((x, y, z, s), chi_origin,
                                       theta_origin, seq_c, seq_t))

    print(f'Successfully generated proof steps for {len(proofs)}' +
          f' glitch+transition-extended probes,')
    print(f'and encountered failures in {len(leaks)} cases.')

    # Save proofs to file
    with open('glitch+trans_ct_uniform_proofs.json', 'w') as file2:
        json.dump(proofs, file2)
