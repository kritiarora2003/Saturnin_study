def generate_bct(sbox):
    N = len(sbox)
    if N & (N-1) != 0:
        raise ValueError("sbox length must be a power of two")
    if sorted(sbox) != list(range(N)):
        raise ValueError("sbox must be a permutation of 0..N-1")
    inv = [0]*N
    for i, v in enumerate(sbox):
        inv[v] = i
    bct = [[0]*N for _ in range(N)]
    for a in range(N):
        for b in range(N):
            count = 0
            for x in range(N):
                lhs = inv[sbox[x] ^ b]
                rhs = inv[sbox[x ^ a] ^ b]
                if (lhs ^ rhs) == a:
                    count += 1
            bct[a][b] = count
    return bct

# Define Saturnin S-boxes
sbox0 = [0x6, 0x9, 0x0, 0xE, 0x1, 0x5, 0x4, 0x7, 0xB, 0xD, 0x8, 0xF, 0x3, 0x2, 0xC, 0xA]
sbox1 = [0x3, 0xC, 0xA, 0x1, 0x2, 0x0, 0xB, 0x7, 0x5, 0x9, 0xE, 0xF, 0x8, 0x4, 0x6, 0xD]
present_sbox = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
                0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]


bct0 = generate_bct(sbox0)
bct1 = generate_bct(sbox1)
bct_present = generate_bct(present_sbox)

def print_bct_table(bct, name="S-box"):
    """
    Pretty print a Boomerang Connectivity Table (BCT) with hex headers.
    """
    n = len(bct)
    print(f"\n{name} (Boomerang Connectivity Table):\n")
    
    # Header row
    header = "a\\b | " + " ".join(f"{b:2X}" for b in range(n))
    print(header)
    print("-" * len(header))
    
    # Each row
    for a, row in enumerate(bct):
        row_str = " ".join(f"{v:2}" for v in row)
        print(f"{a:2X}  | {row_str}")


# After generating the BCTs
print_bct_table(bct0, "σ₀")
print_bct_table(bct1, "σ₁")
print_bct_table(bct_present, "present sbox bct")


