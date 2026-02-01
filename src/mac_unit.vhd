library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library work;
use work.TaskGlobalPackage.all;

entity mac_unit is 
    generic(
        DATA_WIDTH : natural := 8;
        LENGTH     : natural := 4
    );
    port(
        i_clk       : in std_ulogic;
        i_nrst_sync : in std_ulogic;
        i_vecA      : in tvector(0 to LENGTH-1)(DATA_WIDTH-1 downto 0);
        i_vecB      : in tvector(0 to LENGTH-1)(DATA_WIDTH-1 downto 0);
        o_result    : out signed((2*DATA_WIDTH + ceil_log2(LENGTH))-1 downto 0)
    );
end entity mac_unit;

architecture RTL of mac_unit is  
    type tDataHolders is array (natural range <>) of signed;

    constant PROD_W : natural := 2*DATA_WIDTH;
    constant SUM_W  : natural := 2*DATA_WIDTH + 1;
    constant ACC_W  : natural := 2*DATA_WIDTH + ceil_log2(LENGTH);

    signal prod_r : tDataHolders(0 to LENGTH-1)(PROD_W-1 downto 0) := (others => (others => '0'));
    signal sum_r  : tDataHolders(0 to (LENGTH/2)-1)(SUM_W-1 downto 0) := (others => (others => '0'));
    signal res_r  : signed(ACC_W-1 downto 0) := (others => '0');
begin
    process(i_clk)
        variable prod_next : tDataHolders(0 to LENGTH-1)(PROD_W-1 downto 0) := (others => (others => '0'));
        variable res_next  : signed(ACC_W-1 downto 0) := (others => '0');
        variable sum_next  : tDataHolders(0 to (LENGTH/2)-1)(SUM_W-1 downto 0) := (others => (others => '0'));
        variable idx : integer := 0;
    begin 
        if(rising_edge(i_clk)) then 
            if(i_nrst_sync = '0') then 
                prod_r <= (others => (others => '0'));
                sum_r  <= (others => (others => '0'));
                res_r  <= (others => '0');
            else 
                -- stage 1 
                for i in 0 to LENGTH-1 loop
                    prod_next(i) := i_vecA(i)*i_vecB(i);
                end loop;
                -- stage 2
                for i in 0 to (LENGTH/2)-1 loop
                    idx := 2*i;
                    sum_next(i) := resize(prod_r(idx),SUM_W) + resize(prod_r(idx+1),SUM_W);
                end loop;
                -- stage 3
                res_next := resize(sum_r(0),ACC_W) + resize(sum_r(1),ACC_W);
            end if;
            prod_r <= prod_next;
            sum_r  <= sum_next;
            res_r  <= res_next;
        end if;
    end process;
    o_result <= res_r;  
end architecture RTL;