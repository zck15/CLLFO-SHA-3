# mybytes, bytes processing
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
import secrets
def bytes_xor(b1, b2):
    assert type(b1) is bytes, "b1 is not bytes"
    assert type(b2) is bytes, "b2 is not bytes"
    return bytes([_b1 ^ _b2 for _b1, _b2 in zip(b1, b2)])

def loadhextxt(filename):
    res = []
    file = open(filename, 'rt')
    for line in file.readlines():
        line = line.strip()
        res.append(bytes.fromhex(line))
    return res

def randbytes(n):
    return secrets.token_bytes(n)