from sage.all import *   # Use Sage inside Python

# === Define Boolean ring ===
B = BooleanPolynomialRing(4, 'a')
a0, a1, a2, a3 = B.gens()

# === Your 4×4 S-box ===
S = [0, 6, 14, 1, 15, 4, 7, 13, 9, 8, 12, 5, 2, 10, 3, 11]

# === Helper functions ===
def int_to_bits(x, n=4):
    return [(x >> i) & 1 for i in range(n)]

def get_anf(S, n=4):
    anf = []
    for bit in range(n):
        monomials = []
        for x in range(1 << n):
            in_bits = int_to_bits(x, n)
            out_bit = (S[x] >> bit) & 1
            if out_bit:
                term = 1
                for i, b in enumerate(in_bits):
                    term *= (a0, a1, a2, a3)[i] if b else (1 + (a0, a1, a2, a3)[i])
                monomials.append(term)
        f = sum(monomials)
        anf.append(f)
    return anf

# === Compute ANF ===
anf = get_anf(S)

print("=== ANF (Boolean form) ===")
for i, f in enumerate(anf):
    print(f"b[{i}] = {f}")

print("\n=== Verilog form ===")
for i, f in enumerate(anf):
    expr = str(f).replace("+", " ^ ").replace("*", "&")
    print(f"assign b[{i}] = {expr};")

# === Verify correctness ===
def verify(anf, S):
    for x in range(16):
        bits = int_to_bits(x)
        out_bits = [int(f(*bits)) for f in anf]
        val = sum(out_bits[i]<<i for i in range(4))
        assert val == S[x], f"Mismatch at input {x}"
    print("\n✅ ANF verified correctly!")

verify(anf, S)
