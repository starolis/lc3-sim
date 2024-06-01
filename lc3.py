class LC3Registers:
    def __init__(self):
        self.registers = {f'R{i}': 0 for i in range(8)}
        self.PC = 0
        self.IR = 0
        self.CC = {'N': 0, 'Z': 0, 'P': 0}

class LC3Memory:
    def __init__(self, size=2**16):
        self.memory = [0] * size
    
    def load(self, address):
        return self.memory[address]
    
    def store(self, address, value):
        self.memory[address] = value

class LC3ControlUnit:
    def __init__(self, registers, memory):
        self.registers = registers
        self.memory = memory
    
    def decode_and_execute(self):
        instruction = self.registers.IR
        opcode = (instruction >> 12) & 0xF
        
        if opcode == 0x1:  # ADD
            self.execute_add(instruction)
        elif opcode == 0x5:  # AND
            self.execute_and(instruction)
        elif opcode == 0x0:  # BR
            self.execute_br(instruction)
        elif opcode == 0xC:  # JMP
            self.execute_jmp(instruction)
        elif opcode == 0x4:  # JSR/JSRR
            self.execute_jsr_jsrr(instruction)
        elif opcode == 0x2:  # LD
            self.execute_ld(instruction)
        elif opcode == 0xA:  # LDI
            self.execute_ldi(instruction)
        elif opcode == 0x6:  # LDR
            self.execute_ldr(instruction)
        elif opcode == 0xE:  # LEA
            self.execute_lea(instruction)
        elif opcode == 0x9:  # NOT
            self.execute_not(instruction)
        elif opcode == 0x3:  # ST
            self.execute_st(instruction)
        elif opcode == 0xB:  # STI
            self.execute_sti(instruction)
        elif opcode == 0x7:  # STR
            self.execute_str(instruction)
        elif opcode == 0xF:  # TRAP
            self.execute_trap(instruction)
        else:
            raise ValueError(f"Unsupported opcode: {opcode}")
    
    def execute_add(self, instruction):
        dr = (instruction >> 9) & 0x7
        sr1 = (instruction >> 6) & 0x7
        imm_flag = (instruction >> 5) & 0x1
        
        if imm_flag:
            imm5 = instruction & 0x1F
            if imm5 & 0x10:
                imm5 |= 0xFFE0  # Sign extend
            self.registers.registers[f'R{dr}'] = (self.registers.registers[f'R{sr1}'] + imm5) & 0xFFFF
        else:
            sr2 = instruction & 0x7
            self.registers.registers[f'R{dr}'] = (self.registers.registers[f'R{sr1}'] + self.registers.registers[f'R{sr2}']) & 0xFFFF
        
        self.set_condition_codes(self.registers.registers[f'R{dr}'])
    
    def execute_and(self, instruction):
        dr = (instruction >> 9) & 0x7
        sr1 = (instruction >> 6) & 0x7
        imm_flag = (instruction >> 5) & 0x1
        
        if imm_flag:
            imm5 = instruction & 0x1F
            if imm5 & 0x10:
                imm5 |= 0xFFE0  # Sign extend
            self.registers.registers[f'R{dr}'] = self.registers.registers[f'R{sr1}'] & imm5
        else:
            sr2 = instruction & 0x7
            self.registers.registers[f'R{dr}'] = self.registers.registers[f'R{sr1}'] & self.registers.registers[f'R{sr2}']
        
        self.set_condition_codes(self.registers.registers[f'R{dr}'])
    
    def execute_br(self, instruction):
        n = (instruction >> 11) & 0x1
        z = (instruction >> 10) & 0x1
        p = (instruction >> 9) & 0x1
        pc_offset9 = instruction & 0x1FF
        if pc_offset9 & 0x100:
            pc_offset9 |= 0xFE00  # Sign extend
        
        if (n and self.registers.CC['N']) or (z and self.registers.CC['Z']) or (p and self.registers.CC['P']):
            self.registers.PC = (self.registers.PC + pc_offset9) & 0xFFFF
    
    def execute_jmp(self, instruction):
        base_r = (instruction >> 6) & 0x7
        self.registers.PC = self.registers.registers[f'R{base_r}']
    
    def execute_jsr_jsrr(self, instruction):
        long_flag = (instruction >> 11) & 0x1
        self.registers.registers['R7'] = self.registers.PC
        
        if long_flag:
            pc_offset11 = instruction & 0x7FF
            if pc_offset11 & 0x400:
                pc_offset11 |= 0xF800  # Sign extend
            self.registers.PC = (self.registers.PC + pc_offset11) & 0xFFFF
        else:
            base_r = (instruction >> 6) & 0x7
            self.registers.PC = self.registers.registers[f'R{base_r}']
    
    def execute_ld(self, instruction):
        dr = (instruction >> 9) & 0x7
        pc_offset9 = instruction & 0x1FF
        if pc_offset9 & 0x100:
            pc_offset9 |= 0xFE00  # Sign extend
        address = (self.registers.PC + pc_offset9) & 0xFFFF
        self.registers.registers[f'R{dr}'] = self.memory.load(address)
        self.set_condition_codes(self.registers.registers[f'R{dr}'])
    
    def execute_ldi(self, instruction):
        dr = (instruction >> 9) & 0x7
        pc_offset9 = instruction & 0x1FF
        if pc_offset9 & 0x100:
            pc_offset9 |= 0xFE00  # Sign extend
        address = (self.registers.PC + pc_offset9) & 0xFFFF
        indirect_address = self.memory.load(address)
        self.registers.registers[f'R{dr}'] = self.memory.load(indirect_address)
        self.set_condition_codes(self.registers.registers[f'R{dr}'])
    
    def execute_ldr(self, instruction):
        dr = (instruction >> 9) & 0x7
        base_r = (instruction >> 6) & 0x7
        offset6 = instruction & 0x3F
        if offset6 & 0x20:
            offset6 |= 0xFFC0  # Sign extend
        address = (self.registers.registers[f'R{base_r}'] + offset6) & 0xFFFF
        self.registers.registers[f'R{dr}'] = self.memory.load(address)
        self.set_condition_codes(self.registers.registers[f'R{dr}'])
    
    def execute_lea(self, instruction):
        dr = (instruction >> 9) & 0x7
        pc_offset9 = instruction & 0x1FF
        if pc_offset9 & 0x100:
            pc_offset9 |= 0xFE00  # Sign extend
        self.registers.registers[f'R{dr}'] = (self.registers.PC + pc_offset9) & 0xFFFF
        self.set_condition_codes(self.registers.registers[f'R{dr}'])
    
    def execute_not(self, instruction):
        dr = (instruction >> 9) & 0x7
        sr = (instruction >> 6) & 0x7
        self.registers.registers[f'R{dr}'] = ~self.registers.registers[f'R{sr}'] & 0xFFFF
        self.set_condition_codes(self.registers.registers[f'R{dr}'])
    
    def execute_st(self, instruction):
        sr = (instruction >> 9) & 0x7
        pc_offset9 = instruction & 0x1FF
        if pc_offset9 & 0x100:
            pc_offset9 |= 0xFE00  # Sign extend
        address = (self.registers.PC + pc_offset9) & 0xFFFF
        self.memory.store(address, self.registers.registers[f'R{sr}'])
    
    def execute_sti(self, instruction):
        sr = (instruction >> 9) & 0x7
        pc_offset9 = instruction & 0x1FF
        if pc_offset9 & 0x100:
            pc_offset9 |= 0xFE00  # Sign extend
        address = (self.registers.PC + pc_offset9) & 0xFFFF
        indirect_address = self.memory.load(address)
        self.memory.store(indirect_address, self.registers.registers[f'R{sr}'])
    
    def execute_str(self, instruction):
        sr = (instruction >> 9) & 0x7
        base_r = (instruction >> 6) & 0x7
        offset6 = instruction & 0x3F
        if offset6 & 0x20:
            offset6 |= 0xFFC0  # Sign extend
        address = (self.registers.registers[f'R{base_r}'] + offset6) & 0xFFFF
        self.memory.store(address, self.registers.registers[f'R{sr}'])
    
    def execute_trap(self, instruction):
        trapvect8 = instruction & 0xFF
        self.registers.registers['R7'] = self.registers.PC
        self.registers.PC = self.memory.load(trapvect8)
    
    def set_condition_codes(self, value):
        if value == 0:
            self.registers.CC = {'N': 0, 'Z': 1, 'P': 0}
        elif value & 0x8000:
            self.registers.CC = {'N': 1, 'Z': 0, 'P': 0}
        else:
            self.registers.CC = {'N': 0, 'Z': 0, 'P': 1}

class LC3Simulator:
    def __init__(self):
        self.registers = LC3Registers()
        self.memory = LC3Memory()
        self.control_unit = LC3ControlUnit(self.registers, self.memory)
    
    def load_program(self, program, start_address=0x3000):
        for i, instruction in enumerate(program):
            self.memory.store(start_address + i, instruction)
        self.registers.PC = start_address
    
    def run(self, steps=None):
        step_count = 0
        while steps is None or step_count < steps:
            # Fetch
            self.registers.IR = self.memory.load(self.registers.PC)
            self.registers.PC += 1
            
            # Decode and Execute
            self.control_unit.decode_and_execute()
            
            step_count += 1
    
    def peek_registers(self):
        return self.registers.registers
    
    def peek_memory(self, address, length=10):
        return self.memory.memory[address:address+length]
    
    def peek_cc(self):
        return self.registers.CC
    
    def peek_pc(self):
        return self.registers.PC
    
    def peek_ir(self):
        return self.registers.IR
