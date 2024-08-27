// sim_main, testbench required for Verilator simulation.
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

#include <iostream>
#include <fstream>
#include <string>
#include <unordered_map>
#include <bitset>
#include <random>
#include <verilated.h>
#include <verilated_vcd_c.h>
#include "Vkeccak_top.h"

std::string get_test_function(const std::string& filename) {
    static std::unordered_map<std::string, std::string> kat_to_function = {
        {"./KAT/SHA3_224ShortMsg.rsp", "SHA3-224"},
        {"./KAT/SHA3_256ShortMsg.rsp", "SHA3-256"},
        {"./KAT/SHA3_384ShortMsg.rsp", "SHA3-384"},
        {"./KAT/SHA3_512ShortMsg.rsp", "SHA3-512"},
        {"./KAT/SHAKE128ShortMsg.rsp", "SHAKE128"},
        {"./KAT/SHAKE256ShortMsg.rsp", "SHAKE256"}
    };
    
    auto it = kat_to_function.find(filename);
    if (it != kat_to_function.end()) {
        return it->second;
    } else {
        return "UNKNOWN";
    }
}

std::bitset<1600> pad_message(const std::string& msg, int len, const std::string& test_function) {
    std::bitset<1600> padded_msg;
    int msg_index = 0;
    int bit_index = 0;

    while (msg_index < msg.size() && bit_index < len) {
        int byte_value = std::stoi(msg.substr(msg_index, 2), nullptr, 16);
        int bit_value = (byte_value >> (bit_index % 8)) & 1;
        padded_msg.set(bit_index, bit_value);
        bit_index++;
        
        if (bit_index % 8 == 0) {
            msg_index += 2;
        }
    }

    if (test_function.substr(0, 4) == "SHA3") {
        padded_msg.set(bit_index, 0);
        bit_index++;
        padded_msg.set(bit_index, 1);
        bit_index++;
    } else {
        padded_msg.set(bit_index, 1);
        bit_index++;
        padded_msg.set(bit_index, 1);
        bit_index++;
        padded_msg.set(bit_index, 1);
        bit_index++;
        padded_msg.set(bit_index, 1);
        bit_index++;
    }

    padded_msg.set(bit_index, 1);
    bit_index++;
    while (bit_index < 1600) {
        if (bit_index == 1600 - 2 * std::stoi(test_function.substr(5,3)) - 1) {
            padded_msg.set(bit_index, 1);
        } else {
            padded_msg.set(bit_index, 0);
        }
        bit_index++;
    }

    return padded_msg;
}

bool compare_output(const std::bitset<1600>& dout, const std::string& output_str, const std::string& test_function) {
    int output_len = (output_str.size() - 1) * 4;
    std::bitset<1600> expected_output;

    int str_index = 0;
    int bit_index = 0;

    while (str_index < (output_str.size() - 1)) {
        int byte_value = std::stoi(output_str.substr(str_index, 2), nullptr, 16);
        int bit_value = (byte_value >> (bit_index % 8)) & 1;
        expected_output.set(bit_index, bit_value);
        bit_index++;
        
        if (bit_index % 8 == 0) {
            str_index += 2;
        }
    }

    for (int i = 0; i < output_len; ++i) {
        if (dout[i] != expected_output[i]) {
            return false;
        }
    }
    return true;
}

int main(int argc, char **argv, char **env) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <KAT file>" << std::endl;
        return -1;
    }

    std::string kat_filename = argv[1];
    std::string test_function = get_test_function(kat_filename);
    int len_max = 1600 - 2 * std::stoi(test_function.substr(5,3)) - 2 - 2;
    if (test_function.substr(0, 5) == "SHAKE") len_max -= 2;


    Verilated::commandArgs(argc, argv);
    Vkeccak_top* top = new Vkeccak_top;

    Verilated::traceEverOn(true);
    VerilatedVcdC* tfp = new VerilatedVcdC;
    top->trace(tfp, 99);
    tfp->open("waveform.vcd");

    std::ifstream kat_file(argv[1]);
    if (!kat_file.is_open()) {
        std::cerr << "Error: Could not open KAT file." << std::endl;
        return -1;
    }
    if (test_function == "UNKNOWN") {
        std::cerr << "Error: Unknown KAT file." << std::endl;
        return -1;
    }

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 1);

    std::string line;
    int sim_time = 0;
    while (std::getline(kat_file, line)) {
        if (line.empty()) {
            continue;
        }
        if (line.find("Len = ") != std::string::npos) {
            int len = std::stoi(line.substr(6));
            std::getline(kat_file, line);
            std::string msg_str = line.substr(6);
            std::getline(kat_file, line);
            std::string output_str;
            if (test_function.substr(0, 4) == "SHA3") {
                output_str = line.substr(5);
            } else {
                output_str = line.substr(9);
            }

            if (len > len_max) {
                break;
            }

            std::bitset<1600> din = pad_message(msg_str, len, test_function);

            std::bitset<1600> din_share0, din_share1;
            for (size_t i = 0; i < 1600; i++) {
                din_share0[i] = dis(gen); // Generate a random bit
                din_share1[i] = din[i] ^ din_share0[i];
            }

            std::bitset<2> random_i;
            random_i[0] = dis(gen);
            random_i[1] = dis(gen);

            top->clk = 0;
            top->rst_n = 0;
            top->random_i = static_cast<CData>(random_i.to_ulong());
            std::string din_share0_str = din_share0.to_string();
            std::string din_share1_str = din_share1.to_string();
            for (int i = 0; i < 50; ++i) {
                std::bitset<32> temp32_share0(din_share0_str.substr((49 - i) * 32, 32));
                top->din_share0_i[i] = static_cast<WData>(temp32_share0.to_ulong());
                std::bitset<32> temp32_share1(din_share1_str.substr((49 - i) * 32, 32));
                top->din_share1_i[i] = static_cast<WData>(temp32_share1.to_ulong());
            }

            // Reset cycle
            for (int i = 0; i < 3; i++) {
                top->clk = !top->clk;
                top->rst_n = 0;
                top->eval();
                tfp->dump(sim_time++);
            }

            top->rst_n = 1;

            // Main simulation loop
            for (int i = 3; i < 1000; i++) {
                top->clk = !top->clk;
                if (top->clk == 0) {
                    random_i[0] = dis(gen);
                    random_i[1] = dis(gen);
                    top->random_i = static_cast<CData>(random_i.to_ulong());
                }
                top->eval();
                tfp->dump(sim_time++);
                if (top->dout_vld_o) {
                    top->clk = !top->clk;
                    top->eval();
                    tfp->dump(sim_time++);
                    break;
                }
            }

            // Compare output
            std::bitset<1600> dout_share0;
            std::bitset<1600> dout_share1;
            for (int i = 0; i < 50; ++i)
            {
                for (int j = 0; j < 32; ++j)
                {
                    dout_share0.set(i * 32 + j, (top->dout_share0_o[i] >> j) & 1);
                    dout_share1.set(i * 32 + j, (top->dout_share1_o[i] >> j) & 1);
                }
            }
            std::bitset<1600> dout(dout_share0 ^ dout_share1);

            bool result = compare_output(dout, output_str, test_function);
            if (result) {
                std::cout << "Pass #" << len << "; ";

            } else {
                std::cerr << std::endl << "Test failed for Len = " << len << std::endl;
            }
        }        
    }

    kat_file.close();

    top->final();
    tfp->close();
    delete top;
    return 0;
}
