

def sbox_kriti(state):
    a, b ,c ,d = state[0], state[1], state[2], state[3]
    # Implement the S-box logic here
    a ^= b & c
    b ^= a | d
    d ^= b | c
    c ^= b & d
    b ^= a | c
    a ^= b | d
    state[0], state[1], state[2], state[3] = b,c,d,a
    # print("state is ", state)

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
    # print("state is ", state)

    d,b,a,c = state[4], state[5], state[6], state[7]
    a ^= b | d
    b ^= a | c
    c ^= b & d
    d ^= b | c
    b ^= a | d
    a ^= b & c
    state[4], state[5], state[6], state[7] = a,b,c,d 
    return state 


# In[2]:


state = [1,0,0,0,0,0,0,0]
print("Input state:     ", [(x) for x in state])
state_sboxed = sbox_kriti(state)
print("After S-box:     ", [(x) for x in state_sboxed])
state_sboxed_inv = sbox_inv_kriti(state_sboxed)
print("After S-box inv: ", [(x) for x in state_sboxed_inv])


# ## Making round constants (same as original implementation)

# In[3]:


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

# In[4]:


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

# In[5]:


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


# In[6]:


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


# In[7]:


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

# In[8]:


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


# In[23]:


# Random 8-nibble state
state = [1,2,3,4,5,6,7,8]

state = [0,0,0,0,0,0,0,1]
state = [0,1,0,0,0,0,0,0]
state = [0,0,0,1,0,0,0,0]
state = [1,0,0,0,0,0,0,0]
print("Original:", state)

fwd = mds(state)
print("After MDS:", fwd)

inv = inv_mds(fwd)
print("After inverse:", inv)

print("Correct:", inv == state)


# In[10]:


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


avg = average_diffusion(mds, trials=100)
print(f"Average diffusion: {avg:.2f} output nibbles changed per input bit flip")


# ## Encryption and decryption functions



# In[12]:


def encrypt_toy_debug(plaintext, key, R=1):
    """
    Toy Saturnin encryption with 8-nibble state and 8-nibble key.
    Follows the control-flow of official C implementation.
    """

    state = plaintext.copy()

    # ---------- 1. Round constants ----------
    rc0, rc1 = make_round_constants(R)

    # ---------- 2. Initial key XOR ----------
    state = xor_key(key, state)

    # ---------- 3. R rounds (like C) ----------
    for r in range(R):

        # ---------------- EVEN ROUND ----------------
        state = sbox_kriti(state)
        state = mds(state)

        # ---------------- ODD ROUND -----------------
        state = sbox_kriti(state)

        # ---------------- ROUND TYPE ----------------
        if (r & 1) == 0:
            # r ≡ 0 mod 2 → matches C's "r = 1 mod 4" behavior
            state = SR_slice(state)
            state = mds(state)
            state = inv_SR_slice(state)

            # --------- Add Round Constants ---------
            state[0] ^= rc0[r] & 0xF
            state[4] ^= rc1[r] & 0xF

            # --------- XOR ROTATED KEY -------------
            state = xor_key_rotated(key, state)

        else:
            # r ≡ 1 mod 2 → matches C "r = 3 mod 4"
            state = SR_sheet(state)
            state = mds(state)
            state = inv_SR_sheet(state)

            # --------- Add Round Constants ---------
            state[0] ^= rc0[r] & 0xF
            state[4] ^= rc1[r] & 0xF

            # --------- XOR NORMAL KEY --------------
            state = xor_key(key, state)

    return state


def decrypt_toy_debug(plaintext, key, R=1):
    """
    Toy Saturnin decryption without debug prints.
    Follows the same control-flow as the debug version.
    """

    state = plaintext.copy()

    # ---------- 1. Round constants ----------
    rc0, rc1 = make_round_constants(R)

    # ---------- 3. Rounds ----------
    for i in range(R-1, -1, -1):

        # ---------- ODD ROUND ----------
        if (i & 1) == 0:
            state = xor_key_rotated(key, state)
            state[0] ^= rc0[i]
            state[4] ^= rc1[i]
            state = SR_slice(state)
            state = inv_mds(state)
            state = inv_SR_slice(state)

        # ---------- SHEET ROUND ----------
        else:
            state = xor_key(key, state)
            state[0] ^= rc0[i]
            state[4] ^= rc1[i]
            state = SR_sheet(state)
            state = inv_mds(state)
            state = inv_SR_sheet(state)

        # always apply inverse S-box
        state = sbox_inv_kriti(state)

        # ---------- EVEN ROUND ----------
        state = inv_mds(state)
        state = sbox_inv_kriti(state)

    # ---------- Final key XOR ----------
    state = xor_key(key, state)

    return state
