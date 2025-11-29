#!/usr/bin/env python
# coding: utf-8

# # Toy saturnin implementation

# ### The state is 8x4 rather than the 16x16 of the original
# Below is the s box, tried and tested to be correct

# In[193]:


def sbox_kriti(state):
    a, b ,c ,d = state[0], state[1], state[2], state[3]
    # Implement the S-box logic here
    a ^= b & c
    print("a is ", a)
    b ^= a | d
    print("b is ", b)
    d ^= b | c
    print("d is ", d)
    c ^= b & d
    print("c is ", c)
    b ^= a | c
    print("b is ", b)
    a ^= b | d
    print("a is ", a)
    state[0], state[1], state[2], state[3] = b,c,d,a
    print("state is ", state)

    a, b, c, d = state[4], state[5], state[6], state[7]
    a ^= b & c
    b ^= a | d
    d ^= b | c
    c ^= b & d
    b ^= a | c
    a ^= b | d
    state[4], state[5], state[6], state[7] = d,b,a,c   
    return state 


def sbox_inv_kriti(state):
    b,c,d,a = state[0], state[1], state[2], state[3]
    # Implement the S-box logic here
    a ^= b | d
    b ^= a | c
    c ^= b & d
    d ^= b | c
    b ^= a | d
    a ^= b & c
    state[0], state[1], state[2], state[3] = a,b,c,d
    print("state is ", state)

    d,b,a,c = state[4], state[5], state[6], state[7]
    a ^= b | d
    b ^= a | c
    c ^= b & d
    d ^= b | c
    b ^= a | d
    a ^= b & c
    state[4], state[5], state[6], state[7] = a,b,c,d 
    return state 


# In[194]:


state = [1,0,0,0,0,0,0,0]
print("Input state:     ", [(x) for x in state])
state_sboxed = sbox_kriti(state)
print("After S-box:     ", [(x) for x in state_sboxed])
state_sboxed_inv = sbox_inv_kriti(state_sboxed)
print("After S-box inv: ", [(x) for x in state_sboxed_inv])


# ## Making round constants (same as original implementation)

# In[195]:


def make_round_constants(R):
    rc0 = []
    rc1 = []

    # 4-bit LFSR seeds (we keep them 4-bit)
    x0 = 0b1011   # arbitrary but fixed
    x1 = 0b1101

    for r in range(R):
        # Run 4-bit LFSRs for 4 cycles
        for _ in range(4):
            # LFSR taps chosen to give good period for 4-bit
            fb0 = (x0 >> 3) & 1
            x0 = ((x0 << 1) & 0xF) ^ (fb0 * 0b0011)

            fb1 = (x1 >> 3) & 1
            x1 = ((x1 << 1) & 0xF) ^ (fb1 * 0b0101)

        rc0.append(x0 & 0xF)
        rc1.append(x1 & 0xF)

    return rc0, rc1


# ## making xor key and xor rotated key functions (same as original implementation)

# In[196]:


def xor_key(key, state):
    """
    XOR the 8×4-bit state with the 8×4-bit key.
    """
    for i in range(8):
        state[i] ^= (key[i] & 0xF)   # ensure 4-bit result
        state[i] &= 0xF
    return state


def rol4(x, r):
    """4-bit rotate left."""
    return ((x << r) | (x >> (4 - r))) & 0xF


def xor_key_rotated(key, state):
    """
    XOR the state with the key rotated left by 3 bits (because 11 mod 4 = 3).
    """
    for i in range(8):
        rotated = rol4(key[i], 3)   # rotate-left 3 bits
        state[i] ^= rotated
        state[i] &= 0xF  
        
    return state           # enforce 4-bit state


# ## Shift rows functions
# ### Similar to the original just scaled down
# 
# The original had slice rotations and sheet rotations so first row no rotation, 2nd row 1 rotation, 3rd row 2 rotation and so on (exactly like aes). 
# but in the toy we only have 2 rows in sheets and slices

# In[197]:


def SR_slice(state):
    """
    Toy SR_slice: on state[4..7], apply nibble permutation:
        abcd → badc
    """

    new_state = state.copy()

    for i in range(4, 8):
        x = state[i] & 0xF

        a = (x >> 3) & 1
        b = (x >> 2) & 1
        c = (x >> 1) & 1
        d = (x >> 0) & 1

        # abcd → badc
        new = (b << 3) | (a << 2) | (d << 1) | (c << 0)

        new_state[i] = new

    return new_state


def inv_SR_slice(state):
    """
    Inverse of toy SR_slice: on state[4..7], undo nibble permutation:
        badc → abcd
    """

    new_state = state.copy()

    for i in range(4, 8):
        x = state[i] & 0xF

        b = (x >> 3) & 1
        a = (x >> 2) & 1
        d = (x >> 1) & 1
        c = (x >> 0) & 1

        # inverse: badc → abcd
        new = (a << 3) | (b << 2) | (c << 1) | (d << 0)

        new_state[i] = new

    return new_state


# In[198]:


state = [1,2,3,4,5,6,7,8]
print("Input state:     ", [(x) for x in state])
state_sr_sliced = SR_slice(state)
print("After SR_slice:  ", [(x) for x in state_sr_sliced])
state_sr_sliced_inv = SR_slice_inv(state_sr_sliced)
print("After SR_slice_inv:", [(x) for x in state_sr_sliced_inv])


# In[199]:


def SR_sheet(state):
    """
    Toy SR_sheet for registers 4..7.
    Nibble permutation: abcd → cdab
    """

    new_state = state.copy()

    for i in range(4, 8):
        x = state[i] & 0xF

        a = (x >> 3) & 1
        b = (x >> 2) & 1
        c = (x >> 1) & 1
        d = (x >> 0) & 1

        # abcd → cdab
        new = (c << 3) | (d << 2) | (a << 1) | (b << 0)

        new_state[i] = new

    return new_state


def inv_SR_sheet(state):
    """
    Inverse of toy SR_sheet.
    Undo nibble permutation: cdab → abcd
    """

    new_state = state.copy()

    for i in range(4, 8):
        x = state[i] & 0xF

        c = (x >> 3) & 1
        d = (x >> 2) & 1
        a = (x >> 1) & 1
        b = (x >> 0) & 1

        # inverse: cdab → abcd
        new = (a << 3) | (b << 2) | (c << 1) | (d << 0)

        new_state[i] = new

    return new_state


# In[200]:


state = [1,2,3,4,5,6,7,8]
print("Input State:     ", [(x) for x in state])
state_sr = SR_sheet(state)
print("After SR sheet:  ", [(x) for x in state_sr])
state_inv_sr = inv_SR_sheet(state_sr)
print("After inv SR:    ", [(x) for x in state_inv_sr])


# ## Trying to implement mds here and checking if its coming to be an involution or not
# (it is)

# So the original saturning mds was divided into 4 groups of 4 registers each, here I have done to convert into into 4 groups of 2 registers each. 
# 
# I've changed the rotation from 4 term thing to 2 term thing (the mul function)
# 
# And the rest, same operations are applied

# In[201]:


def mul2(t0, t1):
    """Simple 2x2 rotation + xor for each pair"""
    tmp = t0
    t0 = t1
    t1 = tmp ^ t0
    return t0, t1

def mds(state):
    # state: list of 8 nibbles [a0,a1,b0,b1,c0,c1,d0,d1]
    x0, x1, x2, x3, x4, x5, x6, x7 = state

    # Split into pairs: A = x0,x1, B = x2,x3, C = x4,x5, D = x6,x7
    # Step 1: Local XORs like Saturnin
    x4 ^= x6  # C ^= D
    x5 ^= x7
    x0 ^= x2  # A ^= B
    x1 ^= x3

    # Step 2: Apply MUL2 to each pair
    x2, x3 = mul2(x2, x3)  # B = MUL2(B)
    x6, x7 = mul2(x6, x7)  # D = MUL2(D)

    # Step 3: More XORs
    x2 ^= x4  # B ^= C
    x3 ^= x5
    x6 ^= x0  # D ^= A
    x7 ^= x1

    # Step 4: Apply MUL2 twice to A and C
    x0, x1 = mul2(*mul2(x0, x1))  # A = MUL2²(A)
    x4, x5 = mul2(*mul2(x4, x5))  # C = MUL2²(C)

    # Step 5: Final XORs
    x4 ^= x6  # C ^= D
    x5 ^= x7
    x0 ^= x2  # A ^= B
    x1 ^= x3
    x2 ^= x4  # B ^= C
    x3 ^= x5
    x6 ^= x0  # D ^= A
    x7 ^= x1

    return [x0, x1, x2, x3, x4, x5, x6, x7]


def inv_mul2(u0, u1):
    # Reverse the steps of mul2
    t1 = u0
    t0 = u1 ^ t1
    return t0, t1


def inv_mds(state):
    # state: list of 8 nibbles [x0..x7]
    x0, x1, x2, x3, x4, x5, x6, x7 = state

    # Step 1: Reverse final XORs
    x6 ^= x0  # D ^= A
    x7 ^= x1
    x2 ^= x4  # B ^= C
    x3 ^= x5
    x0 ^= x2  # A ^= B
    x1 ^= x3
    x4 ^= x6  # C ^= D
    x5 ^= x7

    # Step 2: Reverse MUL2² on A and C
    x0, x1 = inv_mul2(*inv_mul2(x0, x1))
    x4, x5 = inv_mul2(*inv_mul2(x4, x5))

    # Step 3: Reverse XORs before MUL2
    x6 ^= x0  # D ^= A
    x7 ^= x1
    x2 ^= x4  # B ^= C
    x3 ^= x5

    # Step 4: Reverse MUL2 on B and D
    x2, x3 = inv_mul2(x2, x3)
    x6, x7 = inv_mul2(x6, x7)

    # Step 5: Reverse initial XORs
    x0 ^= x2  # A ^= B
    x1 ^= x3
    x4 ^= x6  # C ^= D
    x5 ^= x7

    return [x0, x1, x2, x3, x4, x5, x6, x7]


# In[202]:


# Random 8-nibble state
state = [1,2,3,4,5,6,7,8]
state = [1,0,0,0,0,0,0,0]
state = [0,0,0,0,0,0,0,1]
state = [0,1,0,0,0,0,0,0]
state = [0,0,0,1,0,0,0,0]
print("Original:", state)

fwd = mds(state)
print("After MDS:", fwd)

inv = inv_mds(fwd)
print("After inverse:", inv)

print("Correct:", inv == state)


# In[203]:


import random

def average_diffusion(mds_func, trials=100):
    n = 8  # number of nibbles
    total_flipped = 0
    total_bits = 0

    for _ in range(trials):
        state = [random.randint(0, 0xF) for _ in range(n)]
        for i in range(n):          # each nibble
            for bit in range(4):    # each bit in nibble
                s2 = state.copy()
                s2[i] ^= (1 << bit)  # flip 1 bit
                out1 = mds_func(state)
                out2 = mds_func(s2)
                diff = sum(1 for a, b in zip(out1, out2) if a != b)
                total_flipped += diff
                total_bits += 1

    avg_diffusion = total_flipped / total_bits
    return avg_diffusion


avg = average_diffusion(mds8, trials=100)
print(f"Average diffusion: {avg:.2f} output nibbles changed per input bit flip")


# ## Encryption and decryption functions

# In[213]:


def encrypt_toy_debug(plaintext, key, R=1):
    """
    Toy Saturnin encryption with 8-nibble state and 8-nibble key.
    Follows the control-flow of official C implementation.
    """

    print("========== TOY SATURNIN DEBUG ==========")
    print(f"Plaintext: {plaintext}")
    print(f"Key:       {key}")
    print("----------------------------------------")

    state = plaintext.copy()

    # ---------- 1. Round constants ----------
    rc0, rc1 = make_round_constants(R)
    print("Round constants RC0:", rc0)
    print("Round constants RC1:", rc1)
    print("----------------------------------------")

    # ---------- 2. Initial key XOR ----------
    state = xor_key(key, state)
    print("After initial key XOR:", state)

    # ---------- 3. R rounds (like C) ----------
    for r in range(R):

        print(f"\n====== ROUND {r} ======")

        # ---------------- EVEN ROUND ----------------
        print("Before S-box (even):", state)
        state = sbox_kriti(state)
        print("After S-box  (even):", state)

        # print("(Skipping MDS Even)")
        print("Before mds even:", state)
        state = mds(state)
        print("After mds even:", state)

        # ---------------- ODD ROUND -----------------
        print("Before S-box (odd):", state)
        state = sbox_kriti(state)
        print("After S-box  (odd):", state)

        # ---------------- ROUND TYPE ----------------
        if (r & 1) == 0:
            # r ≡ 0 mod 2 → matches C's "r = 1 mod 4" behavior
            print("Slice-Type Round")

            print("Before SR_slice:", state)
            state = SR_slice(state)
            print("After SR_slice:", state)

            # print("(Skipping MDS Odd)")
            print("Before mds odd:", state)
            state = mds(state)
            print("After mds odd:", state)

            print("Before inv_SR_slice:", state)
            state = inv_SR_slice(state)
            print("After inv_SR_slice:", state)

            # --------- Add Round Constants ---------
            print("Before RC XOR:", state)
            state[0] ^= rc0[r] & 0xF
            state[4] ^= rc1[r] & 0xF
            print("After RC XOR:", state)

            # --------- XOR ROTATED KEY -------------
            print("Before XOR rotated key:", state)
            state = xor_key_rotated(key, state)
            print("After XOR rotated key:", state)

        else:
            # r ≡ 1 mod 2 → matches C "r = 3 mod 4"
            print("Sheet-Type Round")

            print("Before SR_sheet:", state)
            state = SR_sheet(state)
            print("After SR_sheet:", state)

            # print("(Skipping MDS Odd)")
            print("Before mds odd:", state)
            state = mds(state)
            print("After mds odd:", state)

            print("Before inv_SR_sheet:", state)
            state = inv_SR_sheet(state)
            print("After inv_SR_sheet:", state)

            # --------- Add Round Constants ---------
            print("Before RC XOR:", state)
            state[0] ^= rc0[r] & 0xF
            state[4] ^= rc1[r] & 0xF
            print("After RC XOR:", state)

            # --------- XOR NORMAL KEY --------------
            print("Before XOR key:", state)
            state = xor_key(key, state)
            print("After XOR key:", state)

    print("\n========== FINAL CIPHERTEXT ==========")
    print(state)
    print("======================================\n")

    return state


# In[214]:


def decrypt_toy_debug(plaintext, key, R=1):
    """
    Toy Saturnin decryption with full debug output.
    Tracks every internal step, round, XOR, S-box, and permutation.
    """

    print("\n========== TOY SATURNIN DEBUG ==========")
    print(f"Plaintext (input to decrypt): {plaintext}")
    print(f"Key:                         {key}")
    print(f"Rounds:                      {R}")
    print("========================================\n")

    state = plaintext.copy()

    # ---------- 1. Round constants ----------
    rc0, rc1 = make_round_constants(R)
    print("[*] Round constants generated")
    print("    RC0 =", rc0)
    print("    RC1 =", rc1)
    print("----------------------------------------\n")

    # ---------- 3. Rounds ----------
    for i in range(R-1, -1, -1):
        print(f"\n============ ROUND {i} START ============\n")

        # ---------- ODD ROUND ----------
        if (i & 1) == 0:
            print(f"[Odd Round] (i={i}) — slice mode")

            print("  XOR with rotated key:")
            print("    Before:", state)
            state = xor_key_rotated(key, state)
            print("    After :", state)

            print("  Add round constants:")
            print(f"    state[0] ^= RC0[{i}] ({rc0[i]})")
            print(f"    state[8] ^= RC1[{i}] ({rc1[i]})")
            state[0] ^= rc0[i]
            state[4] ^= rc1[i]
            print("    After:", state)

            print("  SR_slice →")
            before_sr = state.copy()
            state = SR_slice(state)
            print("    Before:", before_sr)
            print("    After :", state)

            print("before mds inverse odd", state)
            state = inv_mds(state)
            print("after mds inverse odd", state)

            print("  SR_slice_inv →")
            before_inv = state.copy()
            state = inv_SR_slice(state)
            print("    Before:", before_inv)
            print("    After :", state)

        # ---------- SHEET ROUND ----------
        else:
            print(f"[Odd Round] (i={i}) — sheet mode")

            print("  XOR with key:")
            print("    Before:", state)
            state = xor_key(key, state)
            print("    After :", state)

            print("  Add round constants:")
            print(f"    state[0] ^= RC0[{i}] ({rc0[i]})")
            print(f"    state[8] ^= RC1[{i}] ({rc1[i]})")
            state[0] ^= rc0[i]
            state[4] ^= rc1[i]
            print("    After :", state)

            print("  SR_sheet →")
            before_sr = state.copy()
            state = SR_sheet(state)
            print("    Before:", before_sr)
            print("    After :", state)

            print("before mds inverse odd", state)
            state = inv_mds(state)  
            print("after mds inverse odd", state)

            print("  SR_sheet_inv →")
            before_inv = state.copy()
            state = inv_SR_sheet(state)
            print("    Before:", before_inv)
            print("    After :", state)

        # always apply inverse S-box
        print("\n  Apply inverse S-box (odd-round post step):")
        before_sbox = state.copy()
        state = sbox_inv_kriti(state)
        print("    Before:", before_sbox)
        print("    After :", state)

        # ---------- EVEN ROUND ----------
        print("before mds inverse even", state)
        state = inv_mds(state)
        print("after mds inverse even", state)
        
        print("\n  [Even Round Step] Apply inverse S-box again:")
        before_even = state.copy()
        state = sbox_inv_kriti(state)
        print("    Before:", before_even)
        print("    After :", state)

        print(f"\n============ ROUND {i} END ============\n")

    # ---------- Final key XOR ----------
    print("[*] Final key XOR")
    print("    Before:", state)
    state = xor_key(key,state)
    print("    After :", state)
    print("========================================")
    print("========== DECRYPTION COMPLETE =========\n")

    return state


# In[217]:


r = 10


# In[218]:


plaintext = [1,0,0,0,0,0,0,0]
key       = [0,0,0,0,0,0,0,0]

ciphertext = encrypt_toy_debug(plaintext.copy(), key.copy(), R=r)
print(plaintext)
print(key)

decrypted_ct = decrypt_toy_debug(ciphertext.copy(), key.copy(), R=r)
print("Decrypted ciphertext:", decrypted_ct)
print(ciphertext)
print(plaintext)
print(key)
print("sahi aya kya : ", plaintext == decrypted_ct)


# ## making test vectors
# Test vectors are present in the file test_vectors.txt
# 
# Uncomment this code to make more TVs

# In[1]:


# import random

# def generate_random_state():
#     """Generate a list of 8 random nibbles (0..15)."""
#     return [random.randint(0, 15) for _ in range(8)]

# def make_test_vectors(num_vectors=10, R=1):
#     vectors = []

#     for i in range(num_vectors):
#         print("\n==============================")
#         print(f"      TEST VECTOR {i+1}")
#         print("==============================")

#         P = generate_random_state()
#         K = generate_random_state()

#         print("Plaintext :", P)
#         print("Key       :", K)

#         print("\n---- Encryption ----")
#         C = encrypt_toy_debug(P.copy(), K.copy(), R=R)

#         print("\n---- Decryption ----")
#         D = decrypt_toy_debug(C.copy(), K.copy(), R=R)

#         ok = (D == P)
#         print("\nRecovered :", D)
#         print("Correct   :", ok)

#         vectors.append({
#             "plaintext": P,
#             "key": K,
#             "ciphertext": C,
#             "correct": ok
#         })

#     return vectors


# # Run the generator
# vectors = make_test_vectors(num_vectors=10, R=10)

# print("\n\n========== FINAL SUMMARY ==========")
# for i, v in enumerate(vectors):
#     print(f"\nVector {i+1}")
#     print("P =", v["plaintext"])
#     print("K =", v["key"])
#     print("C =", v["ciphertext"])
#     print("Correct =", v["correct"])


# # miscellenious

# ### Another nice mds matrix with full 9 nibble diffusion

# In[139]:


# Corrected GF(2^4) inversion and full test for the 8x8 MDS matrix.
PRIMITIVE_POLY = 0b10011  # x^4 + x + 1

def gf4_mul(a, b):
    res = 0
    for _ in range(4):
        if b & 1:
            res ^= a
        carry = a & 0x8
        a <<= 1
        if carry:
            a ^= PRIMITIVE_POLY
        a &= 0xF
        b >>= 1
    return res

def gf4_add(a, b):
    return a ^ b

def gf4_pow(a, e):
    # exponentiation by squaring in GF(2^4)
    if a == 0:
        return 0 if e > 0 else 1
    res = 1
    base = a
    while e > 0:
        if e & 1:
            res = gf4_mul(res, base)
        base = gf4_mul(base, base)
        e >>= 1
    return res

def gf4_inv(a):
    if a == 0:
        raise ValueError("zero has no inverse")
    # a^(2^4 - 2) = a^14
    return gf4_pow(a, 14)

# The 8x8 M matrix from the conversation (simpler Option A)
M = [
    [0x1,0x1,0x1,0x1,0x1,0x1,0x1,0x1],
    [0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8],
    [0x1,0x3,0x5,0x7,0x9,0xB,0xD,0xF],
    [0x1,0x4,0x7,0xA,0xD,0x0,0x3,0x6],
    [0x1,0x5,0x9,0xD,0x1,0x5,0x9,0xD],
    [0x1,0x6,0xB,0x0,0x5,0xA,0xF,0x4],
    [0x1,0x7,0xD,0x3,0x9,0xF,0x5,0xB],
    [0x1,0x8,0xF,0x6,0xD,0x4,0xB,0x2]
]

def mat_vec_mul(Mtx, v):
    out = [0]*8
    for i in range(8):
        s = 0
        for j in range(8):
            s ^= gf4_mul(Mtx[i][j], v[j])
        out[i] = s
    return out

def mat_mul(A, B):
    # multiply 8x8 matrices over GF(2^4)
    n = 8
    C = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = 0
            for k in range(n):
                s ^= gf4_mul(A[i][k], B[k][j])
            C[i][j] = s
    return C

def mat_inverse(A):
    n = 8
    # make a copy and augment with identity
    M = [row[:] + [1 if i==j else 0 for j in range(n)] for i,row in enumerate(A)]
    for col in range(n):
        # find pivot row with nonzero at col
        pivot = col
        if M[pivot][col] == 0:
            for r in range(col+1, n):
                if M[r][col] != 0:
                    pivot = r
                    break
            if M[pivot][col] == 0:
                raise ValueError("Matrix is singular (no pivot)")
            M[col], M[pivot] = M[pivot], M[col]
        # normalize pivot row
        inv_piv = gf4_inv(M[col][col])
        M[col] = [gf4_mul(x, inv_piv) for x in M[col]]
        # eliminate other rows
        for r in range(n):
            if r == col:
                continue
            factor = M[r][col]
            if factor != 0:
                M[r] = [gf4_add(M[r][c], gf4_mul(factor, M[col][c])) for c in range(2*n)]
    # extract inverse
    inv = [row[n:] for row in M]
    return inv

# compute inverse matrix
INV_M = mat_inverse(M)

# test identity M * INV_M
I_test = mat_mul(M, INV_M)

# print I_test to verify identity
print("M * INV_M (should be identity 8x8):")
for row in I_test:
    print([hex(x) for x in row])

# test the given state
state = [1,0,0,0,0,0,0,0]
enc = mat_vec_mul(M, state)
dec = mat_vec_mul(INV_M, enc)
print("\nState:    ", state)
print("After MDS:", enc)
print("After inverse:", dec)
print("Correctly inverted?", dec == state)


# ###  using mini aes matrix

# In[153]:


PRIM = 0x13

def gf_add(a, b):
    return a ^ b

def gf_mul(a, b):
    res = 0
    while b:
        if b & 1:
            res ^= a
        a <<= 1
        if a & 0x10:
            a ^= PRIM
        a &= 0xF
        b >>= 1
    return res

def gf_pow(a, e):
    r = 1
    for _ in range(e):
        r = gf_mul(r, a)
    return r

def gf_inv(a):
    if a == 0:
        raise ZeroDivisionError("inv(0)")
    return gf_pow(a, 14)

# -----------------------------
# Invertible 4x4 MDS
# -----------------------------
M4 = [
    [1, 4, 9, 13],
    [13, 1, 4, 9],
    [9, 13, 1, 4],
    [4, 9, 13, 1]
]

def make_M8():
    M8 = []
    for i in range(4):
        M8.append(M4[i] + [0,0,0,0])
    for i in range(4):
        M8.append([0,0,0,0] + M4[i])
    return M8

def mat_inv_4x4(M):
    n = 4
    A = [[M[r][c] for c in range(n)] + [1 if r==c else 0 for c in range(n)] for r in range(n)]
    for col in range(n):
        pivot = None
        for r in range(col, n):
            if A[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            raise ValueError("Matrix not invertible")
        if pivot != col:
            A[col], A[pivot] = A[pivot], A[col]
        inv_p = gf_inv(A[col][col])
        A[col] = [gf_mul(x, inv_p) for x in A[col]]
        for r in range(n):
            if r != col:
                factor = A[r][col]
                if factor != 0:
                    A[r] = [gf_add(A[r][c], gf_mul(factor, A[col][c])) for c in range(2*n)]
    Inv = [[A[r][c] for c in range(n,2*n)] for r in range(n)]
    return Inv

def mds(state):
    M8 = make_M8()
    out = []
    for row in M8:
        s = 0
        for a,b in zip(row, state):
            s ^= gf_mul(a,b)
        out.append(s)
    return out

def inv_mds(state):
    M4inv = mat_inv_4x4(M4)
    blk1 = state[:4]
    blk2 = state[4:]
    out1 = []
    out2 = []
    for row in M4inv:
        s = 0
        for a,b in zip(row, blk1):
            s ^= gf_mul(a,b)
        out1.append(s)
    for row in M4inv:
        s = 0
        for a,b in zip(row, blk2):
            s ^= gf_mul(a,b)
        out2.append(s)
    return out1 + out2

# -----------------------------
# Test
# -----------------------------
state = [1,0,0,0,0,0,0,0]
out = mds(state)
recovered = inv_mds(out)
print("Original:", state)
print("After MDS:", out)
print("Recovered:", recovered)  # should match original now


# ## checking full diffusion bounds: got 72

# In[185]:


def to_bitslices(state):
    """
    state: list of 8 nibbles [s0..s7]
    returns: x[0..7], each 4-bit integer
    """

    x = [0]*8

    # slice 0: s0—s3
    for bit in range(4):  # 0..3
        val = 0
        for i in range(4):  # s0..s3
            val |= ((state[i] >> bit) & 1) << i
        x[bit] = val

    # slice 1: s4—s7
    for bit in range(4):  # 0..3
        val = 0
        for i in range(4):  # s4..s7
            val |= ((state[4+i] >> bit) & 1) << i
        x[4+bit] = val

    return x


def nibble_diffusion(plaintext, key, rounds):
    """
    Flip one whole nibble (not one bit) and see which x-registers get activated.
    """
    results = []

    for nib in range(8):
        # Flip 1 nibble
        P2 = plaintext.copy()
        P2[nib] ^= 0xF   # activate nibble by xoring 1111

        C1 = encrypt_toy_debug(plaintext, key, R=rounds)
        C2 = encrypt_toy_debug(P2,        key, R=rounds)

        x1 = to_bitslices(C1)
        x2 = to_bitslices(C2)

        # a bitsliced nibble is "activated" if any of its 4 bits differ
        activated = [(x1[i] ^ x2[i]) != 0 for i in range(8)]

        results.append(sum(activated))

    avg = sum(results) / 8
    return avg, results


def find_full_nibble_diffusion(P, key, max_rounds=80):
    for R in range(1, max_rounds+1):
        avg, res = nibble_diffusion(P, key, R)
        print(f"Round {R}: avg={avg:.2f}, min={min(res)}")

        if min(res) == 8:
            print(f"\n>>> FULL nibble → bitslice diffusion at round {R}! <<<\n")
            return R

    print("No full diffusion found up to max_rounds.")
    return None

P = [0,0,0,0,0,0,0,0]
K = [1,2,3,4,5,6,7,8]

find_full_nibble_diffusion(P, K)



# In[ ]:




