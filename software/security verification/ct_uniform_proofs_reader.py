# ct_uniform_proofs_reader, read proof steps of uniformity of 
# (\hat v^{n-1}[...], \hat s'^{n-1}[...])
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
import argparse

if __name__ == "__main__":
    # Arguments parsing
    parser = argparse.ArgumentParser(
        description="index of the glitch-robust probe")
    parser.add_argument('fn', type=str, help='file name of the proofs')
    parser.add_argument('x', type=int, help='x-coordinate of the probe')
    parser.add_argument('y', type=int, help='y-coordinate of the probe')
    parser.add_argument('z', type=int, help='z-coordinate of the probe')
    parser.add_argument('s', type=int, help='share (register number) of the probe')
    args = parser.parse_args()
    probe_index = (args.x, args.y, args.z, args.s)

    # with open('glitch+trans_ct_uniform_proofs.json', 'r') as file:
    # with open('glitch_ct_uniform_proofs.json', 'r') as file:
    with open(args.fn, 'r') as file:
        proofs = json.load(file)
        # Extract the indices of probes in the proof
        index_list = [tuple(proof[0]) for proof in proofs]
        # Check if the target probe exists
        if probe_index in index_list:
            i = index_list.index(probe_index)
            _, chi_origin, theta_origin, seq, seq_r = proofs[i]
            print(f"Index of the glitch-extended probe: {probe_index}")
            print(f"Indices of v^{{n-1}} before rho and pi (theta output " +
                  f"t^{{n-1}}):\n{chi_origin}")
            print(f"Indices of s'^{{n-1}} before rho and pi (theta input " +
                  f"s^{{n-1}}):\n{theta_origin}")
            print(f"---------------------------------------------------------")
            print("Proof for uniformity of (v^{n-1}[...], s'^{n-1}[...]):")
            print(f"- Current uniform set consists of all the theta inputs " +
                  f"s: {theta_origin}")
            for n in range(len(seq)):
                step = n + 1
                print(f"- Step {step}")
                print(f"  - Utilizing independent theta inputs s: " +
                      f"{seq_r[-step]}")
                print(f"  - Add to uniform set these theta outputs t: " +
                      f"{seq[-step]}")
        else:
            print(f"Proof for probe {probe_index} does not exist!")
