# Keccak_verilator_makefile, makefile for functional simulation of Keccak.
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

# Specify the path to Verilator, if it is not in your PATH environment variable
VERILATOR = verilator

# Verilog source code directory
SRC_RTL_DIR = ./src_rtl

# Verilog source files
VERILOG_SRCS = $(SRC_RTL_DIR)/keccak_top.v $(SRC_RTL_DIR)/keccak_comp_iota.v \
    $(SRC_RTL_DIR)/keccak_chi_pr.v $(SRC_RTL_DIR)/keccak_state.v \
    $(SRC_RTL_DIR)/keccak_theta_rho_pi.v $(SRC_RTL_DIR)/keccak_rho_pi.v \
    $(SRC_RTL_DIR)/keccak_control.v $(SRC_RTL_DIR)/keccak_roundconstant.v

# KAT files directory
KAT_DIR = ./KAT

# C++ simulation source files directory
SRC_TB_DIR = ./src_tb

# C++ simulation source files
SIM_SRC = $(SRC_TB_DIR)/sim_main.cpp

# Generated executable file
EXE = sim_main

# Verilator output directory
BUILD_DIR = ./build

# Simulation VCD file
VCD = waveform.vcd

# C++ compiler
CXX = g++

# C++ compile options
CXXFLAGS = -Wall -Wno-unused-variable -std=c++11 -I$(BUILD_DIR)


# Generate C++ in executable form
VERILATOR_FLAGS += -cc --exe
# Generate makefile dependencies (not shown as complicates the Makefile)
#VERILATOR_FLAGS += -MMD
# Optimize
VERILATOR_FLAGS += -x-assign fast
# Warn about lint issues; may not want this on less solid designs
VERILATOR_FLAGS += -Wall
# Make waveforms
VERILATOR_FLAGS += --trace
# Check SystemVerilog assertions
VERILATOR_FLAGS += --assert
# Generate coverage analysis
VERILATOR_FLAGS += --coverage
# Run Verilator in debug mode
#VERILATOR_FLAGS += --debug
# Add this trace to get a backtrace in gdb
# VERILATOR_FLAGS += --gdbbt

# Target: Default to generate all KAT test targets
all: $(EXE) run_tests

# Target: Compile Verilog and C++ source files
$(EXE): $(VERILOG_SRCS) $(SIM_SRC)
	@echo
	@echo "-- VERILATE ----------------"
	@mkdir -p $(BUILD_DIR)
	$(VERILATOR) $(VERILATOR_FLAGS) $(SIM_SRC) $(VERILOG_SRCS) --Mdir $(BUILD_DIR)

	@echo
	@echo "-- BUILD -------------------"
	$(MAKE) -j -C $(BUILD_DIR) -f Vkeccak_top.mk
	mv $(BUILD_DIR)/Vkeccak_top $(EXE)

# Target: Run all KAT tests
run_tests: run_SHA3_224 run_SHA3_256 run_SHA3_384 run_SHA3_512 run_SHAKE128 run_SHAKE256

run_SHA3_224:
	@echo "Running SHA3-224 test..."
	./$(EXE) $(KAT_DIR)/SHA3_224ShortMsg.rsp

run_SHA3_256:
	@echo "Running SHA3-256 test..."
	./$(EXE) $(KAT_DIR)/SHA3_256ShortMsg.rsp

run_SHA3_384:
	@echo "Running SHA3-384 test..."
	./$(EXE) $(KAT_DIR)/SHA3_384ShortMsg.rsp

run_SHA3_512:
	@echo "Running SHA3-512 test..."
	./$(EXE) $(KAT_DIR)/SHA3_512ShortMsg.rsp

run_SHAKE128:
	@echo "Running SHAKE128 test..."
	./$(EXE) $(KAT_DIR)/SHAKE128ShortMsg.rsp

run_SHAKE256:
	@echo "Running SHAKE256 test..."
	./$(EXE) $(KAT_DIR)/SHAKE256ShortMsg.rsp

# Target: Clean generated files
clean:
	@rm -rf $(BUILD_DIR) $(EXE) $(VCD)

.PHONY: all clean run_tests run_SHA3_224 run_SHA3_256 run_SHA3_384 run_SHA3_512 run_SHAKE128 run_SHAKE256
