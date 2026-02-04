#!/bin/bash
WORK_DIR=work
WAVE_FILE=result.vcd
GTKPROJ_FILE=result.gtkw
TOP_MODULE=tb_top

rm -rf $WORK_DIR
mkdir -p $WORK_DIR

echo "Creating work library..."
vlib $WORK_DIR
vmap work $WORK_DIR

echo "Compiling sources..."
vlog -sv -work $WORK_DIR ../src/mac_unit.sv || exit 1
vlog -sv -work $WORK_DIR ../src/TopModule.sv || exit 1
vlog -sv -work $WORK_DIR ./tb_top.sv || exit 1

echo "Running simulation..."
vsim -c -do "run 2us; quit -f" work.$TOP_MODULE

echo "Launching GTKWave..."
if [ -f "$WORK_DIR/$WAVE_FILE" ]; then
    if [ -f "$WORK_DIR/$GTKPROJ_FILE" ]; then
        gtkwave "$WORK_DIR/$WAVE_FILE" "$WORK_DIR/$GTKPROJ_FILE" &
    else
        gtkwave "$WORK_DIR/$WAVE_FILE" &
        echo ">>> TIP: Save signal arrangement to $WORK_DIR/$GTKPROJ_FILE"
    fi
else
    echo "Add \$dumpfile/\$dumpvars to testbench!"
fi

echo "Done!"