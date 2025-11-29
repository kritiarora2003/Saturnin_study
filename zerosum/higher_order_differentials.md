# 🔍 Understanding Higher-Order Boolean Differentials and the Zero-Sum Property

### 📘 Overview

This document explains how Boolean derivatives, higher-order differentials, and the zero-sum (integral) property are connected — and how these ideas reveal the algebraic degree and diffusion behaviour of block ciphers like the **toy Saturnin**.

---

## 🧩 1. Boolean Derivative — the Core Idea

In normal calculus, a derivative measures how much a function changes when its input changes slightly.
In Boolean algebra, we define an analogous concept — the **Boolean derivative** — using XOR (⊕) instead of subtraction.

For a Boolean function ( f : {0,1}^n \to {0,1} ),
the derivative in direction (a) is:

[
\Delta_a f(x) = f(x) \oplus f(x \oplus a)
]

It answers:

> “Does flipping bits given by mask (a) change the output of (f)?”

If yes → output is 1,
if no → output is 0.

---

## ⚙️ 2. Second-Order and Higher-Order Differentiation

We can apply the derivative repeatedly with different directions.

### 🔹 Second-Order Example:

[
\Delta_{a,b} f(x) = f(x) \oplus f(x \oplus a) \oplus f(x \oplus b) \oplus f(x \oplus a \oplus b)
]

Each new direction doubles the number of terms you XOR together.

| Order | Directions | Number of XOR terms |
| :---- | :--------- | :-----------------: |
| 1st   | (a)        |          2          |
| 2nd   | (a,b)      |          4          |
| 3rd   | (a,b,c)    |          8          |
| 4th   | (a,b,c,d)  |          16         |

These sets of inputs form an **affine cube** in the input space.

---

## ⚡ 3. Taking Derivatives in the Same Direction

If you take derivatives in the **same direction twice**:

[
\Delta_{a,a} f(x) = 0
]

Why?
Flipping the same bits twice brings you back to the original input, so the overall “change in change” is zero.
This property holds for any Boolean function.

---

## 🧮 4. Differentiation and Algebraic Degree

The **algebraic degree** of a Boolean function is the degree of its highest-order monomial in its Algebraic Normal Form (ANF).

A crucial relationship:
[
\Delta_{a_1,\dots,a_k} f(x) = 0 \text{ for all } x \iff \deg(f) < k
]

So:

* If (f) is linear (deg 1) → 2nd derivative = 0
* If (f) is quadratic (deg 2) → 3rd derivative = 0
* If (f) is cubic (deg 3) → 4th derivative = 0

---

## 🧠 5. The Zero-Sum (Integral) Property

For an S-box or round function of degree ≤ 3,
the XOR of all outputs over a **4-dimensional cube** of inputs equals zero:

[
\bigoplus_{I \subseteq {1,2,3,4}} F!\left(x \oplus \bigoplus_{i \in I} a_i\right) = 0
]

This vanishing XOR is known as a **zero-sum** or **integral property**.
It’s the practical manifestation of the 4th-order derivative being zero.

---

## 🧩 6. Application to Toy Saturnin

* Each S-box is **cubic** → degree 3.
* Linear layers (MDS, key XOR) don’t increase degree.
* So, after 1 round, the cipher’s degree ≤ 3 → 4th derivative (XOR over 16 points) = 0.
* After several rounds, nonlinear terms multiply and spread, raising the degree > 3 → 4th derivative ≠ 0.

**Experimental observation:**

| Rounds | XOR result     | Interpretation                       |
| :----- | :------------- | :----------------------------------- |
| 1      | All zeros      | Degree ≤ 3 → 4th derivative vanishes |
| 2      | All zeros      | Degree growth not yet visible        |
| 3      | Random nonzero | Degree > 3                           |
| 4+     | Random nonzero | Fully diffused                       |

---

## 🔬 7. Why This Matters

Higher-order derivatives and zero-sum tests are powerful tools to:

* Measure **algebraic degree growth** of a cipher.
* Detect how quickly **nonlinearity spreads**.
* Identify the boundary between **structured** and **pseudorandom** behaviour.

This is exactly the basis of **higher-order differential** and **integral cryptanalysis**.

---

## 🧾 Summary

| Concept                 | Meaning                                    |
| :---------------------- | :----------------------------------------- |
| Boolean derivative      | XOR-based “change detector”                |
| Higher-order derivative | XOR of outputs over affine cube            |
| Same direction twice    | Always 0                                   |
| k-th derivative = 0     | Function degree ≤ k – 1                    |
| Zero-sum property       | Practical test for low algebraic degree    |
| Degree growth           | Indicates rounds needed for full diffusion |

---
