from lc3 import LC3Simulator

# Example program: ADD R1, R2, #3; AND R0, R2, R0; BRnzp #1
program = [0x1263, 0x5040, 0x0E01]

sim = LC3Simulator()
sim.load_program(program)

# Run the simulation for a few steps
sim.run(steps=2)

# Peek at values
print("Registers:", sim.peek_registers())
print("Condition Codes:", sim.peek_cc())
print("PC:", sim.peek_pc())
print("IR:", sim.peek_ir())
print("Memory at 0x3000:", sim.peek_memory(0x3000, length=3))
