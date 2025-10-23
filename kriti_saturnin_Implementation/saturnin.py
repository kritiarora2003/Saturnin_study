# saturnin_full.py
from typing import List

# ------------------- Utilities -------------------

def to_words(b: bytes) -> List[int]:
    return [b[i*2] | (b[i*2+1] << 8) for i in range(16)]

def from_words(words: List[int]) -> bytes:
    out = bytearray()
    for w in words:
        out.append(w & 0xFF)
        out.append((w >> 8) & 0xFF)
    return bytes(out)

def print_state(state: List[int], label: str, round_num: int, phase: str):
    print(f"\n{label} - Round {round_num:02d} [{phase}]")
    for i in range(16):
        w = state[i]
        bin_str = f"{w:016b}"
        nib_str = " ".join([bin_str[j:j+4] for j in range(0,16,4)])
        print(f"Word {i:2d}: {w:04x} | {nib_str}")
    print("-"*60)

# ------------------- Round Constants -------------------

def make_round_constants(R:int,D:int):
    RC0,RC1 = [0]*R,[0]*R
    x0 = x1 = D + (R << 4) + 0xFE00
    for n in range(R):
        for i in range(16):
            x0 = ((x0 << 1) ^ (0x2D if x0 & 0x8000 else 0)) & 0xFFFF
            x1 = ((x1 << 1) ^ (0x53 if x1 & 0x8000 else 0)) & 0xFFFF
        RC0[n]=x0; RC1[n]=x1
    return RC0,RC1

# ------------------- S-box -------------------

def S_box(state: List[int]):
    for i in range(0,16,8):
        a,b,c,d = state[i:i+4]
        a ^= b & c; b ^= a | d; d ^= b | c; c ^= b & d; b ^= a | c; a ^= b | d
        state[i:i+4] = [b,c,d,a]
        a,b,c,d = state[i+4:i+8]
        a ^= b & c; b ^= a | d; d ^= b | c; c ^= b & d; b ^= a | c; a ^= b | d
        state[i+4:i+8] = [d,b,a,c]

def S_box_inv(state: List[int]):
    for i in range(0,16,8):
        b,c,d,a = state[i:i+4]
        a ^= b | d; b ^= a | c; c ^= b & d; d ^= b | c; b ^= a | d; a ^= b & c
        state[i:i+4] = [a,b,c,d]
        d,b,a,c = state[i+4:i+8]
        a ^= b | d; b ^= a | c; c ^= b & d; d ^= b | c; b ^= a | d; a ^= b & c
        state[i+4:i+8] = [a,b,c,d]

# ------------------- MDS -------------------

def MDS(state: List[int]):
    x = state.copy()
    def MUL(t0,t1,t2,t3):
        return t1,t2,t3,t0^t1
    x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,xa,xb,xc,xd,xe,xf = x
    x8 ^= xc; x9 ^= xd; xa ^= xe; xb ^= xf
    x0 ^= x4; x1 ^= x5; x2 ^= x6; x3 ^= x7
    x4,x5,x6,x7 = MUL(x4,x5,x6,x7)
    xc,xd,xe,xf = MUL(xc,xd,xe,xf)
    x4 ^= x8; x5 ^= x9; x6 ^= xa; x7 ^= xb
    xc ^= x0; xd ^= x1; xe ^= x2; xf ^= x3
    x0,x1,x2,x3 = MUL(x0,x1,x2,x3)
    x0,x1,x2,x3 = MUL(x0,x1,x2,x3)
    x8,x9,xa,xb = MUL(x8,x9,xa,xb)
    x8,x9,xa,xb = MUL(x8,x9,xa,xb)
    x8 ^= xc; x9 ^= xd; xa ^= xe; xb ^= xf
    x0 ^= x4; x1 ^= x5; x2 ^= x6; x3 ^= x7
    x4 ^= x8; x5 ^= x9; x6 ^= xa; x7 ^= xb
    xc ^= x0; xd ^= x1; xe ^= x2; xf ^= x3
    state[:] = [x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,xa,xb,xc,xd,xe,xf]

def MDS_inv(state: List[int]):
    x = state.copy()
    def MULinv(t0,t1,t2,t3):
        return t3,t0^t1,t1,t2
    x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,xa,xb,xc,xd,xe,xf = x
    x4 ^= x8; x5 ^= x9; x6 ^= xa; x7 ^= xb
    xc ^= x0; xd ^= x1; xe ^= x2; xf ^= x3
    x8 ^= xc; x9 ^= xd; xa ^= xe; xb ^= xf
    x0 ^= x4; x1 ^= x5; x2 ^= x6; x3 ^= x7
    x0,x1,x2,x3 = MULinv(x0,x1,x2,x3)
    x0,x1,x2,x3 = MULinv(x0,x1,x2,x3)
    x8,x9,xa,xb = MULinv(x8,x9,xa,xb)
    x8,x9,xa,xb = MULinv(x8,x9,xa,xb)
    x4 ^= x8; x5 ^= x9; x6 ^= xa; x7 ^= xb
    xc ^= x0; xd ^= x1; xe ^= x2; xf ^= x3
    x4,x5,x6,x7 = MULinv(x4,x5,x6,x7)
    xc,xd,xe,xf = MULinv(xc,xd,xe,xf)
    x8 ^= xc; x9 ^= xd; xa ^= xe; xb ^= xf
    x0 ^= x4; x1 ^= x5; x2 ^= x6; x3 ^= x7
    state[:] = [x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,xa,xb,xc,xd,xe,xf]

# ------------------- SR permutations -------------------

def SR_slice(state: List[int]):
    for i in range(4):
        state[4+i] = ((state[4+i] & 0x7777)<<1) | ((state[4+i]&0x8888)>>3)
        state[8+i] = ((state[8+i] & 0x3333)<<2) | ((state[8+i]&0xCCCC)>>2)
        state[12+i] = ((state[12+i]&0x1111)<<3) | ((state[12+i]&0xEEEE)>>1)

def SR_slice_inv(state: List[int]):
    for i in range(4):
        state[4+i] = ((state[4+i]&0x1111)<<3) | ((state[4+i]&0xEEEE)>>1)
        state[8+i] = ((state[8+i]&0x3333)<<2) | ((state[8+i]&0xCCCC)>>2)
        state[12+i] = ((state[12+i]&0x7777)<<1) | ((state[12+i]&0x8888)>>3)

def SR_sheet(state: List[int]):
    for i in range(4):
        state[4+i] = ((state[4+i]<<4) | (state[4+i]>>12)) & 0xFFFF
        state[8+i] = ((state[8+i]<<8) | (state[8+i]>>8)) & 0xFFFF
        state[12+i] = ((state[12+i]<<12) | (state[12+i]>>4)) & 0xFFFF

def SR_sheet_inv(state: List[int]):
    for i in range(4):
        state[4+i]  = ((state[4+i] << 12) | (state[4+i] >> 4)) & 0xFFFF
        state[8+i]  = ((state[8+i] << 8)  | (state[8+i] >> 8)) & 0xFFFF
        state[12+i] = ((state[12+i] << 4) | (state[12+i] >> 12)) & 0xFFFF

# ------------------- Key XOR -------------------

def XOR_key(key: List[int], state: List[int]):
    for i in range(16):
        state[i] ^= key[i]

def XOR_key_rotated(key: List[int], state: List[int]):
    for i in range(16):
        state[i] ^= ((key[i]<<11) | (key[i]>>5)) & 0xFFFF

# ------------------- Block Encrypt -------------------

def saturnin_block_encrypt(R:int, D:int, key_bytes:bytes, buf:bytes) -> bytes:
    RC0, RC1 = make_round_constants(R,D)
    xk = to_words(key_bytes)
    xb = to_words(buf[:32])
    
    XOR_key(xk, xb)
    
    for i in range(R):
        # Even round
        S_box(xb)
        MDS(xb)
        print_state(xb, "Encrypt", i, "Even")
        
        # Odd round
        S_box(xb)
        if (i & 1) == 0:
            # r = 1 mod 4
            SR_slice(xb)
            MDS(xb)
            SR_slice_inv(xb)
            xb[0] ^= RC0[i]; xb[8] ^= RC1[i]
            XOR_key_rotated(xk, xb)
            print_state(xb, "Encrypt", i, "Odd Slice")
        else:
            # r = 3 mod 4
            SR_sheet(xb)
            MDS(xb)
            SR_sheet_inv(xb)
            xb[0] ^= RC0[i]; xb[8] ^= RC1[i]
            XOR_key(xk, xb)
            print_state(xb, "Encrypt", i, "Odd Sheet")
    
    return from_words(xb)

# ------------------- Block Decrypt -------------------

def saturnin_block_decrypt(R:int, D:int, key_bytes:bytes, buf:bytes) -> bytes:
    RC0, RC1 = make_round_constants(R,D)
    xk = to_words(key_bytes)
    xb = to_words(buf[:32])
    
    for i in reversed(range(R)):
        # Odd round
        if (i & 1) == 0:
            XOR_key_rotated(xk, xb)
            xb[0] ^= RC0[i]; xb[8] ^= RC1[i]
            SR_slice(xb)
            MDS_inv(xb)
            SR_slice_inv(xb)
            print_state(xb, "Decrypt", i, "Odd Slice")
        else:
            XOR_key(xk, xb)
            xb[0] ^= RC0[i]; xb[8] ^= RC1[i]
            SR_sheet(xb)
            MDS_inv(xb)
            SR_sheet_inv(xb)
            print_state(xb, "Decrypt", i, "Odd Sheet")
        
        # Even round
        MDS_inv(xb)
        S_box_inv(xb)
        print_state(xb, "Decrypt", i, "Even")
    
    XOR_key(xk, xb)
    return from_words(xb)

import matplotlib.pyplot as plt
import numpy as np

def plot_state_3d(state, title="Saturnin State 4x4x4"):
    """
    Visualize 16-word Saturnin state as a 4x4x4 cube.
    X,Y = position in slice, Z = slice index.
    Color intensity = word value normalized.
    """
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title(title, fontsize=14)

    # normalize word values to [0,1] for color
    vals = np.array(state).reshape((4,4,4))
    colors = vals / np.max(vals)

    for z in range(4):
        for y in range(4):
            for x in range(4):
                val = colors[z,y,x]
                ax.bar3d(x, y, z, 1, 1, 1, color=plt.cm.viridis(val), alpha=0.8)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Slice Z")
    ax.set_xlim(0,4)
    ax.set_ylim(0,4)
    ax.set_zlim(0,4)
    plt.show()


# ------------------- Example Test -------------------

if __name__ == "__main__":
    R = 10
    D = 6
    KEY = bytes.fromhex(
        "000102030405060708090A0B0C0D0E0F"
        "101112131415161718191A1B1C1D1E1F"
    )
    NONCE = bytes.fromhex("000102030405060708090A0B0C0D0E0F")
    
    # Test Vector 1
    PT1 = b""
    buf1 = NONCE + PT1 + b'\x80' + b'\x00'*(15-len(PT1))
    CT1 = saturnin_block_encrypt(R,D,KEY,buf1)
    print("--- Test Vector 1 ---")
    print("Plaintext (PT):", PT1.hex())
    print("Ciphertext (CT):", CT1.hex())
    print("Expected CT   : ef142fc810ce92839726d600fccfd7119050da25a3ec5586c7c43ca668e3c8c0\n")

    # Test Vector 2
    PT2 = bytes.fromhex("00")
    buf2 = NONCE + PT2 + b'\x80' + b'\x00'*(15-len(PT2))
    CT2 = saturnin_block_encrypt(R,D,KEY,buf2)
    print("--- Test Vector 2 ---")
    print("Plaintext (PT):", PT2.hex())
    print("Ciphertext (CT):", CT2.hex())
    print("Expected CT   : 1eff913c607db032c8f1726d51401ca13c54365dbc4074ef8148e0c2160ad656\n")

    # plot_state_3d(xb, title="After S_box (Round 0)")