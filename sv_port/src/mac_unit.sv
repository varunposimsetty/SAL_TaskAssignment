`timescale 1ns/1ps
module mac_unit #(
    parameter DATA_WIDTH = 8,
    parameter LENGTH     = 4
)(
    input  logic i_clk,
    input  logic i_nrst_sync,
    input  logic i_start,
    input  logic signed [DATA_WIDTH-1:0] i_vecA [LENGTH],
    input  logic signed [DATA_WIDTH-1:0] i_vecB [LENGTH],
    output logic signed [(2*DATA_WIDTH + $clog2(LENGTH))-1:0] o_result,
    output logic o_valid
);

    localparam PROD_W = 2 * DATA_WIDTH;
    localparam SUM_W  = 2 * DATA_WIDTH + 1;
    localparam ACC_W  = 2 * DATA_WIDTH + $clog2(LENGTH);

    logic signed [PROD_W-1:0] prod_r [LENGTH];
    logic signed [SUM_W-1:0]  sum_r  [LENGTH/2];
    logic signed [ACC_W-1:0]  res_r;
    logic [2:0]               start_shift;

    always_ff @(posedge i_clk) begin
        if (!i_nrst_sync) begin
            start_shift <= 3'b0;
            res_r       <= '0;
            for (int i = 0; i < LENGTH; i++)   prod_r[i] <= '0;
            for (int i = 0; i < LENGTH/2; i++) sum_r[i]  <= '0;
        end else begin
            start_shift <= {start_shift[1:0], i_start};
            // Stage 1
            if (i_start) begin
                for (int i = 0; i < LENGTH; i++) begin
                    prod_r[i] <= i_vecA[i] * i_vecB[i];
                end
            end
            // Stage 2
            if (start_shift[0]) begin
                for (int i = 0; i < LENGTH/2; i++) begin
                    sum_r[i] <= $signed(prod_r[2*i]) + $signed(prod_r[2*i+1]);
                end
            end
            // Stage 3
            if (start_shift[1]) begin
                res_r <= $signed(sum_r[0]) + $signed(sum_r[1]);
            end
        end
    end

    assign o_result = res_r;
    assign o_valid  = start_shift[2];
endmodule
