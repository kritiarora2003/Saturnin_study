from .mix_slice_inv import compute_slice_mapping
def left_rotate(val: int, d: int, n: int) -> int:
    """Left rotate an n-bit integer by d positions."""
    d %= n
    return ((val << d) | (val >> (n - d))) & ((1 << n) - 1)


def mix_slice(S: int, l: int = 80, inverse: bool = False) -> int:
    """
    Perform slice-wise left rotations on the 1280-bit state.
    
    Args:
        S (int): The 1280-bit state as an integer.
        d (int): Rotation offset (same for all slices).
        l (int): Number of slices (z dimension), default 80.
    
    Returns:
        int: Updated state after slice rotations.
    """
    if inverse:
        inverse_slice_dict = compute_slice_mapping()
    for z in range(l):
        # Extract slice bits into a 16-bit integer
        slice_val = 0
        for y in range(4):
            for x in range(4):
                bit_pos = x + 4*y + 16*z
                bit = (S >> bit_pos) & 1
                slice_val |= bit << ((x + 4*y))  # LSB = (x=0,y=0)
        
        if inverse:
            rotated_slice = inverse_slice_dict[slice_val]
        else:
            # Rotate slice
            rotated_slice_5 = left_rotate(slice_val, 5, 16)
            rotated_slice_12 = left_rotate(slice_val, 12, 16)
            rotated_slice = (slice_val^rotated_slice_5^rotated_slice_12)

        
        # Plug rotated slice back into S
        for y in range(4):
            for x in range(4):
                bit_pos = x + 4*y + 16*z
                new_bit = (rotated_slice >> ((x + 4*y))) & 1
                if new_bit:
                    S |= (1 << bit_pos)
                else:
                    S &= ~(1 << bit_pos)
    
    return S
