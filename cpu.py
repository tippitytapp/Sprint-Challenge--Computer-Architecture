"""CPU functionality."""

import sys

PRN = 0b01000111 
LDI = 0b10000010 
HLT = 0b00000001 
MUL = 0b10100010 
PUSH = 0b01000101 
POP = 0b01000110 
CALL = 0b01010000 
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110    
SP = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.branchtable = {}
        self.branchtable[PRN] = self.prn
        self.branchtable[LDI] = self.ldi
        self.branchtable[HLT] = self.hlt
        self.branchtable[MUL] = self.mul
        self.branchtable[PUSH] = self.push
        self.branchtable[POP] = self.pop
        self.branchtable[CALL] = self.call
        self.branchtable[RET] = self.ret
        self.branchtable[CMP] = self.CMP
        self.branchtable[JMP] = self.JMP
        self.branchtable[JEQ] = self.JEQ
        self.branchtable[JNE] = self.JNE
        # Flag setup
        self.E = 0
        self.L = 0
        self.G = 0  

    def prn(self):
        '''Print numeric value stored in the given register.
        Print to the console the decimal integer value that is stored in the given register.'''
        operand_a = self.ram[self.pc + 1]
        print(self.reg[operand_a])

    def ldi(self):
        '''Set the value of a register to an integer.'''
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.reg[operand_a] = operand_b
    
    def hlt(self):
        '''Halt the CPU (and exit the emulator).'''
        self.running = False

    def mul(self):
        '''Multiply the values in two registers together and store the result in registerA.'''
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.alu("MUL", operand_a, operand_b)

    def push(self):
        '''Push the value in the given register on the stack.'''
        reg_address = self.ram[self.pc + 1] 
        self.reg[SP] -= 1 
        value = self.reg[reg_address] 
        self.ram[self.reg[SP]] = value

    def pop(self):
        '''Pop the value at the top of the stack into the given register.'''
        reg_address = self.ram[self.pc + 1]
        value = self.ram[self.reg[SP]]
        self.reg[reg_address] = value 
        self.reg[SP] += 1 
    
    def call(self):
        '''Calls a subroutine (function) at the address stored in the register.'''
        next_address = self.pc + 2
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = next_address
        address = self.reg[self.ram[self.pc + 1]]
        self.pc = address

    def ret(self):
        '''Return from subroutine.'''
        next_address = self.ram[self.pc]
        self.reg[SP] += 1
        self.pc = next_address

    def CMP(self):
        '''Compare the values in two registers.'''
        self.E = 0
        self.L = 0
        self.G = 0
        reg_a = self.reg[self.ram[self.pc + 1]]
        reg_b = self.reg[self.ram[self.pc + 2]]

        if reg_a == reg_b:
            '''If they are equal, set the Equal `E` flag to 1, otherwise set it to 0.'''
            self.E = 1
        elif reg_a < reg_b:
            '''If registerA is less than registerB, set the Less-than `L` flag to 1,   otherwise set it to 0.'''
            self.L = 1
        elif reg_a > reg_b:
            '''If registerA is greater than registerB, set the Greater-than `G` flag to 1, otherwise set it to 0.'''
            self.G = 1
    
    def JMP(self):
        '''Jump to the address stored in the given register.'''
        jump_address = self.reg[self.ram[self.pc + 1]]
        '''Set the `PC` to the address stored in the given register.'''
        self.pc = jump_address

    def JEQ(self):
        '''If `equal` flag is set (true), jump to the address stored in the given register.'''
        if self.E == 1:
            self.pc = self.reg[self.ram[self.pc + 1]]
        else:
            self.pc += 2

    def JNE(self):
        '''If `E` flag is clear (false, 0), jump to the address stored in the given register.'''
        if self.E == 0:
            self.pc = self.reg[self.ram[self.pc + 1]]
        else:
            self.pc += 2
    

    def ram_read(self, address):
        return(self.ram[address])

    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""
        try: 
            with open(sys.argv[1]) as f:
                address = 0
                for line in f:
                    num = line.split('#', 1)[0]
                    if num.strip() == '':
                        continue
                    self.ram[address] = int(num, 2)
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} Not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run  the CPU."""
        self.reg[SP] = 244
        self.running = True

        while self.running: 
            ir = self.pc
            op = self.ram[ir]
            operand_a = self.ram[self.pc + 1]
            operand_b = self.ram[self.pc + 2]
            instruction_size = ((op & 11000000) >> 6) + 1
            pc_set_flag = (op & 0b00010000) 
            self.branchtable[op]()
            if pc_set_flag != 0b00010000:
                self.pc += instruction_size

