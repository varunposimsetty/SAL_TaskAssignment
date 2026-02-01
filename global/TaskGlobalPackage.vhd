library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package TaskGlobalPackage is 
    type tvector is array (natural range <>) of signed;
    function ceil_log2(Arg : positive) return natural;
end package TaskGlobalPackage;

package body TaskGlobalPackage is
    -- source : https://www.edaboard.com/threads/moved-vhdl-log-base-2-function.242745/
    function ceil_log2(Arg : positive) return natural is
        variable v : natural := Arg - 1;  -- makes Arg=1 return 0
        variable r : natural := 0;
    begin
        while v > 0 loop
            v := v / 2;
            r := r + 1;
        end loop;
        return r;
    end function;
end package body;