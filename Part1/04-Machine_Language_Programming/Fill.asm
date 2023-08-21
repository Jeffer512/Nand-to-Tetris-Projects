// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

@24576
D=A
@14
M=D
@23
M=D
@24576
D=M
@12
D;JNE
@21
D;JEQ
@16384
D=A
A=D
M=-1
D=D+1
@14
M-D;JNE
@0
0;JMP
@16384
D=A
A=D
M=0
D=D+1
@23
M-D;JNE
@0
0;JMP

