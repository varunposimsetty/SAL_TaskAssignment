library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library work;
use work.TaskGlobalPackage.all;

entity mac_unit_wrapper is
    generic(
        DATA_WIDTH : natural := 8;
        LENGTH : natural := 4
    );
    port(
        i_clk       : in std_ulogic;
        i_nrst_sync : in std_ulogic;
        i_start     : in std_ulogic;
        i_vecA_0    : in signed(DATA_WIDTH-1 downto 0);
        i_vecA_1    : in signed(DATA_WIDTH-1 downto 0);
        i_vecA_2    : in signed(DATA_WIDTH-1 downto 0);
        i_vecA_3    : in signed(DATA_WIDTH-1 downto 0);
        i_vecB_0    : in signed(DATA_WIDTH-1 downto 0);
        i_vecB_1    : in signed(DATA_WIDTH-1 downto 0);
        i_vecB_2    : in signed(DATA_WIDTH-1 downto 0);
        i_vecB_3    : in signed(DATA_WIDTH-1 downto 0);
        o_result    : out signed((2*DATA_WIDTH + ceil_log2(LENGTH))-1 downto 0);
        o_valid     : out std_ulogic
    );
end entity;

architecture RTL of mac_unit_wrapper is
    signal vecA : tvector(0 to LENGTH-1)(DATA_WIDTH-1 downto 0);
    signal vecB : tvector(0 to LENGTH-1)(DATA_WIDTH-1 downto 0);
begin
    vecA(0) <= i_vecA_0;
    vecA(1) <= i_vecA_1;
    vecA(2) <= i_vecA_2;
    vecA(3) <= i_vecA_3;
    vecB(0) <= i_vecB_0;
    vecB(1) <= i_vecB_1;
    vecB(2) <= i_vecB_2;
    vecB(3) <= i_vecB_3;
    mac_inst: entity work.mac_unit
    generic map(DATA_WIDTH => DATA_WIDTH, LENGTH => LENGTH)
    port map(
        i_clk => i_clk,
        i_nrst_sync => i_nrst_sync,
        i_start => i_start,
        i_vecA => vecA,
        i_vecB => vecB,
        o_result => o_result,
        o_valid => o_valid
    );
end architecture;