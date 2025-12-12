import sys
import os
import random
import numpy as np

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

def run_one_trial(diff_in, mask_out, trials=5000):
    """Estimate bias for a given diff/mask pair."""
    key = [random.randint(0, 15) for _ in range(8)]
    count_equal = 0

    for _ in range(trials):
        p1 = get_random_state()
        p2 = apply_diff(p1, diff_in)
        c1 = toy.encrypt_toy_debug(p1, key, R=1)
        c2 = toy.encrypt_toy_debug(p2, key, R=1)
        m1 = apply_mask(c1, mask_out)
        m2 = apply_mask(c2, mask_out)
        if m1 == m2:
            count_equal += 1

    prob = count_equal / trials
    bias = 2 * (prob - 0.5)
    return bias, prob

def estimate_data_complexity(bias):
    """Estimate number of pairs needed to detect given bias."""
    if bias == 0:
        return float('inf')
    return round(1 / (bias ** 2))

def run_generic_distinguisher(num_tests=10, trials=5000):
    """Try random Δin and mask_out pairs and estimate their biases."""
    print(f"Testing {num_tests} random trails with {trials} samples each...")
    results = []

    for _ in range(num_tests):
        diff_in = [0]*8
        mask_out = [0]*8

        # Random non-zero input diff and mask on same nibble (for simplicity)
        pos = random.randint(0, 7)
        diff_in[pos] = random.randint(1, 15)
        mask_out[pos] = random.randint(1, 15)

        bias, prob = run_one_trial(diff_in, mask_out, trials=trials)
        N = estimate_data_complexity(bias)
        results.append((diff_in, mask_out, bias, prob, N))

        print(f"\nΔin={diff_in}, mask={mask_out}")
        print(f"  → Prob={prob:.4f}, Bias={bias:.4f}, DataComplexity≈{N}")

    # Sort by strongest bias
    results.sort(key=lambda x: abs(x[2]), reverse=True)
    print("\nTop Biases Found:")
    for r in results[:3]:
        print(f"Δ={r[0]}, Γ={r[1]}, bias={r[2]:.4f}, data≈{r[4]}")
    return results

if __name__ == "__main__":
    results = run_generic_distinguisher(num_tests=20, trials=5000)
