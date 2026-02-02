library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library work;
use work.TaskGlobalPackage.all;

entity tb is
end entity;

architecture sim of tb is
    signal clk    : std_ulogic := '0';
    signal rst    : std_ulogic := '0';
    signal start  : std_ulogic := '0';
    signal vecA   : tvector(0 to 3)(7 downto 0) := (others => (others => '0'));
    signal vecB   : tvector(0 to 3)(7 downto 0) := (others => (others => '0'));
    signal result : signed(17 downto 0);
    signal valid  : std_ulogic;

begin

  dut: entity work.mac_unit(RTL)
    generic map (
      DATA_WIDTH => 8,
      LENGTH     => 4
    )
    port map (
      i_clk       => clk,
      i_nrst_sync => rst,
      i_start     => start,
      i_vecA      => vecA,
      i_vecB      => vecB,
      o_result    => result,
      o_valid     => valid
    );

    proc_clk : process is 
    begin 
        wait for 5 ns;
        clk <= not clk;
    end process proc_clk;

    proc_tb : process is 
    begin 
        wait for 10 ns;
        rst <= '1';
        wait for 30 ns;
        start <='1';
        wait for 13 ns;
        vecA(0) <= x"01";
        wait for 10 ns;
        vecB(0) <= x"01";
        wait for 20 ns;
        vecA(1) <= x"0A";
        wait for 20 ns;
        vecB(1) <= x"01";
        wait for 60 ns;
        rst <= '0';
        wait for 100 ns;
        rst <= '1';
        wait for 20 ns;
        vecB(1) <= x"1F";
        wait for 20 ns;
        vecA(2) <= x"7F";
        wait for 20 ns;
        vecB(2) <= x"FF";
        wait for 30 ns;
        vecA(3) <= x"E0";
        wait for 20 ns;
        vecB(3) <= x"80";
        wait for 200 ns;
        wait;
    end process proc_tb;
end architecture;
