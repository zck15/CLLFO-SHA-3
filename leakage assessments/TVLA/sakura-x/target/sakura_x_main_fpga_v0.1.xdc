# sakura_x_main_fpga, constraint file for sakura-x main fpga
# Copyright (C) 2024, Cankun Zhao, Leibo Liu. All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTERS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# INCLUDING NEGLIGENCE OR OTHERWISE ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Please see LICENSE and README for license and further instructions.
#
# Contact: zhaock97@gmail.com

create_clock -name clk_osc -period 5 [get_ports { clk_osc_p }]
create_generated_clock -name clk -source [get_ports clk_osc_p] -divide_by 1 [get_pins mk_clk_rst/global_clock_buf/O]


#================================================ Pin assignment
#################
# CLOCK / RESET #
#################
set_property -dict { PACKAGE_PIN AC2  IOSTANDARD DIFF_HSTL_I } [get_ports { clk_osc_n }]
set_property -dict { PACKAGE_PIN AB2  IOSTANDARD DIFF_HSTL_I } [get_ports { clk_osc_p }]

set_property -dict { PACKAGE_PIN J8   IOSTANDARD LVCMOS25    } [get_ports { clk_osc_inh_n }]

set_property -dict { PACKAGE_PIN H17  IOSTANDARD LVCMOS25    } [get_ports { sma_trigger }]

##########
# Switch #
##########
set_property -dict { PACKAGE_PIN J21  IOSTANDARD LVCMOS25    } [get_ports { dipsw[0] }]
set_property -dict { PACKAGE_PIN N19  IOSTANDARD LVCMOS25    } [get_ports { dipsw[1] }]
set_property -dict { PACKAGE_PIN M16  IOSTANDARD LVCMOS25    } [get_ports { dipsw[2] }]
set_property -dict { PACKAGE_PIN M20  IOSTANDARD LVCMOS25    } [get_ports { dipsw[3] }]
set_property -dict { PACKAGE_PIN L17  IOSTANDARD LVCMOS25    } [get_ports { dipsw[4] }]
set_property -dict { PACKAGE_PIN N24  IOSTANDARD LVCMOS25    } [get_ports { dipsw[5] }]
set_property -dict { PACKAGE_PIN K21  IOSTANDARD LVCMOS25    } [get_ports { dipsw[6] }]
set_property -dict { PACKAGE_PIN E21  IOSTANDARD LVCMOS25    } [get_ports { dipsw[7] }]

#######
# LED #
#######
set_property -dict { PACKAGE_PIN G20  IOSTANDARD LVCMOS25    } [get_ports { led[0] }]
set_property -dict { PACKAGE_PIN L19  IOSTANDARD LVCMOS25    } [get_ports { led[1] }]
set_property -dict { PACKAGE_PIN K18  IOSTANDARD LVCMOS25    } [get_ports { led[2] }]
set_property -dict { PACKAGE_PIN H19  IOSTANDARD LVCMOS25    } [get_ports { led[3] }]
set_property -dict { PACKAGE_PIN K15  IOSTANDARD LVCMOS25    } [get_ports { led[4] }]
set_property -dict { PACKAGE_PIN P16  IOSTANDARD LVCMOS25    } [get_ports { led[5] }]
set_property -dict { PACKAGE_PIN T19  IOSTANDARD LVCMOS25    } [get_ports { led[6] }]
set_property -dict { PACKAGE_PIN T18  IOSTANDARD LVCMOS25    } [get_ports { led[7] }]
set_property -dict { PACKAGE_PIN H12  IOSTANDARD LVCMOS25    } [get_ports { led[8] }]
set_property -dict { PACKAGE_PIN H11  IOSTANDARD LVCMOS25    } [get_ports { led[9] }]

########
# GPIO #
########
set_property -dict { PACKAGE_PIN D19  IOSTANDARD LVCMOS25    } [get_ports { gpio[0] }]
set_property -dict { PACKAGE_PIN N17  IOSTANDARD LVCMOS25    } [get_ports { gpio[1] }]
set_property -dict { PACKAGE_PIN N16  IOSTANDARD LVCMOS25    } [get_ports { gpio[2] }]
set_property -dict { PACKAGE_PIN P24  IOSTANDARD LVCMOS25    } [get_ports { gpio[3] }]

#############################################
# Spartan-6 HPIC (LVCMOS15, SSTL15 or HTSL) #
#############################################

set_property -dict { PACKAGE_PIN V4   IOSTANDARD LVCMOS15    } [get_ports { c2m_din[0] }]
set_property -dict { PACKAGE_PIN V2   IOSTANDARD LVCMOS15    } [get_ports { c2m_din[1] }]
set_property -dict { PACKAGE_PIN W1   IOSTANDARD LVCMOS15    } [get_ports { c2m_din[2] }]
set_property -dict { PACKAGE_PIN AB1  IOSTANDARD LVCMOS15    } [get_ports { c2m_din[3] }]
set_property -dict { PACKAGE_PIN Y3   IOSTANDARD LVCMOS15    } [get_ports { c2m_din[4] }]
set_property -dict { PACKAGE_PIN U7   IOSTANDARD LVCMOS15    } [get_ports { c2m_din[5] }]
set_property -dict { PACKAGE_PIN V3   IOSTANDARD LVCMOS15    } [get_ports { c2m_din[6] }]
set_property -dict { PACKAGE_PIN AF10 IOSTANDARD LVCMOS15    } [get_ports { c2m_din[7] }]
set_property -dict { PACKAGE_PIN AC13 IOSTANDARD LVCMOS15    } [get_ports { c2m_din[8] }]
set_property -dict { PACKAGE_PIN AE12 IOSTANDARD LVCMOS15    } [get_ports { c2m_din[9] }]
set_property -dict { PACKAGE_PIN U6   IOSTANDARD LVCMOS15    } [get_ports { c2m_din[10] }]
set_property -dict { PACKAGE_PIN AE13 IOSTANDARD LVCMOS15    } [get_ports { c2m_din[11] }]
set_property -dict { PACKAGE_PIN AA10 IOSTANDARD LVCMOS15    } [get_ports { c2m_din[12] }]
set_property -dict { PACKAGE_PIN AB12 IOSTANDARD LVCMOS15    } [get_ports { c2m_din[13] }]
set_property -dict { PACKAGE_PIN AA4  IOSTANDARD LVCMOS15    } [get_ports { c2m_din[14] }]
set_property -dict { PACKAGE_PIN AE8  IOSTANDARD LVCMOS15    } [get_ports { c2m_din[15] }]
set_property -dict { PACKAGE_PIN AD10 IOSTANDARD LVCMOS15    } [get_ports { c2m_rst_n }]
set_property -dict { PACKAGE_PIN Y13  IOSTANDARD LVCMOS15    } [get_ports { c2m_en_lvl }]
set_property -dict { PACKAGE_PIN AA13 IOSTANDARD LVCMOS15    } [get_ports { c2m_done_lvl }]

########################################
# Spartan-6 HRIC (LVCMOS25 or LVDS_25) #
########################################
set_property -dict { PACKAGE_PIN T22  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[0] }]
set_property -dict { PACKAGE_PIN M24  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[1] }]
set_property -dict { PACKAGE_PIN K25  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[2] }]
set_property -dict { PACKAGE_PIN R26  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[3] }]
set_property -dict { PACKAGE_PIN M25  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[4] }]
set_property -dict { PACKAGE_PIN U17  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[5] }]
set_property -dict { PACKAGE_PIN N26  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[6] }]
set_property -dict { PACKAGE_PIN R16  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[7] }]
set_property -dict { PACKAGE_PIN T20  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[8] }]
set_property -dict { PACKAGE_PIN R22  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[9] }]
set_property -dict { PACKAGE_PIN M21  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[10] }]
set_property -dict { PACKAGE_PIN T24  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[11] }]
set_property -dict { PACKAGE_PIN P23  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[12] }]
set_property -dict { PACKAGE_PIN N21  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[13] }]
set_property -dict { PACKAGE_PIN R21  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[14] }]
set_property -dict { PACKAGE_PIN N18  IOSTANDARD LVCMOS25    } [get_ports { m2c_dout[15] }]
set_property -dict { PACKAGE_PIN R18  IOSTANDARD LVCMOS25    } [get_ports { device_rdy }]
set_property -dict { PACKAGE_PIN U19  IOSTANDARD LVCMOS25    } [get_ports { m2c_en_lvl }]
set_property -dict { PACKAGE_PIN P19  IOSTANDARD LVCMOS25    } [get_ports { m2c_done_lvl }]


set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 2.5 [current_design]