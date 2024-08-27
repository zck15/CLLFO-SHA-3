# glitch_list_generation, generate glitch-extended probing index list.
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


def chi_before_reg(state_array, state_in):
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
    # Additional parts in our gadgets
    for y in range(5):
        for z in range(W):
            # Changing Of The Guard (COTG)
            j = W * y + z
            if (j > 0):
                jj = (j - 11) % (5 * W)
                yy = jj // W
                zz = jj % W
                state_array[0][y][z][0] += A[0][yy][zz][0]
                state_array[0][y][z][3] += A[0][yy][zz][0]
                state_array[1][y][z][0] += A[1][yy][zz][0]
                state_array[1][y][z][3] += A[1][yy][zz][0]
            # Use theta inputs as pseudo-randomness
            state_array[0][y][z][0] += I[0][y][z][0]
            state_array[0][y][z][1] += I[0][y][z][0]
            state_array[0][y][z][2] += I[0][y][z][1]
            state_array[0][y][z][3] += I[0][y][z][1]
    return state_array

# Main
state_array = init_state() # Initialize index list for theta inputs
state_array = theta(state_array)
state_array = rho(state_array)
state_array = pi(state_array)

# Backup a theta input list for use in chi
state_in = init_state()
# Bypass theta
state_in = rho(state_in)
state_in = pi(state_in)

state_array = chi_before_reg(state_array, state_in)

# Save results to file
with open('glitch_list.json', 'w') as file:
    json.dump(state_array, file)

# Print runtime result information to console
print(f'Generated index lists for {len(state_array)}x{len(state_array[0])}' +
      f'x{len(state_array[0][0])}' +
      f'x{len(state_array[0][0][0])} glitch-extended probes.')
