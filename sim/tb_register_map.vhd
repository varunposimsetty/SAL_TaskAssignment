library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library work;
use work.TaskGlobalPackage.all;

entity tb_top is
end entity;

architecture sim of tb_top is
    signal clk    : std_ulogic := '0';
    signal rst    : std_ulogic := '0';
    signal instruction : std_ulogic_vector(1 downto 0) := (others => '0');
    signal address : std_ulogic_vector(1 downto 0) := (others => '0');
    signal wr_data : std_ulogic_vector(31 downto 0) := (others => '0');
    signal rd_data : std_ulogic_vector(31 downto 0) := (others => '0');

    begin 

    DUT : entity work.TopModuleStalled(RTL)
        generic map(
        DATA_WIDTH => 8,
        LENGTH     => 4,
        MEM_DEPTH  => 4,
        MEM_WIDTH  => 32
    )
    port map(
        i_clk         => clk,
        i_nrst        => rst,
        i_instruction => instruction,
        i_address     => address,
        i_wr_data     => wr_data,
        o_rd_data     => rd_data
    );

    proc_clk : process is 
    begin 
        wait for 5 ns;
        clk <= not clk;
    end process proc_clk;

    proc_tb : process is 
    begin 
        wait for 40 ns;
        rst <= '1';
        wait for 50 ns;
        instruction <= "01";
        address <= "11";
        wait for 20 ns;
        instruction <= "10";
        address <= "01";
        wr_data <= x"00000000";
        wait for 10 ns;
        address <= "10";
        wr_data <= x"00000000";
        wait for 10 ns;
        instruction <= "11";
        wait for 10 ns;
        instruction <= "00";
        wait for 40 ns;
        instruction <= "01";
        address <= "11";
        wait for 20 ns;
        instruction <= "10";
        address <= "01";
        wr_data <= x"01010101";
        wait for 10 ns;
        address <= "10";
        wr_data <= x"01010101";
        wait for 10 ns;
        instruction <= "11";
        wait for 10 ns;
        instruction <= "10";
        address <= "01";
        wr_data <= x"02020202";
        wait for 10 ns;
        address <= "10";
        wr_data <= x"02020202";
        wait for 10 ns;
        instruction <= "11";
        wait for 10 ns;
        instruction <= "00";
        wait for 60 ns;
        instruction <= "01";
        address <= "11";
        wait for 20 ns;
        instruction <= "01";
        address <= "00";  
        wait for 20 ns;
        instruction <= "10";
        address <= "01";
        wr_data <= x"AABBCCDD";
        wait for 10 ns;
        instruction <= "01";
        address <= "01";
        wait for 20 ns;        
        instruction <= "10";
        address <= "10";
        wr_data <= x"11223344";
        wait for 10 ns;
        instruction <= "01";
        address <= "10";
        wait for 20 ns;
        wait for 30 ns;
        instruction <= "11";
        wait for 50 ns;
        instruction <= "01";
        wait for 20 ns;
        address <= "11";
        wait for 60 ns;
        wait;
    end process proc_tb;
end architecture;

