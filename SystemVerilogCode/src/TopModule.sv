`timescale 1ns/1ps
module TopModule #(
    parameter DATA_WIDTH = 8,
    parameter LENGTH     = 4,
    parameter MEM_DEPTH  = 4,
    parameter MEM_WIDTH  = 32
)(
    input  logic i_clk,
    input  logic i_nrst,
    input  logic [1:0] i_instruction, // 00 Null Operation 01 Read 10 Write 11 Compute
    input  logic [$clog2(MEM_DEPTH)-1:0] i_address,
    input  logic [MEM_WIDTH-1:0] i_wr_data,
    output logic [MEM_WIDTH-1:0] o_rd_data
);

    logic [MEM_WIDTH-1:0] MemReg [MEM_DEPTH];
    logic signed [DATA_WIDTH-1:0] vecA [LENGTH];
    logic signed [DATA_WIDTH-1:0] vecB [LENGTH];
    logic signed [(2*DATA_WIDTH + $clog2(LENGTH))-1:0] result;
    
    logic start, valid;
    logic [2:0] pipe_busy;

    typedef enum logic {IDLE, RUNNING} t_state;
    t_state state;

    mac_unit #(
        .DATA_WIDTH(DATA_WIDTH),
        .LENGTH(LENGTH)
    ) MAC_INST (
        .i_clk(i_clk),
        .i_nrst_sync(i_nrst),
        .i_start(start),
        .i_vecA(vecA),
        .i_vecB(vecB),
        .o_result(result),
        .o_valid(valid)
    );

    // Mapping register values to the MAC Unit
    always_comb begin
        for (int i = 0; i < LENGTH; i++) begin
            vecA[i] = MemReg[1][(8*i) +: 8];
            vecB[i] = MemReg[2][(8*i) +: 8];
        end
    end

    always_ff @(posedge i_clk) begin
        if (!i_nrst) begin
            state     <= IDLE;
            start     <= 0;
            pipe_busy <= 0;
            o_rd_data <= 0;
            for (int i = 0; i < MEM_DEPTH; i++) MemReg[i] <= 0;
        end else begin
            // External write
            if (i_instruction == 2'b10 && i_address != 0 && i_address != 3) 
                MemReg[i_address] <= i_wr_data;
            // External read
            if (i_instruction == 2'b01)
                o_rd_data <= MemReg[i_address];
            // Writing the Result of MAC operation into Memory
            if (valid)
                MemReg[3] <= MEM_WIDTH'(result);
            // Status Registers
            MemReg[0][0] <= (state == RUNNING);
            MemReg[0][1] <= valid;
            MemReg[0][4:2] <= pipe_busy;
            // piplined status
            pipe_busy <= {pipe_busy[1:0], start};
            // FSM
            case (state)
                IDLE: begin
                    if (i_instruction == 2'b11) begin
                        start <= 1;
                        state <= RUNNING;
                    end else begin
                        start <= 0;
                    end
                end
                RUNNING: begin
                    start <= (i_instruction == 2'b11);
                    if (i_instruction != 2'b11 && pipe_busy == 0)
                        state <= IDLE;
                end
            endcase
        end
    end
endmodule
