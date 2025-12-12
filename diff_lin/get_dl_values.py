import sys
import os
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from toy import toy

def get_random_state():
    return [random.randint(0, 15) for _ in range(8)]

def apply_diff(state, diff):
    return [s ^ d for s, d in zip(state, diff)]

def apply_mask(state, mask):
    res = 0
    for s, m in zip(state, mask):
        val = s & m
        while val:
            res ^= (val & 1)
            val >>= 1
    return res

def run_one_trial_debug(diff_in, mask_out):
    key = [random.randint(0, 15) for _ in range(8)]
    p1 = get_random_state()
    p2 = apply_diff(p1, diff_in)
    c1 = toy.encrypt_toy_debug(p1, key, R=1)
    c2 = toy.encrypt_toy_debug(p2, key, R=1)
    m1 = apply_mask(c1, mask_out)
    m2 = apply_mask(c2, mask_out)
    
    print(f"p1 = {p1}")
    print(f"p2 = {p2}")
    print(f"c1 = {c1}")
    print(f"c2 = {c2}")
    print(f"diff_in = {diff_in}")
    print(f"mask_out = {mask_out}")
    print(f"m1 = {m1}")
    print(f"m2 = {m2}")
    print(f"correlation = {1 if m1 == m2 else -1}")

# Best characteristic from previous run
# Δ=[0, 0, 8, 0, 0, 0, 0, 0], Γ=[0, 0, 11, 0, 0, 0, 0, 0]
diff_in = [0, 0, 8, 0, 0, 0, 0, 0]
mask_out = [0, 0, 11, 0, 0, 0, 0, 0]

run_one_trial_debug(diff_in, mask_out)
