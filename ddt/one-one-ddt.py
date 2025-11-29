# Saturnin 1->1 DDT (single-bit input diffs vs single-bit output diffs)
# S-boxes from Saturnin spec:
s0 = [0, 6,14, 1,15, 4, 7,13, 9, 8,12, 5, 2,10, 3,11]
s1 = [0, 9,13, 2,15, 1,11, 7, 6, 4, 5, 3, 8,12,10,14]

def bit_positions(nbits=4):
    return [1 << i for i in range(nbits)]

def compute_1to1_ddt(sbox):
    """
    Returns a 4x4 matrix M where
      M[i][j] = number of x in 0..15 s.t.
                sbox[x] ^ sbox[x ^ in_diff] == out_diff
    where in_diff = 1<<i and out_diff = 1<<j (i,j in 0..3).
    """
    nbits = 4
    in_diffs = bit_positions(nbits)   # [1,2,4,8]
    out_diffs = bit_positions(nbits)
    M = [[0]*nbits for _ in range(nbits)]
    for i, ind in enumerate(in_diffs):
        for j, outd in enumerate(out_diffs):
            cnt = 0
            for x in range(16):
                y = x ^ ind
                if (sbox[x] ^ sbox[y]) == outd:
                    cnt += 1
            M[i][j] = cnt
    return M

def pretty_print_matrix(M, title):
    print(title)
    print("input-bit-diff -> output-bit-diff")
    header = " in\\out | " + " ".join(f"{1<<j:2d}" for j in range(4))
    print(header)
    print("-" * len(header))
    for i,row in enumerate(M):
        print(f"  {1<<i:2d}    | " + " ".join(f"{v:2d}" for v in row))
    print()

if __name__ == "__main__":
    M0 = compute_1to1_ddt(s0)
    M1 = compute_1to1_ddt(s1)
    pretty_print_matrix(M0, "σ0  (Saturnin) 1→1 DDT (rows: input single-bit diffs, cols: output single-bit diffs)")
    pretty_print_matrix(M1, "σ1  (Saturnin) 1→1 DDT (rows: input single-bit diffs, cols: output single-bit diffs)")
