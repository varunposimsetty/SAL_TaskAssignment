library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library work;
use work.TaskGlobalPackage.all;

entity TopModuleStalled is 
    generic(
        DATA_WIDTH : integer := 8;
        LENGTH     : integer := 4;
        MEM_DEPTH  : integer := 4;
        MEM_WIDTH  : integer := 32
    );
    port(
        i_clk         : in std_ulogic;
        i_nrst        : in std_ulogic;
        i_instruction : in std_ulogic_vector(1 downto 0); -- 00 Null 01 Read 10 Write 11 Compute
        i_address     : in std_ulogic_vector(ceil_log2(MEM_DEPTH)-1 downto 0);
        i_wr_data     : in std_ulogic_vector(MEM_WIDTH-1 downto 0);
        o_rd_data     : out std_ulogic_vector(MEM_WIDTH-1 downto 0)
    );
end entity TopModuleStalled;

architecture RTL of TopModuleStalled is
    type tMemReg is array(0 to MEM_DEPTH-1) of std_ulogic_vector(MEM_WIDTH-1 downto 0);
    signal MemReg : tMemReg := (others => (others => '0'));

    signal vecA : tvector(0 to LENGTH-1)(DATA_WIDTH-1 downto 0) := (others => (others => '0'));
    signal vecB : tvector(0 to LENGTH-1)(DATA_WIDTH-1 downto 0) := (others => (others => '0'));
    signal result : signed((2*DATA_WIDTH + ceil_log2(LENGTH))-1 downto 0) := (others => '0');

    type tmacunit_state is (IDLE, VEC_LOAD, COMPUTE_START, STALL, WRITEBACK, DONE);
    signal mac_status : tmacunit_state := IDLE;

    signal start : std_ulogic := '0';
    signal valid : std_ulogic := '0';
    signal wr_back : std_ulogic := '0';


begin 

    MAC_UNIT : entity work.mac_unit(RTL)
        generic map(
            DATA_WIDTH => DATA_WIDTH,
            LENGTH     => LENGTH
        )
        port map(
            i_clk       => i_clk,
            i_nrst_sync => i_nrst,
            i_start     => start,
            i_vecA      => vecA,
            i_vecB      => vecB,
            o_result    => result,
            o_valid     => valid
        );
    
    -- Handling read and write of external data 
    proc_mem : process(i_clk) 
    begin 
        if(rising_edge(i_clk)) then 
            if(i_nrst = '0') then 
                MemReg <= (others => (others => '0'));
                o_rd_data <= (others =>'0');
            else
                -- WRITE Instruction
                if(i_instruction = "10" and (i_address /= "11" and i_address /= "00") and mac_status = IDLE) then 
                    MemReg(to_integer(unsigned(i_address))) <= i_wr_data;
                end if;
                -- READ Instruction
                if(i_instruction = "01" and mac_status = IDLE) then 
                    o_rd_data <= MemReg(to_integer(unsigned(i_address))); 
                end if;
                if(wr_back = '1') then 
                    MemReg(3) <= std_ulogic_vector(resize(result, MEM_WIDTH));
                end if;
                -- Status Memory Register 
                MemReg(0)(0) <= '1' when mac_status /= IDLE else '0';
                MemReg(0)(1) <= '1' when (mac_status = DONE or mac_status = WRITEBACK) else '0';
                -- Mapping the register data to the MAC Unit
                vectors_loop : for u in 0 to LENGTH-1 loop
                    vecA(u) <= signed(MemReg(1)((8*(u+1))-1 downto 8*u));
                    vecB(u) <= signed(MemReg(2)((8*(u+1))-1 downto 8*u));
                end loop vectors_loop;
            end if;
        end if;
    end process proc_mem;

    -- Control 
    proc_control : process(i_clk)
    begin 
        if(rising_edge(i_clk)) then 
            if(i_nrst = '0') then 
                start <= '0';
                mac_status <= IDLE;
            else 
                case(mac_status) is 
                    when IDLE => 
                        start <= '0';
                        if(i_instruction = "11") then 
                            mac_status <= VEC_LOAD;
                        else 
                            mac_status <= IDLE;
                        end if;
                    when VEC_LOAD => 
                        mac_status <= COMPUTE_START;
                        start <= '1';
                    when COMPUTE_START =>
                        mac_status <= STALL;
                        start <= '0';
                    when STALL => 
                        if(valid = '1') then
                            wr_back <= '1';
                            mac_status <= WRITEBACK;
                        end if;
                    when WRITEBACK =>
                        wr_back <= '0';
                        mac_status <= DONE;
                    when DONE =>
                        mac_status <= IDLE;
                    when others => 
                        null;
                end case;
            end if;
        end if;
    end process proc_control;
end architecture RTL;