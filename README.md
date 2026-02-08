# SAL_TaskAssignment

This repository contains the **RTL-implementation, verification, synthesis, and implementation results** of the hardware design tasks assigned as part of the **SAL technical assignment**.

The work focuses on a **parametric, pipelined INT8 MAC unit** and its integration using two different system-level control approaches:
- a **stalled (FSM-based) approach**
- a **streaming (non-stalled) pipelined approach**

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Task 1 – MAC Unit](#task-1--mac-unit)
- [Task 2 – System Integration](#task-2--system-integration)
- [Register Map](#register-map)
- [Repository Structure](#repository-structure)
- [Build & Simulation](#build--simulation)
- [Verification](#verification)
- [Synthesis & Implementation](#synthesis--implementation)
- [Notes](#notes)

---
## Overview

The goal of this assignment is to design and verify a **hardware MAC accelerator** suitable for quantized edge-AI workloads.

The implementation includes:
- A **3-stage pipelined MAC datapath** for computing a dot product of INT8 vectors
- A **custom memory-mapped register interface**
- Two alternative control strategies:
  - **Streaming (non-stalled)** integration
  - **FSM-based stalled** integration
- Functional verification using **waveform inspection** (GTKWave) and **cocotb** (Python-based verification)

The repository includes:
- RTL implementations in **VHDL and SystemVerilog**
- Verification using **VHDL and SystemVerilog testbenches**
- Python-based verification using **cocotb**
- Timing, utilization, synthesis, and implementation reports generated using **Xilinx Vivado**
---

## Features

- Parametric data width and vector length  
- Signed INT8 arithmetic  
- Fixed-latency pipelined datapath  
- RTL implementations in VHDL and SystemVerilog  
- Multiple verification methodologies  
- FPGA synthesis and implementation reports  
---

## Task 1 – MAC Unit

### Description

The MAC unit computes the dot product of two vectors:
- Vector length: 4  
- Data type: signed INT8  
- Output width: 18 bits (overflow-safe)

### Pipeline Stages

1. **Stage 1 – Parallel multiplication**  
   Four parallel INT8 × INT8 multipliers

2. **Stage 2 – Partial sum tree**  
   Pairwise addition of partial products

3. **Stage 3 – Final accumulation**  
   Produces the final dot-product result

### Interface

- `i_start` launches a computation  
- `o_valid` asserts when the result is ready  
- Fixed pipeline latency of **3 clock cycles**
---

## Task 2 – System Integration

The MAC unit is integrated using a **custom register-based control interface**.  
Two system-level integration variants are provided:

### 1) FSM-Based (Stalled) Integration
- Explicit FSM controlling the compute lifecycle
- No read/write access during computation
- Single compute operation active at a time
- Predictable and well-defined execution flow

### 2) Streaming (Non-Stalled) Integration
- Allows continuous COMPUTE commands
- MAC pipeline can accept new work every cycle
- Results are written to a single result register
- Assumes ordered access by the control unit
---

## Register Map

| Address | Name   | Access | Description |
|--------:|--------|--------|-------------|
| `0x00`  | STATUS | R      | Busy / Done status |
| `0x01`  | VEC_A  | W      | Packed vector A (4 × INT8) |
| `0x02`  | VEC_B  | W      | Packed vector B (4 × INT8) |
| `0x03`  | RESULT | R      | MAC output (18-bit signed) |

The table above shows the register mapping used for system integration.
---

## Repository Structure

<details>
<summary><strong>Repository Structure</strong></summary>

``` bash
SAL_TaskAssignment/
├── README.md
├── .gitignore
│
├── doc/
│ ├── Freiberger - Task Assignment Combined.docx
│ ├── RegisterMapping.xlsx
| └── Varun_Posimsetty_SAL_Presentation.pptx
│
├── reports_stream/
│ ├── synth_drc.txt
│ ├── synth_power.txt
│ ├── synth_timing_summary.txt
│ ├── synth_utilization.txt
│ ├── impl_check_timing.txt
│ ├── impl_clock_utilization.txt
│ ├── impl_drc.txt
│ ├── impl_power.txt
│ ├── impl_route_status.txt
│ ├── impl_timing_summary.txt
│ └── impl_utilization.txt
│
├── reports_stalled/
│ ├── synth_drc.txt
│ ├── synth_power.txt
│ ├── synth_timing_summary.txt
│ ├── synth_utilization.txt
│ ├── impl_check_timing.txt
│ ├── impl_clock_utilization.txt
│ ├── impl_drc.txt
│ ├── impl_power.txt
│ ├── impl_route_status.txt
│ ├── impl_timing_summary.txt
│ └── impl_utilization.txt
│
├── sv_port/
│ ├── src/
│ │ ├── mac_unit.sv
│ │ └── TopModule.sv
│ └── sim/
│ ├── compSim.sh
│ ├── run.sh
│ ├── tb_top.sv
│ └── work/
│ └── result.gtkw
│
├── vhdl_impl/
│ ├── global/
│ │ └── TaskGlobalPackage.vhd
│ │
│ ├── src/
│ │ ├── mac_unit.vhd
│ │ ├── register_map.vhd
│ │ └── register_map_stalled.vhd
│ │
│ ├── wrapper/
│ │ └── mac_unit_wrapper.vhd
│ │
│ ├── sim/
│ │ ├── compSim.sh
│ │ ├── run.sh
│ │ ├── tb_mac_unit.vhd
│ │ ├── tb_register_map.vhd
│ │ └── work/
│ │ ├── result.gtkw
│ │ └── result_top.gtkw
│ │
│ └── cocotb_tests/
│ ├── Makefile
│ ├── run.sh
│ ├── test_mac_unit_wrapper.py
│ ├── test_top_module.py
│ ├── mac_unit.gtkw
│ ├── top_module.gtkw
│ └── error.log
```
</details>
---

## Build & Simulation

### VHDL Simulation
The VHDL implementation can be compiled and simulated using **GHDL**.

```bash
cd vhdl_impl/sim
./compSim.sh
```
### SystemVerilog Simulation
The SystemVerilog implementation includes its own simulation scripts.
```bash 
cd sv_port/sim
./run.sh
```
- Waveforms are generated and can be viewed using GTKWave.
--- 
## Verification
Functional verification was performed using multiple complementary approaches:
- Waveform-based functional verification using GTKWave
- RTL testbenches written in VHDL and SystemVerilog
- Python-based verification using cocotb applied to the VHDL implementation

The cocotb testbenches were used to apply multiple test vectors, including signed INT8 edge cases and randomized test cases, to verify correct pipeline behavior across repeated compute operations.

- Waveform files generated during simulation are available in the corresponding ```sim/work/``` and ```cocotb_tests/``` directories.
---
## Synthesis & Implementation
The VHDL implementation was synthesized and implemented using **Xilinx Vivado**.
The following reports were generated as part of the flow:
- Synthesis reports
- Timing analysis reports
- Resource utilization reports
- Implementation and routing reports
All generated reports are stored in the ```reports_stream/``` and ```reports_stalled``` directory.
--- 
## Notes
- Two system-level integration approaches are included to illustrate different architectural tradeoffs.
- The stalled FSM-based integration enforces serialized execution, while the streaming integration allows continuous operation.
- The repository reflects the complete design flow from RTL implementation to verification and FPGA implementation.



