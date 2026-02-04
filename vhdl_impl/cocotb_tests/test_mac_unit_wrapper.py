import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.types import LogicArray, Range
from collections import deque
import random

DATA_WIDTH = 8
LENGTH = 4
RESULT_WIDTH = 2 * DATA_WIDTH + 2 # ceil_log2(4) = 2

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

def set_vector(dut, vec_name, values, width=DATA_WIDTH):
    assert len(values) == LENGTH
    for i in range(LENGTH):
        signal = getattr(dut, f"{vec_name}_{i}")
        signed_val = int_to_signed(values[i], width)
        signal.value = LogicArray(signed_val, Range(width-1, 'downto', 0))

def calculate_mac(vecA, vecB):
    return sum(a * b for a, b in zip(vecA, vecB))

def get_result(dut):
    return signed_to_int(dut.o_result.value, RESULT_WIDTH)

async def drive_inputs(dut,test_cases,expected_queue):
    for vecA,vecB,expected in test_cases:
        set_vector(dut,"i_vecA",vecA)
        set_vector(dut,"i_vecB",vecB)
        dut.i_start.value = 1
        expected_queue.append(expected)
        await RisingEdge(dut.i_clk)
        dut.i_start.value = 0
        await RisingEdge(dut.i_clk)

async def moniter(dut,expected_queue,n_outputs):
    got = 0
    while got < n_outputs:
        await RisingEdge(dut.i_clk)
        if int(dut.o_valid.value):
            assert expected_queue, "o_valid asserted but expected_queue empty"
            result = get_result(dut)
            expected = expected_queue.popleft()
            assert result == expected, f"Expected {expected}, got {result}"
            got += 1

async def drive_burst(dut,test_cases,expected_queue):
    dut.i_start.value = 1
    for vecA,vecB,expected in test_cases:
        set_vector(dut,"i_vecA",vecA)
        set_vector(dut,"i_vecB",vecB)
        expected_queue.append(expected)
        await RisingEdge(dut.i_clk)
    dut.i_start.value = 0

@cocotb.test()
# sanity check
async def test_sanity(dut):
    clock = Clock(dut.i_clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.i_nrst_sync.value = 0
    dut.i_start.value = 0
    set_vector(dut, "i_vecA", [0, 0, 0, 0])
    set_vector(dut, "i_vecB", [0, 0, 0, 0])

    await ClockCycles(dut.i_clk, 3)
    assert int(dut.o_valid.value) == 0, "o_valid should be 0 during reset"

    dut.i_nrst_sync.value = 1
    await ClockCycles(dut.i_clk, 1)

    dut.i_start.value = 1
    await ClockCycles(dut.i_clk, 1)
    dut.i_start.value = 0

    await ClockCycles(dut.i_clk, 3)

    valid = int(dut.o_valid.value)
    result = get_result(dut)
    assert valid == 1, f"o_valid should be 1, got {valid}"
    assert result == 0, f"Expected result=0, got {result}"

    cocotb.log.info("Sanity check complete")


@cocotb.test()
async def test_reset(dut):
    clock = Clock(dut.i_clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.i_nrst_sync.value = 0
    dut.i_start.value = 0
    set_vector(dut, "i_vecA", [0, 0, 0, 0])
    set_vector(dut, "i_vecB", [0, 0, 0, 0])

    await ClockCycles(dut.i_clk,5)
    assert int(dut.o_valid.value) == 0, "o_valid must stay 0 during reset"
    assert get_result(dut) == 0, "o_result must stay 0 during reset"

    dut.i_nrst_sync.value = 1
    await ClockCycles(dut.i_clk,1)
    set_vector(dut, "i_vecA", [1, 2, 3, 4])
    set_vector(dut, "i_vecB", [1, 1, 1, 1])
    dut.i_start.value = 1
    await ClockCycles(dut.i_clk,1)
    dut.i_start.value = 0
    await ClockCycles(dut.i_clk,1)
    dut.i_nrst_sync.value = 0
    await ClockCycles(dut.i_clk,1)
    assert int(dut.o_valid.value) == 0, "Reset clears the o_valid and hence should be 0"

    cocotb.log.info("Reset test Passed")

# running the mac on different test cases
@cocotb.test()
async def test_basic_test_vectors(dut):
    clock = Clock(dut.i_clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.i_nrst_sync.value = 0
    dut.i_start.value = 0
    set_vector(dut, "i_vecA", [0, 0, 0, 0])
    set_vector(dut, "i_vecB", [0, 0, 0, 0])

    await ClockCycles(dut.i_clk,5)
    dut.i_nrst_sync.value = 1
    await ClockCycles(dut.i_clk,1)

    test_cases = [([1,1,1,1],[1,1,1,1],4),
                  ([2,3,4,5],[1,1,1,1],14),
                  ([10,20,30,40],[2,2,2,2],200),
                  ([-1,-1,-1,-1],[1,1,1,1],-4),
                  ([5,-3,2,-1],[2,4,-1,3],-7),
                  ([127,127,0,0],[1,1,0,0],254),
                  ([-128,0,0,0],[1,0,0,0],-128)]
    
    for vecA, vecB, expected in test_cases:
        set_vector(dut,"i_vecA",vecA)
        set_vector(dut,"i_vecB",vecB)
        dut.i_start.value = 1
        await ClockCycles(dut.i_clk,1)
        dut.i_start.value = 0
        await ClockCycles(dut.i_clk,3)
        result = get_result(dut)
        assert int(dut.o_valid.value) == 1, f"o_valid not asserted"
        assert result == expected, f"Expected {expected}, got {result} for {vecA}.{vecB}"
        await ClockCycles(dut.i_clk,1)

    cocotb.log.info("Passed for different test cases")


# running the mac on corner cases
@cocotb.test()
async def test_boundary_cases(dut):
    clock = Clock(dut.i_clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.i_nrst_sync.value = 0
    dut.i_start.value = 0
    set_vector(dut, "i_vecA", [0, 0, 0, 0])
    set_vector(dut, "i_vecB", [0, 0, 0, 0])

    await ClockCycles(dut.i_clk,5)
    dut.i_nrst_sync.value = 1
    await ClockCycles(dut.i_clk,1)

    test_cases = [([127,127,127,127],[127,127,127,127],64516),
                  ([-128,-128,-128,-128],[-128,-128,-128,-128],65536),
                  ([127,-128,127,-128],[127,-128,127,-128],65026),
                  ([0,0,0,127],[0,0,0,127],16129),
                  ([1,0,0,0],[127,0,0,0],127),
                  ([-1,-1,-1,-1],[-1,-1,-1,-1],4),
                  ([127,1,1,1],[1,127,1,1],256)]
    
    for vecA, vecB, expected in test_cases:
        set_vector(dut,"i_vecA",vecA)
        set_vector(dut,"i_vecB",vecB)
        dut.i_start.value = 1
        await ClockCycles(dut.i_clk,1)
        dut.i_start.value = 0
        await ClockCycles(dut.i_clk,3)
        result = get_result(dut)
        assert int(dut.o_valid.value) == 1, f"o_valid not asserted"
        assert result == expected, f"Expected {expected}, got {result} for {vecA}.{vecB}"
        await ClockCycles(dut.i_clk,1)

    cocotb.log.info("Passed for boundary test cases")

# running the mac and checking the piplined results
@cocotb.test()
async def test_pipline_output(dut):
    clock = Clock(dut.i_clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.i_nrst_sync.value = 0
    dut.i_start.value = 0
    set_vector(dut, "i_vecA", [0, 0, 0, 0])
    set_vector(dut, "i_vecB", [0, 0, 0, 0])

    await ClockCycles(dut.i_clk,5)
    dut.i_nrst_sync.value = 1
    await ClockCycles(dut.i_clk,1)

    test_cases = [([1,2,3,4],[5,6,7,8],70),
                  ([10,11,12,13],[1,1,1,1],46),
                  ([-5,-10,15,20],[2,3,4,5],120),
                  ([0,0,0,127],[0,0,0,127],16129),
                  ([7,7,7,7],[3,3,3,3],84),
                  ([100,0,0,0],[1,2,3,4],100),
                  ([127,1,1,1],[1,127,1,1],256)]
    # Testing serially 
    expected_queue = deque()
    cocotb.start_soon(drive_inputs(dut, test_cases,expected_queue))
    await moniter(dut,expected_queue,len(test_cases))
    # Burst data transfer
    expected_queue = deque()
    cocotb.start_soon(drive_burst(dut, test_cases, expected_queue))
    await moniter(dut, expected_queue, len(test_cases))

    cocotb.log.info("Passed serial and burst transfer test cases with known inputs")


# running the mac and checking the serial and burst transfers for random values
@cocotb.test()
async def test_pipline_output(dut):
    clock = Clock(dut.i_clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.i_nrst_sync.value = 0
    dut.i_start.value = 0
    set_vector(dut, "i_vecA", [0, 0, 0, 0])
    set_vector(dut, "i_vecB", [0, 0, 0, 0])

    await ClockCycles(dut.i_clk,5)
    dut.i_nrst_sync.value = 1
    await ClockCycles(dut.i_clk,1)

    test_cases = [([1,2,3,4],[5,6,7,8],70),
                  ([10,11,12,13],[1,1,1,1],46),
                  ([-5,-10,15,20],[2,3,4,5],120),
                  ([0,0,0,127],[0,0,0,127],16129),
                  ([7,7,7,7],[3,3,3,3],84),
                  ([100,0,0,0],[1,2,3,4],100),
                  ([127,1,1,1],[1,127,1,1],256)]
    # Testing serially 
    expected_queue = deque()
    cocotb.start_soon(drive_inputs(dut, test_cases,expected_queue))
    await moniter(dut,expected_queue,len(test_cases))
    # Burst data transfer
    expected_queue = deque()
    cocotb.start_soon(drive_burst(dut, test_cases, expected_queue))
    await moniter(dut, expected_queue, len(test_cases))

    cocotb.log.info("Passed Pipline test cases")