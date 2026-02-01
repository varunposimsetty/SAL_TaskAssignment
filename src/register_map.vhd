library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity register_map is 
    generic(
        DEPTH : natural := 4;
        WIDTH : natural := 32
    );
    port(
        i_address : in std_ulogic_vector(ceil_log2(DEPTH)-1 downto 0);
        i_data    : in std_ulogic_vector(WIDTH-1 downto 0);
    );
end entity register_map;

architecture RTL of register_map is 
begin 

end architecture RTL;
