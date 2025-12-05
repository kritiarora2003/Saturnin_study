import gurobipy as gp
from gurobipy import GRB

# Number of nibbles in toy Saturnin
N = 8

# Create model
m = gp.Model("ToySaturnin_MILP")

# Binary variables: activity of each nibble
x_in = m.addVars(N, vtype=GRB.BINARY, name="x_in")
x_sbox = m.addVars(N, vtype=GRB.BINARY, name="x_sbox")
x_mds = m.addVars(N, vtype=GRB.BINARY, name="x_mds")

# Objective: minimize total active S-boxes
m.setObjective(gp.quicksum(x_sbox[i] for i in range(N)), GRB.MINIMIZE)

# 1️⃣ S-box activity propagation: 
# If input active → output active (simple linear constraint)
for i in range(N):
    m.addConstr(x_sbox[i] >= x_in[i], f"Sbox_{i}")

# 2️⃣ MDS diffusion (toy version)
# MDS mixes all nibbles → if any x_sbox active, all x_mds can become active
# We'll approximate by: x_mds[i] >= (1/N) * sum(x_sbox)
for i in range(N):
    m.addConstr(x_mds[i] * N >= gp.quicksum(x_sbox[j] for j in range(N)), f"MDS_{i}")

# 3️⃣ Non-trivial input (avoid all zeros)
m.addConstr(gp.quicksum(x_in[i] for i in range(N)) >= 1, "Nontrivial")

# Solve
m.optimize()

# Print results
print("\n=== MILP Results ===")
for i in range(N):
    print(f"x_in[{i}]   = {int(x_in[i].X)}")
for i in range(N):
    print(f"x_sbox[{i}] = {int(x_sbox[i].X)}")
for i in range(N):
    print(f"x_mds[{i}]  = {int(x_mds[i].X)}")

print(f"\nTotal active S-boxes = {m.objVal}")
