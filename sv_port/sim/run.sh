#!/bin/bash

# Configuration
TOP_MODULE="tb_top"
SRC_DIR="../src"

# 1. Clean up
rm -rf obj_dir
rm -f dump.vcd

echo "Building Simulation with Waveform Support..."

# 2. Build
verilator --binary --timing --trace -Wno-fatal \
    -I$SRC_DIR \
    $SRC_DIR/TopModule.sv \
    $SRC_DIR/mac_unit.sv \
    tb_top.sv \
    --top-module $TOP_MODULE

# 3. Execute
if [ $? -eq 0 ]; then
    echo "Running Simulation..."
    ./obj_dir/V$TOP_MODULE
    
    # 4. Open Waveform
    if [ -f "dump.vcd" ]; then
        echo "Opening GTKWave..."
        open -a gtkwave dump.vcd || gtkwave dump.vcd
    else
        echo "Error: dump.vcd was not generated. Check tb_top.sv for \$dumpvars."
    fi
else
    echo "Build failed."
    exit 1
fi