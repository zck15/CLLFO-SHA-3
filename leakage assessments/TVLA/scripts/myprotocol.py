# myprotocol, wrapper of custom protocol for SAKURA
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
import rtoml
import serial # pyserial
import numpy as _np

tomlfile = open("protocol.toml", "rt")
protocol = rtoml.load(tomlfile)
tomlfile.close()

for k, v in protocol.items():
    if k == "description":
        continue
    elif v["type"] == "synonym":
        continue
    elif v["type"] == "enum":
        globals()[k] = v["member"]
    elif v["type"] == "struct":
        continue
    elif v["type"] == "function":
        continue
    else:
        raise ValueError("Unknown format")

def main_instr(ser, instr):
    assert instr in MainInstr, "Unknown main instruction!"
    msg_int = FPGALabel[ 'Main']
    msg_int =   MsgType['Instr'] + (msg_int <<  2)
    msg_int = MainInstr[  instr] + (msg_int << 14)
    ser.write(msg_int.to_bytes(3, byteorder='big'))

def main_acq(ser, addrid, index=0, byteorder='big'):
    assert addrid in MainAddrID, "Unknown main address id!"
    assert (index <= 0x7f) and (index >= 0), "Invalid index!"
    assert (byteorder=='big') or (byteorder=='little'), "Invalid byteorder!"    
    msg_int =  FPGALabel['Main']
    msg_int =    MsgType[ 'Acq'] + (msg_int << 2)
    msg_int = MainAddrID[addrid] + (msg_int << 7)
    msg_int =              index + (msg_int << 7)
    ser.write(msg_int.to_bytes(3, byteorder='big'))
    if int.from_bytes(ser.read(1), byteorder='big') != FPGALabel['Main']:
        print("You should flush the serial buffer before invoke this function")
        return
    if byteorder == 'big':
        return ser.read(2)
    else:
        return ser.read(2)[::-1]

def main_trans(ser, addrid, index, data=None, byteorder='big'):
    if data == None: # input arg. are (ser, addrid, data), index = 0
        data = index
        index = 0
    assert addrid in MainAddrID, "Unknown main address id!"
    assert (index <= 0x7f) and (index >= 0), "Invalid index!"
    assert (byteorder=='big') or (byteorder=='little'), "Invalid byteorder!"    
    if type(data) == bytes:
        data = int.from_bytes(data, byteorder=byteorder)
    assert (data <= 0xffff) and (data >= 0), "Invalid data!"
    msg_int =  FPGALabel[ 'Main']
    msg_int =    MsgType['Trans'] + (msg_int <<  2)
    msg_int = MainAddrID[ addrid] + (msg_int <<  7)
    msg_int =               index + (msg_int <<  7)
    msg_int =                data + (msg_int << 16)
    ser.write(msg_int.to_bytes(5, byteorder='big'))

def ctrl_instr(ser, instr):
    assert instr in CtrlInstr, "Unknown ctrl instruction!"
    msg_int = FPGALabel[ 'Ctrl']
    msg_int =   MsgType['Instr'] + (msg_int <<  2)
    msg_int = CtrlInstr[  instr] + (msg_int << 14)
    ser.write(msg_int.to_bytes(3, byteorder='big'))

def ctrl_acq(ser, addrid, index=0, byteorder='big'):
    assert addrid in CtrlAddrID, "Unknown ctrl address id!"
    assert (index <= 0x7f) and (index >= 0), "Invalid index!"
    assert (byteorder=='big') or (byteorder=='little'), "Invalid byteorder!"
    msg_int =  FPGALabel['Ctrl']
    msg_int =    MsgType[ 'Acq'] + (msg_int << 2)
    msg_int = CtrlAddrID[addrid] + (msg_int << 7)
    msg_int =              index + (msg_int << 7)
    ser.write(msg_int.to_bytes(3, byteorder='big'))
    if int.from_bytes(ser.read(1), byteorder='big') != FPGALabel['Ctrl']:
        print("You should flush the serial buffer before invoke this function")
        return
    if byteorder == 'big':
        return ser.read(2)
    else:
        return ser.read(2)[::-1]

def ctrl_trans(ser, addrid, index, data=None, byteorder='big'):
    if data == None: # input arg. are (ser, addrid, data), index = 0
        data = index
        index = 0
    assert addrid in CtrlAddrID, "Unknown ctrl address id!"
    assert (index <= 0x7f) and (index >= 0), "Invalid index!"
    assert (byteorder=='big') or (byteorder=='little'), "Invalid byteorder!"
    if type(data) == bytes:
        data = int.from_bytes(data, byteorder=byteorder)
    assert (data <= 0xffff) and (data >= 0), "Invalid data!"
    msg_int =  FPGALabel[ 'Ctrl']
    msg_int =    MsgType['Trans'] + (msg_int <<  2)
    msg_int = CtrlAddrID[ addrid] + (msg_int <<  7)
    msg_int =               index + (msg_int <<  7)
    msg_int =                data + (msg_int << 16)
    ser.write(msg_int.to_bytes(5, byteorder='big'))

def main_acq_bytes(ser, addrid, num_bytes, byteorder='big'):
    assert addrid in MainAddrID, "Unknown main address id!"
    assert (num_bytes <= 256) and (num_bytes >= 1), "Invalid num_bytes!"
    assert (byteorder=='big') or (byteorder=='little'), "Invalid byteorder!"
    b = b''
    for index in range((num_bytes-1)//2, -1, -1):
        b += main_acq(ser, addrid, index, 'big')
    if (num_bytes % 2) == 1:
        b = b[1:]
    if byteorder == 'little':
        b = b[::-1]
    return b

def ctrl_acq_bytes(ser, addrid, num_bytes, byteorder='big'):
    assert addrid in CtrlAddrID, "Unknown ctrl address id!"
    assert (num_bytes <= 256) and (num_bytes >= 1), "Invalid num_bytes!"
    assert (byteorder=='big') or (byteorder=='little'), "Invalid byteorder!"
    b = b''
    for index in range((num_bytes-1)//2, -1, -1):
        b += ctrl_acq(ser, addrid, index, 'big')
    if (num_bytes % 2) == 1:
        b = b[1:]
    if byteorder == 'little':
        b = b[::-1]
    return b
    
def main_trans_bytes(ser, addrid, data, byteorder='big'):
    assert addrid in MainAddrID, "Unknown main address id!"
    assert type(data) == bytes, "Data should be bytes!"
    num_bytes = len(data)
    assert (num_bytes <= 256) and (num_bytes >= 1), "Invalid num_bytes!"
    assert (byteorder=='big') or (byteorder=='little'), "Invalid byteorder!"
    if byteorder == 'big':
        data = data[::-1]
    if (num_bytes % 2) == 1:
        data = data + b'\x00'
    for index in range((num_bytes+1)//2):
        main_trans(ser, addrid, index, data[2*index:2*index+2], 'little')

def ctrl_trans_bytes(ser, addrid, data, byteorder='big'):
    assert addrid in CtrlAddrID, "Unknown ctrl address id!"
    assert type(data) == bytes, "Data should be bytes!"
    num_bytes = len(data)
    assert (num_bytes <= 256) and (num_bytes >= 1), "Invalid num_bytes!"
    assert (byteorder=='big') or (byteorder=='little'), "Invalid byteorder!"
    if byteorder == 'big':
        data = data[::-1]
    if (num_bytes % 2) == 1:
        data = data + b'\x00'
    for index in range((num_bytes+1)//2):
        ctrl_trans(ser, addrid, index, data[2*index:2*index+2], 'little')