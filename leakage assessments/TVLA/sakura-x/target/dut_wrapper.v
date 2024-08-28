// dut_wrapper, wrapper of the dut top module for BSV interface
// Copyright (C) 2024, Cankun Zhao, Leibo Liu. All rights reserved.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
// ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTERS BE LIABLE FOR ANY
// DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
// INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION HOWEVER CAUSED AND
// ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// INCLUDING NEGLIGENCE OR OTHERWISE ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
// Please see LICENSE and README for license and further instructions.
//
// Contact: zhaock97@gmail.com

module dut_wrapper(
    input  wire              clk,
    input  wire              rst,
    input  wire              rst_n,
    input  wire [     2-1:0] r,
    input  wire [2*1600-1:0] din,  // Input shares concatenateed to each other
    output wire [2*1600-1:0] dout,  // Output shares concatenateed to each other
    output wire              dout_vld,
    input  wire              din_vld,
    input  wire              r_vld,
    input  wire              rst_vld
);
  


  keccak_top u_keccak_top(
    .clk            (clk),
    .rst_n          (~rst),
    .random_i       (r[2-1:0]),
    .din_share0_i   (din[1600-1:0]),
    .din_share1_i   (din[3200-1:1600]),
    .dout_share0_o  (dout[1600-1:0]),
    .dout_share0_o  (dout[3200-1:1600]),
    .dout_vld_o     (dout_vld)
  );

endmodule