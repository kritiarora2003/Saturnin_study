import numpy as np

# Saturnin 4-bit S-box
SATURNIN_SBOX = [0x6, 0x9, 0x0, 0xE, 0x1, 0x5, 0x4, 0x7, 0xB, 0xD, 0x8, 0xF, 0x3, 0x2, 0xC, 0xA]

def compute_ddt(sbox):
    """
    Compute Difference Distribution Table (DDT)
    DDT[dx][dy] = number of input pairs (x1, x2) such that:
    S(x1) ⊕ S(x2) = dy when x1 ⊕ x2 = dx
    """
    n = len(sbox)
    ddt = np.zeros((n, n), dtype=int)
    
    for x1 in range(n):
        for x2 in range(n):
            dx = x1 ^ x2
            dy = sbox[x1] ^ sbox[x2]
            ddt[dx][dy] += 1
    
    return ddt

def print_ddt(ddt):
    """Pretty print DDT table"""
    print("\nDifference Distribution Table (DDT) for Saturnin S-box")
    print("=" * 80)
    print("DDT[dx][dy] = count where S(x) ⊕ S(x ⊕ dx) = dy")
    print("=" * 80)
    n = len(ddt)
    
    # Print header
    print("dx\\dy", end="")
    for i in range(n):
        print(f"{i:4x}", end="")
    print()
    print("     " + "-" * (n * 4))
    
    # Print rows
    for i in range(n):
        print(f"{i:4x} |", end="")
        for j in range(n):
            print(f"{ddt[i][j]:4}", end="")
        print()

def analyze_ddt(ddt):
    """Analyze DDT properties"""
    n = len(ddt)
    print("\n" + "=" * 80)
    print("DDT ANALYSIS")
    print("=" * 80)
    
    # Max differential probability (excluding dx=0)
    max_val = np.max(ddt[1:, :])
    print(f"Maximum DDT value (excluding dx=0): {max_val}")
    print(f"Differential uniformity: {max_val}")
    print(f"Maximum differential probability: {max_val}/{n} = {max_val/n:.4f}")
    
    # Find all maximum entries
    print(f"\nEntries with maximum value {max_val}:")
    for dx in range(1, n):
        for dy in range(n):
            if ddt[dx][dy] == max_val:
                print(f"  DDT[0x{dx:x}][0x{dy:x}] = {max_val}")
    
    # Distribution of values
    print("\nValue distribution in DDT (excluding dx=0):")
    unique, counts = np.unique(ddt[1:, :], return_counts=True)
    for val, count in zip(unique, counts):
        print(f"  Value {val}: appears {count} times")
    
    # Check if dx=0 row is correct (should all be 16 for the diagonal)
    print(f"\nDDT[0][0] (trivial case): {ddt[0][0]}")

def query_ddt(ddt):
    """Interactive query for DDT"""
    print("\n" + "=" * 80)
    print("INTERACTIVE DDT QUERY")
    print("=" * 80)
    print("Enter 'q' to quit, or input/output difference in hex")
    
    while True:
        try:
            inp = input("\nInput difference (dx): ").strip().lower()
            if inp == 'q':
                break
            dx = int(inp, 16) if inp.startswith('0x') else int(inp, 16)
            
            out = input("Output difference (dy): ").strip().lower()
            if out == 'q':
                break
            dy = int(out, 16) if out.startswith('0x') else int(out, 16)
            
            if 0 <= dx < len(ddt) and 0 <= dy < len(ddt[0]):
                count = ddt[dx][dy]
                prob = count / len(ddt)
                print(f"DDT[0x{dx:x}][0x{dy:x}] = {count}")
                print(f"Probability: {count}/{len(ddt)} = {prob:.4f} = 2^{np.log2(prob):.2f}")
                
                # Show which x values satisfy this
                if count > 0 and count <= 8:
                    sbox = SATURNIN_SBOX
                    solutions = []
                    for x in range(len(sbox)):
                        if (sbox[x] ^ sbox[x ^ dx]) == dy:
                            solutions.append(x)
                    print(f"Solutions (x values): {[hex(s) for s in solutions]}")
            else:
                print("Invalid indices!")
        except (ValueError, IndexError):
            print("Invalid input! Please enter hex values (0-f).")

def main():
    print("Saturnin S-box DDT Calculator")
    print("=" * 80)
    print(f"S-box: {[hex(x) for x in SATURNIN_SBOX]}")
    
    # Compute DDT
    print("\nComputing DDT...")
    ddt = compute_ddt(SATURNIN_SBOX)
    
    # Print DDT
    print_ddt(ddt)
    
    # Analyze DDT
    analyze_ddt(ddt)
    
    # Interactive query
    query_ddt(ddt)

if __name__ == "__main__":
    main()