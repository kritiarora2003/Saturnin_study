# 🧮 Finding the Algebraic Degree of an S-box Using Boolean Derivatives

### 📘 Overview

The **algebraic degree** of an S-box measures how nonlinear it is —
that is, the degree of its highest-order term when written in Algebraic Normal Form (ANF).

Instead of expanding the S-box algebraically,
we can determine its degree using **iterated Boolean derivatives**.
This method is elegant, general, and directly connected to higher-order differentials.

---

## 🧩 1. Boolean Derivative — the Key Idea

For a Boolean function ( f : {0,1}^n \to {0,1} ),
its **derivative** in direction (a) is defined as:

[
\Delta_a f(x) = f(x) \oplus f(x \oplus a)
]

This measures how much (f) changes when you flip bits indicated by (a).

* If ( \Delta_a f(x) = 0 ) for all (x), the function is constant (degree 0).
* Otherwise, it has some nonlinearity.

---

## ⚙️ 2. Higher-Order Derivatives

We can apply differentiation repeatedly with different directions:

[
\Delta_{a_1, a_2, \dots, a_k} f(x) = \bigoplus_{I \subseteq {1,2,\dots,k}} f!\left(x \oplus \bigoplus_{i \in I} a_i\right)
]

Each new derivative doubles the number of points in the XOR sum.

| Order | Meaning                 | XOR terms |
| :---- | :---------------------- | :-------- |
| 1st   | (\Delta_a f(x))         | 2         |
| 2nd   | (\Delta_{a,b} f(x))     | 4         |
| 3rd   | (\Delta_{a,b,c} f(x))   | 8         |
| 4th   | (\Delta_{a,b,c,d} f(x)) | 16        |

---

## 🧠 3. Relationship Between Derivatives and Degree

A fundamental property connects differentiation to algebraic degree:

[
\Delta_{a_1,\dots,a_k} f(x) = 0 \text{ for all } x \quad \iff \quad \deg(f) < k
]

This means:

* 1st derivative vanishes → degree = 0 (constant)
* 2nd derivative vanishes → degree = 1 (linear)
* 3rd derivative vanishes → degree = 2 (quadratic)
* 4th derivative vanishes → degree = 3 (cubic)

So, the first derivative order at which **everything becomes zero** tells us the algebraic degree.

---

## 🔁 4. Iterative Derivative Algorithm

The idea of your code is simple:

1. Start from the function’s truth table.
2. Compute derivatives in all possible directions.
3. If *any* derivative is nonzero → degree not reached yet.
4. Replace your function set with those derivatives and repeat.
5. Stop once all derivatives vanish — the number of iterations = algebraic degree.

---

### 🧩 Core Logic

```python
def degree_of_boolean_function(f, n):
    deg = 0
    derivatives = {tuple(f)}  # start with the function itself
    while True:
        new_derivatives = set()
        for d in range(1 << n):         # all directions
            for val in derivatives:     # all current derivatives
                df = derivative(list(val), d, n)
                if any(df):             # if derivative not zero
                    new_derivatives.add(tuple(df))
        if not new_derivatives:         # all vanished
            return deg
        derivatives = new_derivatives
        deg += 1
```

At each iteration, the function checks whether **all** current derivatives vanish.
If they do → the function’s degree = number of iterations taken.

---

## 💡 5. Applying It to an S-box

Each output bit of an S-box is a separate Boolean function.
You compute its degree using the above method,
and the **S-box degree** is the **maximum** among all output bits.

```python
def sbox_degree(sbox, n=4, m=4):
    degrees = []
    for bit in range(m):
        f = [((sbox[x] >> bit) & 1) for x in range(1 << n)]
        deg = degree_of_boolean_function(f, n)
        degrees.append(deg)
    return max(degrees), degrees
```

---

## 🧮 Example Result

For your toy S-boxes:

```python
S0 = [0,6,14,1,15,4,7,13,9,8,12,5,2,10,3,11]
S1 = [0,9,13,2,15,1,11,7,6,4,5,3,8,12,10,14]
```

Running the code yields:

```
S0 degree: (3, [3, 3, 2, 3])
S1 degree: (3, [3, 3, 3, 2])
```

✅ Both have **maximum algebraic degree = 3**
→ meaning each output bit is at most cubic in its input variables.

---

## 🔍 6. Intuition Behind the Method

Each derivative strips away one layer of nonlinearity:

* The first derivative removes constants.
* The second removes linear terms.
* The third removes quadratics.
* The fourth removes cubics.

When nothing remains (the function becomes flat),
you’ve stripped all nonlinear layers — that’s the degree.

---

## 📈 7. Summary

| Step | Description                                      |
| :--- | :----------------------------------------------- |
| 1    | Represent each output bit as a Boolean function  |
| 2    | Compute all possible derivatives iteratively     |
| 3    | Count how many rounds until every derivative = 0 |
| 4    | That count = algebraic degree of the function    |
| 5    | Take the max over all bits → S-box degree        |

---

### 🧾 Key Takeaway

> A function’s algebraic degree is the number of times you can “differentiate” it (in all directions) before it becomes constant.
> The iterative Boolean derivative method captures this exactly, without any symbolic algebra.

---

