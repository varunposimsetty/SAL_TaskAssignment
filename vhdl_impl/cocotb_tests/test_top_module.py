import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, ReadOnly
from cocotb.types import LogicArray, Range
from collections import deque
import random

#GENERICS 
DATA_WIDTH = 8
LENGTH     = 4
MEM_DEPTH  = 4
MEM_WIDTH  = 32

# Instructions (dut.i_instructions)
INS_NULL   = 0b00
INS_READ   = 0b01
INS_WRITE  = 0b10
INS_COMPUTE= 0b11

# Register Address and Mapping
ADDR_STATUS = 0
ADDR_VEC_A  = 1
ADDR_VEC_B  = 2
ADDR_RESULT = 3

def int_to_signed(value, width):
    if value < 0:
        value = (1 << width) + value
    return value & ((1 << width) - 1)

def signed_to_int(value, width):
    if hasattr(value, '__int__'):
        value = int(value)
    if value >= (1 << (width - 1)):
        value = value - (1 << width)
    return value

#converts 4x8-bits into a 32-bit word
def pack_vector(values):
    packed = 0
    for i,val in enumerate(values):
        byte_val = int_to_signed(val,DATA_WIDTH)
        packed |= (byte_val << (i*8))
    return packed

def unpack_vector(packed_val):
    if hasattr(packed_val, "__int__"):
        packed_val = int(packed_val)
    values = []
    for i in range(LENGTH):
        byte_val = (packed_val >> (i * 8)) & 0xFF
        values.append(signed_to_int(byte_val, DATA_WIDTH))
    return values

async def write_register(dut,address,data):
    dut.i_instruction.value = INS_WRITE
    dut.i_address.value = address
    dut.i_wr_data.value = data
    await RisingEdge(dut.i_clk)
    dut.i_instruction.value = INS_NULL
    await RisingEdge(dut.i_clk)

async def read_register(dut,address):
    dut.i_instruction.value = INS_READ
    dut.i_address.value = address
    await RisingEdge(dut.i_clk)
    await RisingEdge(dut.i_clk)
    result = int(dut.o_rd_data.value)
    dut.i_instruction.value = INS_NULL
    await RisingEdge(dut.i_clk)
    return result

async def do_compute_and_wait(dut,timeout_cycles=30):
        dut.i_instruction.value = INS_COMPUTE
        await RisingEdge(dut.i_clk)
        dut.i_instruction.value = INS_NULL

        timeout = timeout_cycles
        while timeout > 0:
            status = await read_register(dut, ADDR_STATUS)
            if (status & 0b10):  # valid bit
                return
            await ClockCycles(dut.i_clk, 1)
            timeout -= 1
        assert False, "Timeout waiting for valid"

# sanity check and basic read and write
@cocotb.test()
async def test_sanity(dut):
    clock = Clock(dut.i_clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.i_nrst.value = 0
    dut.i_instruction.value = INS_NULL
    dut.i_address.value = 0
    dut.i_wr_data.value = 0
    await ClockCycles(dut.i_clk, 5)
    dut.i_nrst.value = 1
    await ClockCycles(dut.i_clk, 3)

    test_vec = [1,2,3,4]
    packed = pack_vector(test_vec)
    cocotb.log.info(f"Writing {test_vec} (packed : 0x{packed:08x})")
    await write_register(dut,ADDR_VEC_A,packed)
    cocotb.log.info("Reading back")
    read_back = await read_register(dut,ADDR_VEC_A)
    cocotb.log.info("Read : 0x{read_back:08x}")

    unpacked = unpack_vector(read_back)

    assert unpacked == test_vec,f"Expected {test_vec}, got {unpacked}"

    cocotb.log.info("Basic Read and Write works")

# reset behvaiour check
@cocotb.test()
async def test_reset(dut):
    clock = Clock(dut.i_clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.i_nrst.value = 0
    dut.i_instruction.value = INS_NULL
    dut.i_address.value = 0
    dut.i_wr_data.value = 0
    await ClockCycles(dut.i_clk, 5)
    dut.i_nrst.value = 1
    await ClockCycles(dut.i_clk, 3)

    await write_register(dut,ADDR_VEC_A,pack_vector([10,20,30,40]))
    await write_register(dut,ADDR_VEC_A,pack_vector([5,6,7,8]))
    dut.i_nrst.value = 0
    await ClockCycles(dut.i_clk, 1)
    dut.i_nrst.value = 1
    
    vecA_data = await read_register(dut,ADDR_VEC_A)
    vecB_data = await read_register(dut,ADDR_VEC_B)
    status = await read_register(dut,ADDR_STATUS)

    assert vecA_data == 0, f"VecA should be 0 after reset, got 0x{vecA_data:08x}"
    assert vecB_data == 0, f"VecA should be 0 after reset, got 0x{vecA_data:08x}"
    assert status == 0, f"VecA should be 0 after reset, got 0x{vecA_data:08x}"

    cocotb.log.info("Reset behaviour verified")

 #checking basic compute   
@cocotb.test()
async def test_basic_compute(dut):
    clock = Clock(dut.i_clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.i_nrst.value = 0
    dut.i_instruction.value = INS_NULL
    dut.i_address.value = 0
    dut.i_wr_data.value = 0
    await ClockCycles(dut.i_clk, 5)
    dut.i_nrst.value = 1
    await ClockCycles(dut.i_clk, 3)

    test_cases = [([1,1,1,1],[1,1,1,1],4),
                  ([2,3,4,5],[1,1,1,1],14),
                  ([10,20,30,40],[2,2,2,2],200),
                  ([-1,-1,-1,-1],[1,1,1,1],-4),
                  ([5,-3,2,-1],[2,4,-1,3],-7),
                  ([127,127,0,0],[1,1,0,0],254),
                  ([-128,0,0,0],[1,0,0,0],-128)]
    
    for vecA,vecB, expected in test_cases:
        await write_register(dut,ADDR_VEC_A,pack_vector(vecA))
        #await ClockCycles(dut.i_clk, 2)
        await write_register(dut,ADDR_VEC_B,pack_vector(vecB))
        #await ClockCycles(dut.i_clk, 2)

        dut.i_instruction.value = INS_COMPUTE
        await RisingEdge(dut.i_clk)
        dut.i_instruction.value = INS_NULL

        timeout = 20
        while timeout > 0:
            status = await read_register(dut,ADDR_STATUS)
            if(status & 0b10):
                break 
            await ClockCycles(dut.i_clk,1)
            timeout -= 1

        assert timeout > 0,f"Timeout Waiting for result:{vecA}.{vecB}"

        result_raw = await read_register(dut,ADDR_RESULT)
        result = signed_to_int(result_raw,MEM_WIDTH) # Reading the sign extended output
        assert result == expected,f"{vecA}.{vecB}: Expected {expected}, got {result}"
        cocotb.log.info(f"{vecA}.{vecB} = {result}")

        await ClockCycles(dut.i_clk, 2)

    cocotb.log.info("Passed basic computation checks")

# checking for multiple sequential computations
@cocotb.test()
async def test_multiple_compute(dut):
    clock = Clock(dut.i_clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.i_nrst.value = 0
    dut.i_instruction.value = INS_NULL
    dut.i_address.value = 0
    dut.i_wr_data.value = 0
    await ClockCycles(dut.i_clk, 5)
    dut.i_nrst.value = 1
    await ClockCycles(dut.i_clk, 3)

    test_cases = [
        ([7, 8, 9, 10],[1, 2, 3, 4],90),
        ([100, 0, 0, 0],[1, 2, 3, 4],100),
        ([-10, -20, 30, 40],[5, 5, 5, 5],200),
        ([127, 127, 0, 0],[1, 1, 0, 0],254),
        ([-128, 0, 0, 0],[1, 0, 0, 0],-128)]

    for i, (vecA, vecB, expected) in enumerate(test_cases, start=1):
        cocotb.log.info(f"Test {i}/{len(test_cases)}: vecA={vecA}, vecB={vecB}")

        await write_register(dut, ADDR_VEC_A, pack_vector(vecA))
        await write_register(dut, ADDR_VEC_B, pack_vector(vecB))

        timeout = 20
        while timeout > 0:
            status = await read_register(dut, ADDR_STATUS)
            if (status & 0b10) == 0:
                break
            await ClockCycles(dut.i_clk, 1)
            timeout -= 1
        assert timeout > 0, f"Timeout waiting for valid to clear before test {i}"

        dut.i_instruction.value = INS_COMPUTE
        await RisingEdge(dut.i_clk)
        dut.i_instruction.value = INS_NULL

        timeout = 10
        while timeout > 0:
            status = await read_register(dut, ADDR_STATUS)
            if (status & 0b10):
                break
            await ClockCycles(dut.i_clk, 1)
            timeout -= 1
        assert timeout > 0, f"Timeout waiting for valid on test {i}"

        result_raw = await read_register(dut, ADDR_RESULT)
        result = signed_to_int(result_raw, 32)

        assert result == expected, f"Test {i}: Expected {expected}, got {result}"
        cocotb.log.info(f"Test {i} PASS: result={result}")

        await ClockCycles(dut.i_clk, 2)

    cocotb.log.info(f"Sucessfully verified continous sequential computations")

#checking the status register i.e. Mem(0)
@cocotb.test()
async def test_status_register(dut):
    clock = Clock(dut.i_clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.i_nrst.value = 0
    dut.i_instruction.value = INS_NULL
    dut.i_address.value = 0
    dut.i_wr_data.value = 0
    await ClockCycles(dut.i_clk, 5)
    dut.i_nrst.value = 1
    await ClockCycles(dut.i_clk, 3)

    status = await read_register(dut, ADDR_STATUS)
    assert (status & 0b1) == 0, "Bit0(running) should be 0 in IDLE"
    assert (status & 0b10) == 0, "Bit1(valid) should be 0 in IDLE"
    cocotb.log.info(f"Initial status: 0x{status:08x}")

    vecA = [3, 4, 5, 6]
    vecB = [2, 2, 2, 2]
    await write_register(dut, ADDR_VEC_A, pack_vector(vecA))
    await write_register(dut, ADDR_VEC_B, pack_vector(vecB))

    dut.i_instruction.value = INS_COMPUTE
    await RisingEdge(dut.i_clk)
    dut.i_instruction.value = INS_NULL
    # We wait a cycle as the run asserts from the next clock cycle
    await ClockCycles(dut.i_clk, 1)

    status = await read_register(dut, ADDR_STATUS)
    running = (status >> 0) & 0x1
    valid = (status >> 1) & 0x1
    pipe_busy = (status >> 2) & 0x7  # bits[4:2]
    cocotb.log.info(f"Status after start: 0x{status:08x} running={running} valid={valid} busy=0b{pipe_busy:03b}")

    assert (running == 1) or (pipe_busy != 0), f"Expected running=1 or pipe_busy!=0 got running = {running} and busy =  {pipe_busy:03x}"

    timeout = 50
    while timeout > 0:
        status = await read_register(dut, ADDR_STATUS)
        if (status & 0b10):
            break
        await ClockCycles(dut.i_clk, 1)
        timeout -= 1
    assert timeout > 0, "Timeout waiting for valid"

    assert (status & 0b10) != 0, "Bit1(valid) should be 1 when done"
    dut._log.info(f"Final status: 0x{status:08x}")

    result_raw = await read_register(dut, ADDR_RESULT)
    result = signed_to_int(result_raw, 32)
    expected = sum(a * b for a, b in zip(vecA, vecB))
    assert result == expected, f"Expected {expected}, got {result}"

    dut._log.info("Stage 5 PASSED: Status register verified")

#checking the read only Mem(0) and Mem(3)
@cocotb.test()
async def test_readonly(dut):
    clock = Clock(dut.i_clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.i_nrst.value = 0
    dut.i_instruction.value = INS_NULL
    dut.i_address.value = 0
    dut.i_wr_data.value = 0
    await ClockCycles(dut.i_clk, 5)
    dut.i_nrst.value = 1
    await ClockCycles(dut.i_clk, 3)

    cocotb.log.info("Attempting to write STATUS (should be blocked) - Cannot Write into Mem(0)")
    await write_register(dut, ADDR_STATUS, 0xDEADBEEF)
    status = await read_register(dut, ADDR_STATUS)
    assert status == 0, f"STATUS should remain 0 after blocked write, got 0x{status:08x}"
    cocotb.log.info("STATUS write blocked")

    cocotb.log.info("Attempting to write RESULT (should be blocked) - Cannot Write into Mem(3)")
    await write_register(dut, ADDR_RESULT, 0xCAFEBABE)
    result = await read_register(dut, ADDR_RESULT)
    assert result == 0, f"RESULT should remain 0 before any compute, got 0x{result:08x}"
    cocotb.log.info("RESULT write blocked")

    test_val_a = pack_vector([11, 22, 33, 44])
    test_val_b = pack_vector([55, 66, 77, 88])
    await write_register(dut, ADDR_VEC_A, test_val_a)
    await write_register(dut, ADDR_VEC_B, test_val_b)

    read_a = await read_register(dut, ADDR_VEC_A)
    read_b = await read_register(dut, ADDR_VEC_B)

    assert read_a == test_val_a, f"VEC_A write failed: exp 0x{test_val_a:08x} got 0x{read_a:08x}"
    assert read_b == test_val_b, f"VEC_B write failed: exp 0x{test_val_b:08x} got 0x{read_b:08x}"
    dut._log.info("VEC_A and VEC_B are writable")

    dut._log.info("checked if writing into Mem(0) and Mem(3) is avoided")

#checks boundary conditions and random tests with random resets in between 
@cocotb.test()
async def test_edge_cases_and_random_tests(dut):
    clock = Clock(dut.i_clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.i_nrst.value = 0
    dut.i_instruction.value = INS_NULL
    dut.i_address.value = 0
    dut.i_wr_data.value = 0
    await ClockCycles(dut.i_clk, 5)
    dut.i_nrst.value = 1
    await ClockCycles(dut.i_clk, 3)

    #Boundary Cases
    cocotb.log.info("=== Testing boundary cases ===")
    boundary_cases = [
        ([127,127,127,127],[127, 127, 127,127],64516),
        ([-128,-128,-128,-128], [-128,-128,-128,-128],65536),
        ([127,-128,0,1],[1,1,127,-128],-129),
        ([0,0,0,0], [127,127,127,127],0)]

    for vecA, vecB, expected in boundary_cases:
        await write_register(dut, ADDR_VEC_A, pack_vector(vecA))
        await write_register(dut, ADDR_VEC_B, pack_vector(vecB))

        await do_compute_and_wait(dut,timeout_cycles=10)

        result_raw = await read_register(dut, ADDR_RESULT)
        result = signed_to_int(result_raw, 32)
        assert result == expected, f"Boundary {vecA}.{vecB}: Expected {expected}, got {result}"
        await ClockCycles(dut.i_clk, 2)

    cocotb.log.info(f"{len(boundary_cases)} boundary cases passed")

    #Reset during computatin
    cocotb.log.info("=== Testing reset during computation ===")
    await write_register(dut, ADDR_VEC_A, pack_vector([10, 20, 30, 40]))
    await write_register(dut, ADDR_VEC_B, pack_vector([5, 5, 5, 5]))

    dut.i_instruction.value = INS_COMPUTE
    await RisingEdge(dut.i_clk)
    dut.i_instruction.value = INS_NULL
    await ClockCycles(dut.i_clk, 2)

    dut.i_nrst.value = 0
    await ClockCycles(dut.i_clk, 3)
    dut.i_nrst.value = 1
    await ClockCycles(dut.i_clk, 3)

    status = await read_register(dut, ADDR_STATUS)
    result = await read_register(dut, ADDR_RESULT)
    assert status == 0, f"Status should be 0 after reset, got 0x{status:08x}"
    assert result == 0, f"Result should be 0 after reset, got 0x{result:08x}"
    cocotb.log.info("Reset during compute works")

    # Random tests
    dut._log.info("=== Random tests ===")
    rng = random.Random(123)
    NUM_RANDOM = 20

    for i in range(NUM_RANDOM):
        vecA = [rng.randint(-128, 127) for _ in range(LENGTH)]
        vecB = [rng.randint(-128, 127) for _ in range(LENGTH)]
        expected = sum(a * b for a, b in zip(vecA, vecB))

        await write_register(dut, ADDR_VEC_A, pack_vector(vecA))
        await write_register(dut, ADDR_VEC_B, pack_vector(vecB))

        await do_compute_and_wait(dut,timeout_cycles=40)

        result_raw = await read_register(dut, ADDR_RESULT)
        result = signed_to_int(result_raw, 32)
        assert result == expected, f"Random {i} {vecA}.{vecB}: Expected {expected}, got {result}"

    dut._log.info(f"{NUM_RANDOM} random tests passed")
    dut._log.info("Succesfully verified against random inputs, boundry cases and resets during computation")
