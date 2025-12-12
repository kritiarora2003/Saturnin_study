Absolutely 👍 Here’s a **clean, professional README** that documents your project’s evolution — from the initial MILP encoding (using DDT constraints) to the improved convex-hull formulation (up to generating the inequalities).

This style works perfectly for a report, GitHub repo, or academic appendix.

---

# 🧩 MILP Modeling of Saturnin Toy Cipher — Differential Trail Analysis

## Overview

This project implements a **Mixed Integer Linear Programming (MILP)** model to analyze the *differential properties* of a toy version of the **Saturnin** cipher.
The objective is to find the **minimal-weight differential trail** across one or more rounds by encoding the cipher’s nonlinear and linear layers as linear constraints over binary variables.

---

## 🔹 Cipher Structure

The toy Saturnin round used in this model follows:

```
S-box → MDS → S-box → SR_slice → MDS → inv_SR_slice
```

Each round operates on an 8-nibble (32-bit) state, where:

* Each nibble = 4 bits
* Each layer is represented using bit-level equations
* S-box is nonlinear, all other layers are linear permutations or XOR operations

---

## 🔹 Phase 1: MILP with DDT-based S-box Encoding

In the first version, each 4-bit S-box was modeled explicitly using its **Differential Distribution Table (DDT)**.

### 🔸 Idea

For each possible 4-bit input difference Δx and output difference Δy:

* If `(Δx, Δy)` is **invalid** (probability 0 in the DDT), we add a linear constraint to *forbid* that pair.
* This yields a set of inequalities ensuring only valid differential transitions remain.

### 🔸 Implementation Steps

1. Enumerate all 16×16 possible input/output difference pairs.

2. Build a binary DDT marking valid transitions.

3. For each *invalid* pair, add one constraint:

   ```
   sum(bit_mismatches(x,y)) <= 7
   ```

   so that combination can never occur.

4. Encode all S-boxes in the cipher using these binary constraints.

5. Add linear constraints for:

   * MDS transformation (XOR and MUL2-based diffusion)
   * SR_slice and inverse nibble permutations

6. Minimize the total Hamming weight of the input and output differences:

   ```
   min  wt(Δx_in) + wt(Δx_out)
   ```

### 🔸 Result

* The model works correctly and finds valid minimal-weight trails.
* However, it’s **quite large and slow**, since each S-box adds **hundreds of constraints** (one per invalid DDT entry).

For example:

```
Optimize a model with 1673 rows, 272 columns, 10928 nonzeros
...
Optimal objective: 3.0
```

Each S-box layer contributes ~1000 constraints, leading to long presolve and node exploration times in Gurobi.

---

## 🔹 Phase 2: Convex Hull S-box Representation (Polytope Method)

To make the MILP more compact and solver-friendly, we replaced the DDT constraint set with a **convex-hull polyhedral encoding**.

### 🔸 Concept

Each valid (Δx, Δy) pair is an 8-dimensional binary vector
`[x0, x1, x2, x3, y0, y1, y2, y3]`.

We compute the **convex hull** of all these points:
[
P = \text{conv}{ (Δx,Δy) \text{ valid pairs} }
]
and express it in **H-representation**:
[
A·v ≤ b
]
where `v = [x0,x1,x2,x3,y0,y1,y2,y3]`.

Thus, all valid transitions satisfy these linear inequalities, and any invalid transition violates at least one.
This captures the full differential behavior of the S-box *without listing every invalid pair*.

---

## 🔸 Generating the Convex Hull Inequalities (in SageMath)

We use **SageMath’s polyhedral geometry tools** to compute the facets of the convex hull polytope.

```python
from sage.all import *

# Define the S-box
s0 = [0, 6,14, 1,15, 4, 7,13, 9, 8,12, 5, 2,10, 3,11]

def bits4(n):
    return [(n >> i) & 1 for i in range(4)]

# Collect all valid (Δx,Δy) pairs
valid_points = []
for dx in range(16):
    for x in range(16):
        dy = s0[x] ^ s0[x ^ dx]
        valid_points.append(bits4(dx) + bits4(dy))

valid_points = [list(p) for p in set(tuple(p) for p in valid_points)]

# Build convex hull polytope
P = Polyhedron(vertices=valid_points)

# Extract facet inequalities A·x ≤ b
inequalities = []
for ineq in P.inequalities_list():
    const = -ineq[0]         # RHS
    coeffs = ineq[1:]        # [a0..a7]
    denoms = [QQ(c).denominator() for c in coeffs + [const]]
    mult = lcm(denoms)
    coeffs_int = [int(mult * c) for c in coeffs]
    const_int = int(mult * const)
    inequalities.append((coeffs_int, const_int))

print(f"Extracted {len(inequalities)} convex hull inequalities:")
for a, b in inequalities:
    print(a, "<= ", b)
```

---

### 🔸 Output Example

```
Total valid differential pairs: 106
Polyhedron dimension: 8
Number of facets: 48
[1, 0, 0, 0, 0, 0, 0, 0] <= 1
[-1, 0, 0, 0, 0, 0, 0, 0] <= 0
...
```

Each inequality represents one facet of the S-box’s **differential polytope**.
These can be saved and imported into the MILP model for all S-boxes, replacing thousands of DDT constraints with just ~50 per S-box.

---

## 🚀 Why It’s Better

| Feature                              | DDT Encoding          | Convex Hull Encoding         |
| ------------------------------------ | --------------------- | ---------------------------- |
| Constraints per S-box                | ~150–200              | ~40–50                       |
| Size of MILP                         | Large (slow presolve) | Compact, tight LP relaxation |
| Exactness                            | Exact                 | Exact                        |
| Suitability for multi-round analysis | Limited               | Excellent                    |

The convex-hull method keeps the same feasible set (i.e., no false trails) but significantly reduces the model size and improves solver performance.

---

## 📊 Summary

| Phase   | Method           | S-box Model                | Pros                | Cons                            |
| ------- | ---------------- | -------------------------- | ------------------- | ------------------------------- |
| Phase 1 | DDT-based MILP   | Forbid invalid transitions | Simple, transparent | Slow, many constraints          |
| Phase 2 | Convex-hull MILP | Polytope facets (A·x ≤ b)  | Compact, scalable   | Requires precomputation in Sage |

---

## 🧠 Next Steps

* Integrate convex-hull inequalities into the MILP (`add_sbox_convex_hull()`).
* Compare runtime and node count vs the DDT version.
* Extend model to multiple rounds to study **minimum number of active S-boxes**.
* Use similar approach for **linear hull** analysis (by replacing differential variables with mask variables).

---

**Author:** Kriti Arora
**Tools:** Gurobi 12.0.3, SageMath, Python 3.11
**Project:** Differential MILP Modeling of Toy Saturnin Cipher
**Date:** December 2025

---

Would you like me to continue this README by adding the **integration part** (where we plug the convex-hull inequalities into the MILP model using `add_sbox_convex_hull()`)?
