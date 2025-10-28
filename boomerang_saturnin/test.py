def parse_state(lines, start_idx):
    """Parse a 4x4 state matrix from lines starting at start_idx"""
    state = []
    for i in range(4):
        if start_idx + i < len(lines):
            row = lines[start_idx + i].strip().split()
            state.append(row)
    return state

def parse_dump(dump_text):
    """Parse an entire encryption dump into stages"""
    lines = dump_text.strip().split('\n')
    stages = {}
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for stage headers
        if line.startswith('Encrypt - Round'):
            stage_name = line.split(':')[0]
            state = parse_state(lines, i + 1)
            stages[stage_name] = state
            i += 5  # Skip the 4 state lines
        elif line.startswith('Ciphertext'):
            stages['Ciphertext'] = line.split(': ')[1] if ': ' in line else ''
            i += 1
        else:
            i += 1
    
    return stages

def xor_states(state1, state2):
    """XOR two states and return the difference"""
    diff = []
    for i in range(4):
        row_diff = []
        for j in range(4):
            if i < len(state1) and j < len(state1[i]) and \
               i < len(state2) and j < len(state2[i]):
                val1 = int(state1[i][j], 16)
                val2 = int(state2[i][j], 16)
                row_diff.append(f"{val1 ^ val2:04x}")
            else:
                row_diff.append("????")
        diff.append(row_diff)
    return diff

def xor_ciphertexts(ct1, ct2):
    """XOR two ciphertext hex strings"""
    if len(ct1) != len(ct2):
        return "Length mismatch"
    
    result = ""
    for i in range(0, len(ct1), 2):
        b1 = int(ct1[i:i+2], 16)
        b2 = int(ct2[i:i+2], 16)
        result += f"{b1 ^ b2:02x}"
    return result

def print_state(state):
    """Pretty print a state"""
    for row in state:
        print("  " + " ".join(row))

# Read the dump files
try:
    with open('../kriti_saturnin_Implementation/dump/pt1dump.txt', 'r') as f:
        dump1 = f.read()
    print("Successfully read pt1dump.txt")
except FileNotFoundError:
    print("Error: pt1dump.txt not found!")
    exit(1)

try:
    with open('../kriti_saturnin_Implementation/dump/pt2dump.txt', 'r') as f:
        dump2 = f.read()
    print("Successfully read pt2dump.txt")
except FileNotFoundError:
    print("Error: pt2dump.txt not found!")
    exit(1)

# Parse both dumps
stages1 = parse_dump(dump1)
stages2 = parse_dump(dump2)

# Find and display differences
print("\n" + "=" * 70)
print("DIFFERENCES BETWEEN PT1 AND PT2 (XOR)")
print("=" * 70)

for stage_name in stages1.keys():
    if stage_name == 'Ciphertext':
        print(f"\n{stage_name}:")
        ct1 = stages1[stage_name]
        ct2 = stages2[stage_name]
        diff = xor_ciphertexts(ct1, ct2)
        print(f"  PT1: {ct1}")
        print(f"  PT2: {ct2}")
        print(f"  XOR: {diff}")
    else:
        print(f"\n{stage_name}:")
        state1 = stages1[stage_name]
        state2 = stages2[stage_name]
        diff = xor_states(state1, state2)
        print_state(diff)