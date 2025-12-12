`timescale 1ns/100ps
module APN_ANF(in, out);
    input  [3:0] in;
    output [3:0] out;

    // Input bit aliases
    wire a0 = in[0];
    wire a1 = in[1];
    wire a2 = in[2];
    wire a3 = in[3];

    // === ANF Implementation ===
    assign out[0] = (a0 & a1 & a3) ^ (a0 & a1) ^ (a0 & a2) ^ (a0 & a3) ^ (a1 & a3) ^ a2 ^ a3;
    assign out[1] = (a0 & a3) ^ a0 ^ (a1 & a2 & a3) ^ (a1 & a2) ^ (a1 & a3) ^ a1 ^ a2;
    assign out[2] = (a0 & a2 & a3) ^ (a0 & a2) ^ (a0 & a3) ^ a0 ^ (a1 & a2) ^ a1 ^ (a2 & a3) ^ a2;
    assign out[3] = (a0 & a1 & a2) ^ (a0 & a1) ^ (a0 & a2) ^ (a1 & a3) ^ a1 ^ a2 ^ a3;

endmodule

