import numpy as np

# Define your 4-bit S-box here (replace with actual Saturnin S-box values)
SBOX = [0x6, 0x9, 0x0, 0xE, 0x1, 0x5, 0x4, 0x7, 0xB, 0xD, 0x8, 0xF, 0x3, 0x2, 0xC, 0xA]

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

def compute_lat(sbox):
    """
    Compute Linear Approximation Table (LAT)
    LAT[a][b] = #{x : a·x = b·S(x)} - n/2
    where · denotes dot product in GF(2)
    """
    n = len(sbox)
    lat = np.zeros((n, n), dtype=int)
    
    for a in range(n):
        for b in range(n):
            count = 0
            for x in range(n):
                # Compute dot product a·x and b·S(x) in GF(2)
                input_parity = bin(a & x).count('1') % 2
                output_parity = bin(b & sbox[x]).count('1') % 2
                if input_parity == output_parity:
                    count += 1
            lat[a][b] = count - (n // 2)
    
    return lat

def compute_bct(sbox):
    """
    Compute Boomerang Connectivity Table (BCT)
    BCT[dx][dy] = #{x : S^(-1)(S(x) ⊕ dy) ⊕ S^(-1)(S(x ⊕ dx) ⊕ dy) = dx}
    """
    n = len(sbox)
    bct = np.zeros((n, n), dtype=int)
    
    # Compute inverse S-box
    sbox_inv = [0] * n
    for i in range(n):
        sbox_inv[sbox[i]] = i
    
    for dx in range(n):
        for dy in range(n):
            count = 0
            for x in range(n):
                x_prime = x ^ dx
                y = sbox[x]
                y_prime = sbox[x_prime]
                
                # Check if boomerang condition holds
                z = y ^ dy
                z_prime = y_prime ^ dy
                
                if 0 <= z < n and 0 <= z_prime < n:
                    x_back = sbox_inv[z]
                    x_prime_back = sbox_inv[z_prime]
                    
                    if (x_back ^ x_prime_back) == dx:
                        count += 1
            
            bct[dx][dy] = count
    
    return bct

def compute_bdt(sbox):
    """
    Compute Boomerang Difference Table (BDT)
    BDT[delta_in][nabla_in][nabla_out] counts solutions to:
    S(x) ⊕ S(x ⊕ delta_in) = nabla_in AND
    S(x ⊕ nabla_out) ⊕ S(x ⊕ delta_in ⊕ nabla_out) = nabla_in
    
    Returns a 3D array of shape (n, n, n)
    """
    n = len(sbox)
    bdt = np.zeros((n, n, n), dtype=int)
    
    for delta_in in range(n):
        for nabla_in in range(n):
            for nabla_out in range(n):
                count = 0
                for x in range(n):
                    # First condition: S(x) ⊕ S(x ⊕ delta_in) = nabla_in
                    if (sbox[x] ^ sbox[x ^ delta_in]) == nabla_in:
                        # Second condition: S(x ⊕ nabla_out) ⊕ S(x ⊕ delta_in ⊕ nabla_out) = nabla_in
                        if (sbox[x ^ nabla_out] ^ sbox[x ^ delta_in ^ nabla_out]) == nabla_in:
                            count += 1
                
                bdt[delta_in][nabla_in][nabla_out] = count
    
    return bdt

def print_table(table, name):
    """Pretty print a 2D table"""
    print(f"\n{name}:")
    print("=" * 80)
    n = len(table)
    
    # Print header
    print("    ", end="")
    for i in range(n):
        print(f"{i:4x}", end="")
    print()
    print("    " + "-" * (n * 4))
    
    # Print rows
    for i in range(n):
        print(f"{i:2x} |", end="")
        for j in range(n):
            print(f"{table[i][j]:4}", end="")
        print()

def print_bdt_slice(bdt, delta_in, name="BDT"):
    """Print a 2D slice of the 3D BDT table for a fixed delta_in"""
    print(f"\n{name}[delta_in=0x{delta_in:x}][nabla_in][nabla_out]:")
    print("=" * 80)
    n = bdt.shape[1]
    
    # Print header
    print("    ", end="")
    for i in range(n):
        print(f"{i:4x}", end="")
    print()
    print("    " + "-" * (n * 4))
    
    # Print rows
    for i in range(n):
        print(f"{i:2x} |", end="")
        for j in range(n):
            print(f"{bdt[delta_in][i][j]:4}", end="")
        print()

def query_table(table, name):
    """Interactive query for a 2D table"""
    print(f"\n--- Query {name} ---")
    print("Enter 'q' to quit, or input/output difference in hex (e.g., '3' or '0xa')")
    
    while True:
        try:
            inp = input(f"Input difference (dx): ").strip().lower()
            if inp == 'q':
                break
            dx = int(inp, 16) if inp.startswith('0x') else int(inp, 16)
            
            out = input(f"Output difference (dy): ").strip().lower()
            if out == 'q':
                break
            dy = int(out, 16) if out.startswith('0x') else int(out, 16)
            
            if 0 <= dx < len(table) and 0 <= dy < len(table[0]):
                print(f"{name}[0x{dx:x}][0x{dy:x}] = {table[dx][dy]}")
            else:
                print("Invalid indices!")
        except (ValueError, IndexError):
            print("Invalid input! Please enter hex values.")

def query_bdt(bdt):
    """Interactive query for the 3D BDT table"""
    print(f"\n--- Query BDT (3D Table) ---")
    print("Enter 'q' to quit, or three hex values for delta_in, nabla_in, nabla_out")
    
    while True:
        try:
            inp = input(f"delta_in: ").strip().lower()
            if inp == 'q':
                break
            delta_in = int(inp, 16) if inp.startswith('0x') else int(inp, 16)
            
            inp2 = input(f"nabla_in: ").strip().lower()
            if inp2 == 'q':
                break
            nabla_in = int(inp2, 16) if inp2.startswith('0x') else int(inp2, 16)
            
            inp3 = input(f"nabla_out: ").strip().lower()
            if inp3 == 'q':
                break
            nabla_out = int(inp3, 16) if inp3.startswith('0x') else int(inp3, 16)
            
            if (0 <= delta_in < bdt.shape[0] and 
                0 <= nabla_in < bdt.shape[1] and 
                0 <= nabla_out < bdt.shape[2]):
                print(f"BDT[0x{delta_in:x}][0x{nabla_in:x}][0x{nabla_out:x}] = {bdt[delta_in][nabla_in][nabla_out]}")
            else:
                print("Invalid indices!")
        except (ValueError, IndexError):
            print("Invalid input! Please enter hex values.")

def analyze_sbox(sbox):
    """Perform complete S-box analysis"""
    print(f"Analyzing S-box: {[hex(x) for x in sbox]}")
    print(f"S-box size: {len(sbox)}")
    
    # Compute tables
    print("\nComputing DDT...")
    ddt = compute_ddt(sbox)
    
    print("Computing LAT...")
    lat = compute_lat(sbox)
    
    print("Computing BCT...")
    bct = compute_bct(sbox)
    
    print("Computing BDT (this may take longer, it's 3D)...")
    bdt = compute_bdt(sbox)
    
    # Print 2D tables
    print_table(ddt, "Difference Distribution Table (DDT)")
    print_table(lat, "Linear Approximation Table (LAT)")
    print_table(bct, "Boomerang Connectivity Table (BCT)")
    
    # Print BDT info
    print("\n" + "=" * 80)
    print("Boomerang Difference Table (BDT) - 3D Table")
    print("=" * 80)
    print(f"BDT shape: {bdt.shape} (delta_in × nabla_in × nabla_out)")
    print("Note: BDT is too large to display fully. Use interactive query or slice view.")
    
    # Show a sample slice
    print_bdt_slice(bdt, 1, "BDT")
    
    # Statistics
    print("\n" + "=" * 80)
    print("STATISTICS:")
    print("=" * 80)
    print(f"DDT max (excluding dx=0): {np.max(ddt[1:, :])}")
    print(f"LAT max (excluding a=0 or b=0): {np.max(np.abs(lat[1:, 1:]))}")
    print(f"BCT max (excluding dx=0): {np.max(bct[1:, :])}")
    print(f"BDT max (excluding delta_in=0): {np.max(bdt[1:, :, :])}")
    
    return ddt, lat, bct, bdt

# Main execution
if __name__ == "__main__":
    # Check if S-box is defined
    if not SBOX:
        print("Please define your S-box in the SBOX variable!")
        exit(1)
    
    # Analyze S-box
    ddt, lat, bct, bdt = analyze_sbox(SBOX)
    
    # Interactive queries
    print("\n" + "=" * 80)
    print("INTERACTIVE QUERY MODE")
    print("=" * 80)
    
    while True:
        print("\nSelect table to query:")
        print("1. DDT (Difference Distribution Table)")
        print("2. LAT (Linear Approximation Table)")
        print("3. BCT (Boomerang Connectivity Table)")
        print("4. BDT (Boomerang Difference Table) - 3D query")
        print("5. BDT Slice View (fix delta_in, view 2D slice)")
        print("6. Exit")
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == '1':
            query_table(ddt, "DDT")
        elif choice == '2':
            query_table(lat, "LAT")
        elif choice == '3':
            query_table(bct, "BCT")
        elif choice == '4':
            query_bdt(bdt)
        elif choice == '5':
            try:
                delta = input("Enter delta_in (hex): ").strip()
                delta_val = int(delta, 16) if delta.startswith('0x') else int(delta, 16)
                if 0 <= delta_val < bdt.shape[0]:
                    print_bdt_slice(bdt, delta_val)
                else:
                    print("Invalid delta_in value!")
            except ValueError:
                print("Invalid input!")
        elif choice == '6':
            break
        else:
            print("Invalid choice!")