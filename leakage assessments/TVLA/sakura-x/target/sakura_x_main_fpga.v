// sakura_x_main_fpga, top module for sakura-x main fpga
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

module sakura_x_main_fpga (
  // clock & reset
  clk_osc_p    ,
  clk_osc_n    ,
  clk_osc_inh_n,
  c2m_rst_n    ,

  // peripheral devices on board
  led          ,
  sma_trigger  ,
  dipsw        ,
  gpio         ,

  // ports for mkMainFPGA
  device_rdy   ,
  c2m_din      ,
  c2m_en_lvl   ,
  c2m_done_lvl ,
  m2c_dout     ,
  m2c_en_lvl   ,
  m2c_done_lvl
);
  // clock & reset
  input           clk_osc_p     ;
  input           clk_osc_n     ;
  output          clk_osc_inh_n ;
  input           c2m_rst_n     ;

  // peripheral devices on board
  output  [ 9:0]  led           ;
  output          sma_trigger   ;
  input   [ 7:0]  dipsw         ;
  output  [ 3:0]  gpio          ;

  // ports for mkMainFPGA
  output          device_rdy    ;
  input   [15:0]  c2m_din       ;
  input           c2m_en_lvl    ;
  output          c2m_done_lvl  ;
  output  [15:0]  m2c_dout      ;
  output          m2c_en_lvl    ;
  input           m2c_done_lvl  ;

  // internal wires
  wire            clk           ;
  wire            rst_n         ;
  wire    [ 7:0]  clk_cfg       ;
  wire            trigger       ;

  reg     [23:0]  clk_monitor_cnt ;
  reg             clk_monitor     ;

  // clock
  assign clk_osc_inh_n = 1'b1;

  mkClkRst mk_clk_rst(
    .clk_in_p     (clk_osc_p    ),
    .clk_in_n     (clk_osc_n    ),
    .rst_n_in     (c2m_rst_n    ),
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

  // sma_trigger
  assign sma_trigger = trigger;

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
  mkMainFPGA main_fpga(
    .clk          (clk          ),
    .rst_n        (rst_n        ),
    .c2m_din      (c2m_din      ),
    .c2m_en_lvl   (c2m_en_lvl   ),
    .c2m_done_lvl (c2m_done_lvl ),
    .m2c_dout     (m2c_dout     ),
    .m2c_en_lvl   (m2c_en_lvl   ),
    .m2c_done_lvl (m2c_done_lvl ),
    .device_rdy   (device_rdy   ),
    .trigger      (trigger      )
  );

endmodule // sakura_x_main_fpga

module mkClkRst (clk_in_p, clk_in_n, rst_n_in, clk_cfg, clk, rst_n);
  input       clk_in_p, clk_in_n, rst_n_in;
  input [7:0] clk_cfg;
  output      clk, rst_n;

  wire        clk_ref;
  reg   [6:0] clk_cnt_max;
  reg   [6:0] clk_cnt;
  reg         clk_div;
  wire        clk_sel;

  reg   [3:0] rst_cnt;

  IBUFGDS clk_in_buf (.I(clk_in_p), .IB(clk_in_n), .O(clk_ref));

  always @(*) begin
    case (clk_cfg)
      // 8'h01 : clk_cnt_max =   1 - 1; //   10ns, 100MHz
      // 8'h02 : clk_cnt_max =   2 - 1; //   20ns,  50MHz
      // 8'h04 : clk_cnt_max =   5 - 1; //   50ns,  20MHz
      // 8'h08 : clk_cnt_max =  10 - 1; //  100ns,  10MHz
      // 8'h10 : clk_cnt_max =  20 - 1; //  200ns,   5MHz
      // 8'h20 : clk_cnt_max =  50 - 1; //  500ns,   2MHz
      // 8'h40 : clk_cnt_max = 100 - 1; // 1000ns,   1MHz
      8'h01 : clk_cnt_max =   1 - 1; //   10ns, 100.0MHz
      8'h02 : clk_cnt_max =   2 - 1; //   20ns,  50.0MHz
      8'h04 : clk_cnt_max =   8 - 1; //   80ns,  12.5MHz
      8'h08 : clk_cnt_max =  10 - 1; //  100ns,  10.0MHz
      8'h10 : clk_cnt_max =  20 - 1; //  200ns,   5.0MHz
      8'h20 : clk_cnt_max =  50 - 1; //  500ns,   2.0MHz
      8'h40 : clk_cnt_max = 100 - 1; // 1000ns,   1.0MHz
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
    else if (~&rst_cnt) rst_cnt <= rst_cnt + 4'd1;
    else                rst_cnt <= rst_cnt;
  end

  assign rst_n = &rst_cnt;

endmodule // mkClkRst