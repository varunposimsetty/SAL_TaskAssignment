#!/bin/bash
cd /Users/varunposimsetty/Desktop/SAL_TaskAssignment/vhdl_impl/cocotb_tests/
rm -rf sim_build
mkdir -p sim_build

GHDL=/opt/homebrew/bin/ghdl

$GHDL -a --std=08 --workdir=sim_build --work=work ../global/TaskGlobalPackage.vhd
$GHDL -a --std=08 --workdir=sim_build --work=work ../src/mac_unit.vhd
$GHDL -a --std=08 --workdir=sim_build --work=work ../src/register_map.vhd
$GHDL -a --std=08 --workdir=sim_build --work=work ../src/register_map_stalled.vhd
$GHDL -e --std=08 --workdir=sim_build -Psim_build --work=work mac_unit

COCOTB_TEST_MODULES=test_mac_unit COCOTB_TOPLEVEL=mac_unit TOPLEVEL_LANG=vhdl $GHDL -r --std=08 --workdir=sim_build -Psim_build --work=work mac_unit --vpi=/Users/varunposimsetty/Desktop/SAL_TaskAssignment/vhdl_impl/venv/lib/python3.9/site-packages/cocotb/libs/libcocotbvpi_ghdl.so --wave=waveform.ghw
