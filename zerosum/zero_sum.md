# 🧩 Zero-Sum Properties of S-boxes

### 📘 Overview

The **zero-sum property** is an important algebraic and structural feature of an S-box.
It reveals symmetries in how outputs combine under XOR — which can help detect hidden linearities or special balance properties.

There are two related concepts:

1. **Global zero-sum** — when all outputs XOR to 0.
2. **Subset (trail) zero-sum** — when a specific subset of inputs produces outputs that XOR to 0.

---

## ⚙️ 1. Global Zero-Sum Property

### 🧮 Definition

For an n-bit S-box ( S : {0,1}^n \to {0,1}^n ):

[
\bigoplus_{x=0}^{2^n - 1} S(x) = 0
]

That means if you XOR together **all output values** of the S-box,
the result is zero.

This shows that the S-box is **balanced** in a global sense —
its outputs are evenly distributed across all bit positions.

---

### 💻 Example Code

```python
def global_zero_sum(sbox):
    xor_value = 0
    for y in sbox:
        xor_value ^= y
    return xor_value == 0, xor_value

S0 = [0, 6,14, 1,15, 4, 7,13, 9, 8,12, 5, 2,10, 3,11]
ok, xor_val = global_zero_sum(S0)
print("S0 global zero-sum:", ok, "| XOR =", hex(xor_val))
```

**Output:**

```
S0 global zero-sum: True | XOR = 0x0
```

✅ Interpretation:

* The XOR of all 16 outputs = 0.
* Hence, S0 satisfies the **global zero-sum property**.

---

## 🧠 2. Zero-Sum Subset (Trail) Property

### 🧮 Definition

The subset zero-sum property looks for a **nontrivial subset** of inputs ( \mathcal{S} \subset {0,1}^n ) such that:

[
\bigoplus_{x \in \mathcal{S}} S(x) = 0
]

Unlike the global one (which uses *all inputs*),
this focuses on specific groups of inputs whose outputs cancel out.

Such subsets are called **zero-sum trails**.

---

### 💻 Example Code

```python
import itertools

def zero_sum_trails(sbox):
    n = len(sbox)
    for r in range(2, n):  # skip size 1 and full set
        for subset in itertools.combinations(range(n), r):
            xor_val = 0
            for i in subset:
                xor_val ^= sbox[i]
            if xor_val == 0:
                return subset  # first nontrivial zero-sum found
    return None

S0 = [0, 6,14, 1,15, 4, 7,13, 9, 8,12, 5, 2,10, 3,11]
trail = zero_sum_trails(S0)
if trail:
    print(f"S0 has a zero-sum trail: {trail}")
else:
    print("S0 has no nontrivial zero-sum subsets.")
```

**Output:**

```
S0 has a zero-sum trail: (1, 2, 9)
```

✅ Meaning:
Inputs 1, 2, and 9 produce outputs that XOR to 0.
Their XOR cancels exactly:

```
S0[1] ^ S0[2] ^ S0[9] = 6 ^ 14 ^ 8 = 0
```

---

## 🔍 3. Why It Matters

| Property            | What It Means                             | Cryptographic Relevance                    |
| :------------------ | :---------------------------------------- | :----------------------------------------- |
| Global zero-sum     | The S-box’s outputs are globally balanced | Ensures no output bias                     |
| Zero-sum trail      | Some subset of inputs cancel exactly      | Can signal structural weakness or symmetry |
| No zero-sum subsets | Desirable — indicates good diffusion      | Harder to exploit algebraically            |

---

## 🧮 4. Connecting to Higher-Order Differentials

The **zero-sum subset property** is mathematically related to **higher-order differentials**:

* A *k*-th order derivative over a set of (2^k) inputs is a zero-sum if the function’s degree ≤ *k – 1*.
* So, finding zero-sum subsets is like experimentally checking higher-order derivative cancellations — but restricted to special input sets.

That’s why we used similar XOR accumulation logic for both **S-box analysis** and **cipher-level zero-sum tests**.

---

## 🧾 Summary

| Concept             | Definition                                                       | Example Outcome                         |
| :------------------ | :--------------------------------------------------------------- | :-------------------------------------- |
| **Global Zero-Sum** | XOR of all outputs = 0                                           | Balanced outputs                        |
| **Zero-Sum Trail**  | XOR of some outputs = 0                                          | Possible internal symmetry              |
| **Both True**       | S-box is globally balanced *and* has specific cancelling subsets | Can be good or bad depending on context |

---

## ✅ Example Results (from our experiments)

| S-box | Global Zero-Sum | Example Trail |
| :---- | :-------------- | :------------ |
| S0    | ✅ Yes           | (1, 2, 9)     |
| S1    | ✅ Yes           | (1, 2, 9)     |

Both S-boxes satisfy the **global** property
and exhibit **nontrivial zero-sum subsets**, meaning certain input patterns cause perfect cancellation.

---

### 🧠 Takeaway

> The zero-sum property gives a simple but deep look into the balance and internal symmetries of an S-box.
>
> * Global zero-sum ensures overall diffusion balance.
> * Subset zero-sum trails expose special input groups that might interact linearly under some conditions.

---
