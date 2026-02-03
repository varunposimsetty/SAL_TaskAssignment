`timescale 1ns/1ps

module tb_top;
    logic clk = 0;
    logic rst = 0;
    logic [1:0] instruction = 0;
    logic [1:0] address = 0;
    logic [31:0] wr_data = 0;
    logic [31:0] rd_data;

    TopModule #(
        .DATA_WIDTH(8),
        .LENGTH(4),
        .MEM_DEPTH(4),
        .MEM_WIDTH(32)
    ) DUT (
        .i_clk(clk),
        .i_nrst(rst),
        .i_instruction(instruction),
        .i_address(address),
        .i_wr_data(wr_data),
        .o_rd_data(rd_data)
    );

    always begin
        #5 clk = ~clk;
    end

    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0, tb_top);
        #40 
        rst = 1;
        #50 
        instruction = 2'b01;
        address = 2'b11;
        #20 
        instruction = 2'b10;
        address = 2'b01;
        wr_data = 32'h00000000;
        #10 
        address = 2'b10;
        wr_data = 32'h00000000;
        #10 
        instruction = 2'b11;
        #10 
        instruction = 2'b00;
        #40 
        instruction = 2'b01;
        address = 2'b11;
        #20 
        instruction = 2'b10;
        address = 2'b01;
        wr_data = 32'h01010101;
        #10 
        address = 2'b10;
        wr_data = 32'h01010101;
        #10 
        instruction = 2'b11;
        #10 
        instruction = 2'b10;
        address = 2'b01;
        wr_data = 32'h02020202;
        #10 
        address = 2'b10;
        wr_data = 32'h02020202;
        #10 
        instruction = 2'b11;
        #10 
        instruction = 2'b00;
        #60 
        instruction = 2'b01;
        address = 2'b11;
        #20 
        instruction = 2'b01;
        address = 2'b00;
        #20 
        instruction = 2'b10;
        address = 2'b01;
        wr_data = 32'hAABBCCDD;
        #10 
        instruction = 2'b01;
        address = 2'b01;
        #20 
        instruction = 2'b10;
        address = 2'b10;
        wr_data = 32'h11223344;
        #10 
        instruction = 2'b01;
        address = 2'b10;
        #30 
        instruction = 2'b11;
        #50 
        instruction = 2'b01;
        #20 
        address = 2'b11;
        #60 
        $finish;
    end
endmodule
