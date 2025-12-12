import sys
import os
import random

# Add parent directory to path to import toy
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

# ---------------------------------------------------------
# Step 1: Find Input Diff for Round 1
# Target Output Diff: [1, 0, 0, 0, 0, 0, 0, 0]
# ---------------------------------------------------------
def search_differential_prepend():
    target_diff = [1, 0, 0, 0, 0, 0, 0, 0]
    key = [0] * 8
    
    print("Searching for Input Diff -> [1, 0, ...] using Decryption")
    
    # We want: Enc(P1) ^ Enc(P2) = target_diff
    # Let's pick a random C1, set C2 = C1 ^ target_diff
    # Then P1 = Dec(C1), P2 = Dec(C2)
    # The input diff is P1 ^ P2
    # We check if this input diff is "stable" (high probability)
    
    # Collect candidate input diffs
    counts = {}
    trials = 1000
    
    for _ in range(trials):
        c1 = get_random_state()
        c2 = apply_diff(c1, target_diff)
        
        p1 = toy.decrypt_toy_debug(c1, key, R=1)
        p2 = toy.decrypt_toy_debug(c2, key, R=1)
        
        diff_in = tuple([x ^ y for x, y in zip(p1, p2)])
        
        if diff_in in counts:
            counts[diff_in] += 1
        else:
            counts[diff_in] = 1
            
    # Find most frequent input diff
    best_diff = None
    best_count = 0
    
    for d, c in counts.items():
        if c > best_count:
            best_count = c
            best_diff = list(d)
            
    prob = best_count / trials
    print(f"  Best Input Diff: {best_diff} with prob {prob:.3f}")
    
    return best_diff, prob

# ---------------------------------------------------------
# Step 2: Find Output Mask for Round 3
# Target Input Mask: [4, 0, 0, 0, 0, 0, 0, 0]
# ---------------------------------------------------------
def search_linear_append():
    target_mask_in = [4, 0, 0, 0, 0, 0, 0, 0]
    key = [0] * 8
    
    print("\nSearching for Target Mask [4, 0, ...] -> Output Mask")
    
    # Try single bit masks
    candidates = []
    for i in range(8):
        for b in range(4):
            m = [0]*8
            m[i] = (1 << b)
            candidates.append(m)
            
    best_bias = 0
    best_mask = None
    
    for mask_out in candidates:
        # Check correlation: Mask_in * P == Mask_out * C
        count = 0
        trials = 1000
        for _ in range(trials):
            p = get_random_state()
            c = toy.encrypt_toy_debug(p, key, R=1)
            
            m_in = apply_mask(p, target_mask_in)
            m_out = apply_mask(c, mask_out)
            
            if m_in == m_out:
                count += 1
                
        prob = count / trials
        bias = 2 * (prob - 0.5)
        
        if abs(bias) > abs(best_bias):
            best_bias = bias
            best_mask = mask_out
            print(f"  Found Target -> Mask {mask_out} with bias {bias:.3f}")
            
    return best_mask, best_bias

if __name__ == "__main__":
    d, p = search_differential_prepend()
    m, b = search_linear_append()
    
    print("\n" + "="*40)
    print(f"Best Prepend Diff: {d} (Prob: {p})")
    print(f"Best Append Mask:  {m} (Bias: {b})")
    print("="*40)
    
    if d and m:
        print("\nSuggested 3-Round Parameters:")
        print(f"Input Diff: {d}")
        print(f"Output Mask: {m}")
