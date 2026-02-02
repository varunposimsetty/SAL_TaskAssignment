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