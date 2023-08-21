// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.
// @16
// M=0
// @2
// M=0
// @1
// D=M
// @16
// D+M;JEQ
// M=M-1
// @0
// D=M
// @2
// M=M+D
// @4
// 0;JMP
// @17
// 0;JMP


@2
M=0
@1
D=M
@14
M=D
@1
M=M-1
D=M 
@17
D;JLT
@0
D=M
@2
M=M+D
@6
0;JMP
@14
D=M
@1
M=D
@21
0;JMP
