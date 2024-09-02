# collect_traces, collect traces for TVLA
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
# import packages
import sys
sys.path.append('.\\lib')
import scared
import serial
import myttest
import mybytes
from mywaverunner import WaveRunner
from tqdm import trange
from math import ceil
import logging
import logging.config
import rtoml

#### Configuration ###################################################
DUTNAME = 'keccak'
ASSESS  = 'ttest'
PRNGON  = True
NSHARES = 2
NTRACES = 300_000_000
NTRACES_GROUP = 100_000_000
FIXPLN  = 'r3f0'

ONOFF   = {True:'on', False:'off'}
TESTNAME = f'{DUTNAME}_{ASSESS}_p{ONOFF[PRNGON]}_{NTRACES}_{FIXPLN}'

with open('log_config.toml', 'r') as f:
    config = rtoml.load(f)
    logging.config.dictConfig(config)

logger = logging.getLogger('test')

#### Test #############################################################
logger.info(f'Start Test')

# Connect sakura
sakura = serial.Serial('COM9', 9600)

# Communication test
myttest.comm_test(sakura)

# Test vector for encryption test
plaintext0, plaintext1, answer0, answer1 = mybytes.loadhextxt('testvector_correct.txt') # read testvector
answer = mybytes.bytes_xor(answer0, answer1)

# Encryption test
myttest.enc_test(sakura, [plaintext0, plaintext1], answer, prngon=False)

myttest.enc_test(sakura, [plaintext0, plaintext1], answer, prngon=True, 
    seed=mybytes.randbytes(20))

# Sequence mode test
myttest.seq_test(sakura, n_seq=15000, fix_pln=mybytes.randbytes(200), 
    seed_coin=mybytes.randbytes(20), prngon=False)

myttest.seq_test(sakura, n_seq=15000, fix_pln=mybytes.randbytes(200),
    seed_coin=mybytes.randbytes(20), seed_share=mybytes.randbytes(20),
    seed_main=mybytes.randbytes(20), n_shares=NSHARES, prngon=True)

# Connect Oscilloscope
wav = WaveRunner('USB0::0x05FF::0x1023::4258N22140::INSTR') # connect
wav.open()
wav.set_config_from_file(f'param_{DUTNAME}_seq') 

# from fixpln_gen import fix_plns
# fix_pln = fix_plns[2]

fix_pln = mybytes.bytes_xor(plaintext0, plaintext1)

n_seq = wav.time['seq']

prng_coin = myttest.reset_ttest(sakura, n_seq, fix_pln, PRNGON, NSHARES)

etsa = scared.traces.ETSWriter(
    './traces/{}_random.ets'.format(TESTNAME), overwrite=True)
etsb = scared.traces.ETSWriter(
    './traces/{}_fixed.ets'.format(TESTNAME), overwrite=True)

logger.info(f'Start sequence')
cnt_r = 0
cnt_f = 0
try:
    for i in trange(ceil(NTRACES/n_seq)):
        try:
            n_r, n_f = myttest.sequence(wav, sakura, prng_coin, etsa, etsb)
            cnt_r += n_r
            cnt_f += n_f
        except RuntimeError as e:
            logger.error(f'Error in loop {i}\n{e}', exc_info=True)
            etsa.close()
            etsb.close()
            raise e
        if cnt_r > NTRACES_GROUP and cnt_f > NTRACES_GROUP:
            break

    etsa.close()
    etsb.close()

    logger.critical('Success')
except Exception as e:
    logger.critical(e, exc_info=True)
