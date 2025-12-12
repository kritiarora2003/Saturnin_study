def reverse_bits(num: int, n: int) -> int:
    """Reverse the bits of num considering it as an n-bit number."""
    result = 0
    for i in range(n):
        # Extract the i-th bit from num
        bit = (num >> i) & 1
        # Place it in the reversed position
        result |= bit << (n - 1 - i)
    return result


    return result
def sbox(S, l=80, inv=False):
    """
    Applies the Twinkle S-box (Sb) to every row of the state S in parallel,
    modifying the input integer directly.
    
    Args:
        S (int): The one-dimensional integer representation of the state S.
        l (int): The third dimension of the state (z-index). Defaults to 80 for Twinkle's 1280-bit state.
        
    Returns:
        int: The updated one-dimensional integer representation of the state S.
    """
    
    # S-box mapping from the paper's table.
    SBOX = {
        0x0: 0x0, 0x1: 0x3, 0x2: 0x5, 0x3: 0xd,
        0x4: 0x6, 0x5: 0xf, 0x6: 0xa, 0x7: 0x8,
        0x8: 0xb, 0x9: 0x4, 0xa: 0xe, 0xb: 0x2,
        0xc: 0x9, 0xd: 0xc, 0xe: 0x7, 0xf: 0x1
    }

    SBOX_INV = {
    0x0: 0x0, 0x3: 0x1, 0x5: 0x2, 0xd: 0x3,
    0x6: 0x4, 0xf: 0x5, 0xa: 0x6, 0x8: 0x7,
    0xb: 0x8, 0x4: 0x9, 0xe: 0xa, 0x2: 0xb,
    0x9: 0xc, 0xc: 0xd, 0x7: 0xe, 0x1: 0xf
    }

    if(inv==False):
        sbox_table = [SBOX[i] for i in range(16)]
    else:
        sbox_table = [SBOX_INV[i] for i in range(16)]
    
    # Iterate through each row of the state.
    for y in range(4):
        for z in range(l):
            # Calculate the starting bit position of the current 4-bit row.
            row_start_index = 4 * y + 16 * z
            
            # 1. Extract the 4-bit S-box input (nibble) from the state S.
            sbox_input = (S >> row_start_index) & 0xF
            # we need to reverse the nibble: ex: 0b0101 -> 0b1010
            sbox_input = reverse_bits(sbox_input,4)
            
            # 2. Look up the S-box output.
            sbox_output = sbox_table[sbox_input]
            sbox_output = reverse_bits(sbox_output,4)
            
            # 3. Create a mask to clear the original 4-bit chunk in the state.
            # We use a bitwise NOT on a mask of 0xF (0b1111) shifted to the correct position.
            clear_mask = ~(0xF << row_start_index)
            
            # 4. Clear the original bits and insert the new bits.
            S = (S & clear_mask) | (sbox_output << row_start_index)
            
    return S