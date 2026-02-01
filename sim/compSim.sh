#!/bin/bash
WORK_DIR=work
WAVE_FILE=result.ghw
GTKPROJ_FILE=result.gtkw
STD="--std=08"

mkdir -p $WORK_DIR

# importing source files
ghdl -i $STD --workdir=$WORK_DIR ../global/TaskGlobalPackage.vhd
ghdl -i $STD --workdir=$WORK_DIR ../src/mac_unit.vhd
ghdl -i $STD --workdir=$WORK_DIR ./tb_mac_unit.vhd

# building simulation files
ghdl -m $STD --workdir=$WORK_DIR tb

# running the simulation
ghdl -r $STD --workdir=$WORK_DIR tb --wave=$WORK_DIR/$WAVE_FILE --stop-time=1ms

if [ -f $WORK_DIR/$GTKPROJ_FILE ]; then
   gtkwave $WORK_DIR/$GTKPROJ_FILE &
else
   gtkwave $WORK_DIR/$WAVE_FILE &
fi
