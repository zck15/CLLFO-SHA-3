// sakura_x_ctrl_fpga, top module for sakura-x ctrl fpga
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

module sakura_x_ctrl_fpga (
  // clock & reset
  clk_osc         ,
  clk_osc_inh_n   ,
  rst_power_on_n  ,
  rst_push_switch ,

  // peripheral devices on board
  led             ,
  dipsw           ,
  gpio            ,

  // ports for mkCtrlFPGA
  usb_dio         ,
  usb_rxf         ,
  usb_txe         ,
  usb_rd          ,
  usb_wr          ,
  usb_siwua       ,
  usb_rst_n       ,

  c2m_rst_n       ,
  c2m_dout        ,
  c2m_en_lvl      ,
  c2m_done_lvl    ,
  m2c_din         ,
  m2c_en_lvl      ,
  m2c_done_lvl    ,
  device_rdy
);
  // clock & reset
  input           clk_osc         ;
  output          clk_osc_inh_n   ;
  input           rst_power_on_n  ;
  input           rst_push_switch ;

  // peripheral devices on board
  output  [ 9:0]  led             ;
  input   [ 7:0]  dipsw           ;
  output  [ 3:0]  gpio            ;

  // ports for mkCtrlFPGA
  inout   [ 7:0]  usb_dio         ;
  input           usb_rxf         ;
  input           usb_txe         ;
  output          usb_rd          ;
  output          usb_wr          ;
  output          usb_siwua       ;
  output          usb_rst_n       ;

  output          c2m_rst_n       ;
  output  [15:0]  c2m_dout        ;
  output          c2m_en_lvl      ;
  input           c2m_done_lvl    ;
  input   [15:0]  m2c_din         ;
  input           m2c_en_lvl      ;
  output          m2c_done_lvl    ;
  input           device_rdy      ;

  // internal wires
  wire            clk             ;
  wire            rst_ext_n       ;
  wire            rst_n           ;
  wire    [ 7:0]  clk_cfg         ;
  wire    [ 7:0]  usb_din         ;
  wire    [ 7:0]  usb_dout        ;
  wire            usb_dio_oe      ;

  reg     [23:0]  clk_monitor_cnt ;
  reg             clk_monitor     ;

  // setting
  assign clk_osc_inh_n = 1'b1;
  assign usb_siwua     = 1'b0;

  // clock & reset
  assign rst_ext_n     = ~(~rst_power_on_n | rst_push_switch);
  assign usb_rst_n     = rst_ext_n;
  assign c2m_rst_n     = rst_n;

  mkClkRst mk_clk_rst(
    .clk_in       (clk_osc      ),
    .rst_n_in     (rst_ext_n    ),
    .clk_cfg      (clk_cfg      ),
    .clk          (clk          ),
    .rst_n        (rst_n        )
  );

  // peripheral devices on board
  // led
  assign led[0] = clk_monitor;
  assign led[1] = 1'b0;
  assign led[2] = 1'b0;
  assign led[3] = 1'b0;
  assign led[4] = 1'b0;
  assign led[5] = 1'b0;
  assign led[6] = 1'b0;
  assign led[7] = 1'b0;
  assign led[8] = 1'b0;
  assign led[9] = 1'b0;

  // dipsw
  assign clk_cfg = dipsw;

  // gpio
  assign gpio[0] = 1'b0;
  assign gpio[1] = 1'b0;
  assign gpio[2] = 1'b0;
  assign gpio[3] = 1'b0;

  // clk monitor
  always @(posedge clk or negedge rst_n) begin
    if(~rst_n) begin
      clk_monitor_cnt <= 24'd0;
      clk_monitor     <= 1'b0;
    end else if (clk_monitor_cnt == (24'd12_000_000 - 24'd1)) begin
      clk_monitor_cnt <= 24'd0;
      clk_monitor     <= ~clk_monitor;
    end else begin
      clk_monitor_cnt <= clk_monitor_cnt + 24'd1;
      clk_monitor     <= clk_monitor;
    end
  end

  // bsv generated core
  assign usb_dio = usb_dio_oe ? usb_dout : 8'hzz;
  assign usb_din = usb_dio;

  mkCtrlFPGA ctrl_fpga(
    .clk          (clk          ),
    .rst_n        (rst_n        ),
    .usb_din      (usb_din      ),
    .usb_rxf      (usb_rxf      ),
    .usb_txe      (usb_txe      ),
    .usb_dout     (usb_dout     ),
    .usb_rd       (usb_rd       ),
    .usb_wr       (usb_wr       ),
    .usb_dio_oe   (usb_dio_oe   ),
    .c2m_dout     (c2m_dout     ),
    .c2m_en_lvl   (c2m_en_lvl   ),
    .c2m_done_lvl (c2m_done_lvl ),
    .m2c_din      (m2c_din      ),
    .m2c_en_lvl   (m2c_en_lvl   ),
    .m2c_done_lvl (m2c_done_lvl ),
    .device_rdy   (device_rdy   )
  );

endmodule // sakura_x_ctrl_fpga

module mkClkRst (clk_in, rst_n_in, clk_cfg, clk, rst_n);
  input       clk_in, rst_n_in;
  input [7:0] clk_cfg;
  output      clk, rst_n;

  wire        clk_ref;
  reg   [6:0] clk_cnt_max;
  reg   [6:0] clk_cnt;
  reg         clk_div;
  wire        clk_sel;

  reg  [15:0] rst_cnt;

  IBUFG clk_in_buf (.I(clk_in), .O(clk_ref));

  always @(*) begin
    case (clk_cfg)
      8'h01 : clk_cnt_max =   1 - 1; // 24MHz /  2 = 12MHz
      8'h02 : clk_cnt_max =   2 - 1; // 24MHz /  4 =  6MHz
      8'h04 : clk_cnt_max =   3 - 1; // 24MHz /  6 =  4MHz
      8'h08 : clk_cnt_max =   4 - 1; // 24MHz /  8 =  3MHz
      8'h10 : clk_cnt_max =   6 - 1; // 24MHz / 12 =  2MHz
      8'h20 : clk_cnt_max =  12 - 1; // 24MHz / 24 =  1MHz
      default : clk_cnt_max = 0;
    endcase
  end

  always @(posedge clk_ref or negedge rst_n_in) begin
    if(~rst_n_in) begin
      clk_cnt <= 0;
      clk_div <= 0;
    end else if (clk_cnt==clk_cnt_max) begin
      clk_cnt <= 0;
      clk_div <= ~clk_div;
    end else begin
      clk_cnt <= clk_cnt + 7'd1;
      clk_div <= clk_div;
    end
  end

  assign clk_sel = (clk_cfg == 8'h00) ? clk_ref : clk_div;
  
  BUFG global_clock_buf (.I(clk_sel), .O(clk));

  always @(posedge clk or negedge rst_n_in) begin
    if(~rst_n_in)       rst_cnt <= 0;
    else if (~&rst_cnt) rst_cnt <= rst_cnt + 16'd1;
    else                rst_cnt <= rst_cnt;
  end

  assign rst_n = &rst_cnt;

endmodule // mkClkRst