# synthesis_dc, synthesis script for DC.
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

set VER zhao
set TOP keccak_top
set CLK_PERIOD 1.700
set LIB typical
set REPORT zhao_keccak_top_CLK_PERIOD_1.700_typical_autoWLM_dc_main

source -e -v ../../run/library_setup_dc.tcl

set hdlin_check_no_latch true
set verilogout_no_tri true
set_app_var hdlin_reporting_level comprehensive
set hdlin_infer_multibit default_all
set do_operand_isolation true
 
echo $file_list
analyze -format sverilog $file_list
elaborate $TOP
current_design $TOP
link
uniquify

set_operating_conditions -lib NangateOpenCellLibrary $LIB

change_names -rules verilog -hier -verbose > report/$TOP.change_name.before_compile

source -e -v ../../constraint/con_$TOP\_$VER.tcl
change_names -rules verilog -hier -verbose > report/$TOP.change_name.after_cons

compile_ultra -exact_map -no_autoungroup

change_names -rules verilog -hier -verbose > report/$TOP.change_name.after_compile

report_area -hier > report/$TOP.area-hier.rpt

ungroup -all -flatten

write -f ddc -hier -o db/$TOP.ddc
write -f verilog -hier -o db/$TOP.v
write_sdc  report/$TOP.sdc
write_sdf  report/$TOP.sdf

sh date

report_clock -group > report/$TOP.clk.rpt
report_clock -skew >> report/$TOP.clk.rpt
all_registers -level_sensitive > report/$TOP.latch.rpt
report_qor -significant_digits 3 > report/$TOP.qor.rpt
report_timing -trans -nets -delay max -max_paths 3000 -slack_lesser_than 0.00 -nosplit -sort_by group -significant_digits 3 > report/$TOP.report_timing
report_constraint -significant_digits 3 -all_violators -max_delay > report/$TOP.violation
report_area -hier > report/$TOP.area.rpt
report_power -nosplit -verbose > report/$TOP.power.rpt
