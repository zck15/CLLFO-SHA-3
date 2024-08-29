# myttest, library for tvla experiment
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
from scared import traces
import time
import myprotocol as prot
import mybytes
import logging

logger = logging.getLogger(__name__)

ONOFF   = {True:'on', False:'off'}

def comm_test(sakura):
    resp = int.from_bytes(prot.ctrl_acq(sakura, 'Test'), byteorder='big')
    if prot.CtrlResp['Test'] == resp:
        logger.info('Communication test with Ctrl FPGA passed')
    else:
        logger.error(f'Communication test with Ctrl FPGA failed. '
            f'Ref. result: {prot.CtrlResp["Test"]}. '
            f'Exp. result: {resp}.')
    resp = int.from_bytes(prot.main_acq(sakura, 'Test'), byteorder='big')
    if prot.MainResp['Test'] == resp:
        logger.info('Communication test with Main FPGA passed')
    else:
        logger.error(f'Communication test with Main FPGA failed. '
            f'Ref. result: {prot.MainResp["Test"]}. '
            f'Exp. result: {resp}.')

def enc_test(sakura, pln_list, answer, prngon=False, seed=None):
    prot.main_instr(sakura, 'RstAll')
    prot.ctrl_instr(sakura, 'RstAll')
    for i, pln in enumerate(pln_list):
        prot.main_trans_bytes(sakura, f'PlnSh{i}', pln, byteorder='big')
    if prngon:
        prot.main_trans_bytes(sakura, 'Seed', seed,  byteorder='big')
        prot.main_instr(sakura, 'InitPRNG')
        prot.main_instr(sakura, 'RandOn')
    else:
        prot.main_instr(sakura, 'RandOff')
    prot.main_instr(sakura, 'StartEnc')
    f_done = sakura.read(3)
    cph_list = []
    ciphertext = b'\x00' * len(answer)
    for i in range(len(pln_list)):
        cph_list.append(prot.main_acq_bytes(sakura, f'CphSh{i}', len(answer), 
            byteorder='big'))
        ciphertext = mybytes.bytes_xor(ciphertext, cph_list[i])
    if answer == ciphertext:
        logger.info(f'Encryption test with PRNG {ONOFF[prngon]} passed')
    else:
        logger.error(f'Encryption test with PRNG {ONOFF[prngon]} failed.\n'
            f'Answer: {answer}.\n'
            f'Result: {ciphertext}.\n'
            f'Shares: {cph_list}')

def seq_test(sakura, n_seq, fix_pln, seed_coin, 
    seed_share=None, seed_main=None, n_shares=1, prngon=False):
    prng_coin  = trivium_coin(seed_coin, n_seq)
    prot.main_instr(sakura, 'RstAll')
    prot.ctrl_instr(sakura, 'RstAll')
    prot.ctrl_trans_bytes(sakura, 'FixPln',   fix_pln)
    prot.ctrl_trans_bytes(sakura, 'SeedCoin', seed_coin)
    if prngon:
        prot.ctrl_trans_bytes(sakura, 'SeedShare', seed_share)
        prot.main_trans_bytes(sakura, 'Seed',      seed_main)
        prot.main_instr(sakura, 'RandOn')
        prot.main_instr(sakura, 'InitPRNG')
    else:
        prot.main_instr(sakura, 'RandOff')
    prot.ctrl_trans(sakura, 'ShareNum', n_shares)
    prot.ctrl_instr(sakura, 'InitPRNG')
    prot.ctrl_trans(sakura, 'SeqNum',   n_seq)
    prot.ctrl_instr(sakura, 'StartSeq')
    res_ref = prng_coin.check()[2]                  # ref result
    res_exp = sakura.read(3)[1:]                    # experimental result
    if res_ref == res_exp:
        logger.info(f'Sequence mode test with PRNG {ONOFF[prngon]} passed')
    else:
        logger.error(f'Sequence mode test with PRNG {ONOFF[prngon]} failed.\n'
            f'Ref. result: {res_ref}.\n'
            f'Exp. result: {res_exp}.')

def reset_ttest(sakura, n_seq, fix_pln, prngon, n_shares,
    seed_coin=None, seed_share=None, seed_main=None):
    if seed_coin == None:
        seed_coin = mybytes.randbytes(20)
    if seed_share == None:
        seed_share = mybytes.randbytes(20)
    if seed_main == None:
        seed_main = mybytes.randbytes(20)

    # send reset instructions
    prot.main_instr(sakura, 'RstAll')
    prot.ctrl_instr(sakura, 'RstAll')

    # store plaintext of fixed subset
    prot.ctrl_trans_bytes(sakura, 'FixPln',    fix_pln)

    # initialize prng
    prot.ctrl_trans_bytes(sakura, 'SeedCoin',  seed_coin)
    prot.ctrl_trans_bytes(sakura, 'SeedShare', seed_share)
    prot.main_trans_bytes(sakura, 'Seed',      seed_main)
    prot.main_instr(sakura, 'InitPRNG')
    prot.ctrl_instr(sakura, 'InitPRNG')

    # Configure PRNG ON/OFF
    if prngon:
        prot.main_instr(sakura, 'RandOn')
    else:
        prot.main_instr(sakura, 'RandOff')

    prot.ctrl_trans(sakura, 'ShareNum', n_shares)
    prot.ctrl_trans(sakura, 'SeqNum',   n_seq)

    return trivium_coin(seed_coin, n_seq)

def sequence(wav, sakura, prng_coin, etsa, etsb):
    wav.single()
    wav.ready()
    prot.ctrl_instr(sakura, 'StartSeq')
    ind_r, ind_f, res_ref = prng_coin.check()
    res_exp = sakura.read(3)[1:]
    if res_exp != res_ref: # CTRL PRNG运行错误
        logger.error(f'Ctrl coin PRNG error in Loop {i}\n'
            f'ref prng: {res_ref}\n'
            f'exp prng: {res_exp}')
    else:
        try:
            wav.wait()
        except Exception as e:
            logger.error(f'Error when wav.wait()\n{e}', exc_info=True)
            wav.scope.disconnect()
            time.sleep(1)
        
        cnt_error = 0
        flag_error = 1
        while flag_error==1 and cnt_error<10:
            try:
                if not wav.scope.connected:
                    wav.scope.reconnect()
                trs = wav.acquire_samples_high_speed()
                flag_error = 0
            except Exception as e:
                logger.error(f'Error when acq samples\n{e}', exc_info=True)
                wav.scope.disconnect()
                time.sleep(1)
                cnt_error += 1
                continue
        if cnt_error == 10:
            raise RuntimeError('continuous 10 errors')
        thsa = traces.read_ths_from_ram(samples=trs[ind_r])
        thsb = traces.read_ths_from_ram(samples=trs[ind_f])
        etsa.add_trace_header_set(thsa)
        etsb.add_trace_header_set(thsb)

class trivium():
    """trivium-based DRBG"""
    def __init__(self, seed, speed=8, pln_len=16):
        assert speed <= 64, 'speed最大64'
        assert ((4*288) % speed) == 0, 'speed应是(4*288)的因数' 
        self.speed = speed
        self.pln_len = pln_len
        self.reg = _np.zeros((288), dtype=bool)
        self.zi  = _np.zeros((speed), dtype=bool)
        self.reg[0:80] = uint8_bool(seed[:10])
        self.reg[93:173] = uint8_bool(seed[10:])
        self.reg[285:] = True
        self.update((4*288)//self.speed)
        self.update(1)
        print("This is an old version.\n"
            + "For bsv version, please use trivium_coin instead.")

    def update(self, num=1):
        w = self.speed

        for i in range(num):
            t1 = self.reg[ 66-w: 66] ^ self.reg[ 93-w: 93]
            t2 = self.reg[162-w:162] ^ self.reg[177-w:177]
            t3 = self.reg[243-w:243] ^ self.reg[288-w:288]
            
            a1 = self.reg[ 91-w: 91] & self.reg[ 92-w: 92]
            a2 = self.reg[175-w:175] & self.reg[176-w:176]
            a3 = self.reg[286-w:286] & self.reg[287-w:287]

            zi = t1 ^ t2 ^ t3

            s1 = t1 ^ a1 ^ self.reg[171-w:171]
            s2 = t2 ^ a2 ^ self.reg[264-w:264]
            s3 = t3 ^ a3 ^ self.reg[ 69-w: 69]

            self.reg = _np.roll(self.reg, w)

            self.reg[  0:  0+w] = s3
            self.reg[ 93: 93+w] = s1
            self.reg[177:177+w] = s2

        self.zi = zi

    def get_bit(self):
        b = self.zi[0]
        self.update()
        return int(b)

    def get_pln(self):
        pln = _np.empty((self.pln_len), dtype=_np.uint8)
        for i in range(self.pln_len):
            pln[i] = self.state()
            self.update()
        return pln

    def state(self):
        return bool_uint8(self.zi)
        
def uint8_bool(array):
    res = []
    for byte in array:
        for i in list('{:08b}'.format(byte)):
            if i == '1':
                res.append(True)
            else:
                res.append(False)
    return _np.array(res[::-1], dtype=bool)

def bool_uint8(array):
    assert (len(array) % 8) == 0, 'array长度应为8的倍数'
    len_uint8 = len(array) // 8
    res = _np.zeros((len_uint8), dtype=_np.uint8)
    weight = 2 ** _np.arange(8, dtype=_np.uint8)
    for i in range(len_uint8):
        res[len_uint8-1-i] = _np.sum(weight[array[i*8:i*8+8]])
    return res


class trivium_coin():
    """trivium-based DRBG for coin generation"""
    def __init__(self, seed, n_seq):
        assert type(seed) == bytes, "seed should be bytes"
        assert len(seed) == 20, "seed should be 160bits, i.e., 20bytes"
        # self.speed = 1
        self.n_seq = n_seq
        self.ind_ran = None
        self.ind_fix = None
        self.coins   = None
        self.reg = _np.zeros((288), dtype=bool)
        self.reg[0:80] = bytes_bool(seed[:10])
        self.reg[93:173] = bytes_bool(seed[10:])
        self.reg[285:] = True
        self.update(4*288)

    def update(self, num=1):
        for i in range(num):
            t1 = self.reg[ 66-1] ^ self.reg[ 93-1]
            t2 = self.reg[162-1] ^ self.reg[177-1]
            t3 = self.reg[243-1] ^ self.reg[288-1]
            
            a1 = self.reg[ 91-1] & self.reg[ 92-1]
            a2 = self.reg[175-1] & self.reg[176-1]
            a3 = self.reg[286-1] & self.reg[287-1]

            zi = t1 ^ t2 ^ t3

            s1 = t1 ^ a1 ^ self.reg[171-1]
            s2 = t2 ^ a2 ^ self.reg[264-1]
            s3 = t3 ^ a3 ^ self.reg[ 69-1]

            self.reg = _np.roll(self.reg, 1)

            self.reg[  0] = s3
            self.reg[ 93] = s1
            self.reg[177] = s2
        return zi

    def update_acc(self, num=1):
        # About 40 times faster than update()
        wl = [64 for i in range(num//64)]
        res = _np.zeros((num), dtype=bool)
        if (num % 64) != 0:
            wl.append(num % 64)
        for i, w in enumerate(wl):
            t1 = self.reg[ 66-w: 66] ^ self.reg[ 93-w: 93]
            t2 = self.reg[162-w:162] ^ self.reg[177-w:177]
            t3 = self.reg[243-w:243] ^ self.reg[288-w:288]
            
            a1 = self.reg[ 91-w: 91] & self.reg[ 92-w: 92]
            a2 = self.reg[175-w:175] & self.reg[176-w:176]
            a3 = self.reg[286-w:286] & self.reg[287-w:287]

            zi = t1 ^ t2 ^ t3

            s1 = t1 ^ a1 ^ self.reg[171-w:171]
            s2 = t2 ^ a2 ^ self.reg[264-w:264]
            s3 = t3 ^ a3 ^ self.reg[ 69-w: 69]

            self.reg = _np.roll(self.reg, w)

            self.reg[  0:  0+w] = s3
            self.reg[ 93: 93+w] = s1
            self.reg[177:177+w] = s2

            res[i*64:i*64+w] = zi[::-1]

        return res

    def check(self):
        self.ind_ran = self.update_acc(self.n_seq)
        self.ind_fix = ~self.ind_ran
        coins = self.update_acc(16)
        self.coins = int(coins.tobytes().hex()[1::2],2).to_bytes(2,'big')
        return self.ind_ran, self.ind_fix, self.coins
            
def bytes_bool(b):
    s = '{:0' + str(len(b)*8) + 'b}'
    res = [i=='1' for i in list(s.format(int(b.hex(), 16)))]
    return _np.array(res[::-1], dtype=bool)
