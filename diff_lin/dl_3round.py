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
        # Parity of val
        while val:
            res ^= (val & 1)
            val >>= 1
    return res

def run_distinguisher(trials=2000000):
    """
    Runs a 3-round Differential-Linear Distinguisher for Toy Saturnin.
    
    Construction:
    Round 1 (Diff): [2, 1, 3, 3, 1, 3, 1, 0] -> [1, 0, 0, 0, 0, 0, 0, 0] (Prob ~0.004)
    Round 2 (DL):   [1, 0, 0, 0, 0, 0, 0, 0] -> [4, 0, 0, 0, 0, 0, 0, 0] (Bias 1.0)
    Round 3 (Lin):  [4, 0, 0, 0, 0, 0, 0, 0] -> [0, 0, 8, 0, 0, 0, 0, 0] (Bias ~0.076)
    
    Expected Total Bias approx 0.0003.
    """
    
    # 1. Setup Parameters
    diff_in = [2, 1, 3, 3, 1, 3, 1, 0]
    mask_out = [0, 0, 8, 0, 0, 0, 0, 0]
    
    # Random key
    key = [random.randint(0, 15) for _ in range(8)]
    
    print(f"Running 3-Round DL Distinguisher with {trials} trials...")
    print(f"Input Difference: {diff_in}")
    print(f"Output Mask:      {mask_out}")
    print("-" * 40)
    
    count_equal = 0
    
    for i in range(trials):
        p1 = get_random_state()
        p2 = apply_diff(p1, diff_in)
        
        # Encrypt for 3 rounds
        c1 = toy.encrypt_toy_debug(p1, key, R=3)
        c2 = toy.encrypt_toy_debug(p2, key, R=3)
        
        m1 = apply_mask(c1, mask_out)
        m2 = apply_mask(c2, mask_out)
        
        if m1 == m2:
            count_equal += 1
            
    prob = count_equal / trials
    bias = 2 * (prob - 0.5)
    
    print(f"Matches: {count_equal}/{trials}")
    print(f"Probability: {prob:.6f}")
    print(f"Bias: {bias:.6f}")
    
    if abs(bias) > 0.0002:
        print("\nResult: Bias detected consistent with theoretical expectation.")
    else:
        print("\nResult: Bias not clearly detected (requires more trials).")

if __name__ == "__main__":
    run_distinguisher()
