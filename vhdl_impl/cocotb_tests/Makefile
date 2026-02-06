SIM = ghdl
TOPLEVEL_LANG = vhdl
#TOPLEVEL = mac_unit_wrapper
#COCOTB_TEST_MODULES = test_mac_unit_wrapper
TOPLEVEL = topmodule
COCOTB_TEST_MODULES = test_top_module
SIM_ARGS = --wave=waveform.ghw
#GTKW_SAVE = mac_unit.gtkw
GTKW_SAVE = top_module.gtkw

# Force use of Intel GHDL
GHDL_BIN_DIR = /Users/varunposimsetty/Downloads/ghdl-mcode-5.1.1-macos13-x86_64/bin

VHDL_SOURCES = $(PWD)/../global/TaskGlobalPackage.vhd
VHDL_SOURCES += $(PWD)/../src/mac_unit.vhd
VHDL_SOURCES += $(PWD)/../wrapper/mac_unit_wrapper.vhd
VHDL_SOURCES += $(PWD)/../src/register_map.vhd
VHDL_SOURCES += $(PWD)/../src/register_map_stalled.vhd

GHDL_ARGS = --std=08
SIM_ARGS = --wave=waveform.ghw

include $(shell cocotb-config --makefiles)/Makefile.sim

view:
	gtkwave waveform.ghw $(GTKW_SAVE) &
run:
	$(MAKE)
	$(MAKE) view
clean::
	rm -rf sim_build __pycache__ results.xml *.ghw *.vcd *.o *.cf