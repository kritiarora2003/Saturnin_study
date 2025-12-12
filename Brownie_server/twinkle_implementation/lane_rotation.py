

def right_rotate_lane(val: int, d: int, n: int = 80) -> int:
    """Right rotate an n-bit integer by d positions."""
    d %= n
    return ((val >> d) | (val << (n - d))) & ((1 << n) - 1)


def lane_rotation(S: int, O, l: int = 80, inverse: bool = False) -> int:
    """
    Perform lane-wise right rotations on the 1280-bit state.
    
    Args:
        S (int): The 1280-bit state as an integer.
        O (list[list[int]]): 4x4 array of rotation amounts, one per lane (x,y).
        l (int): Lane length, defaults to 80.
    
    Returns:
        int: Updated state after lane rotations.
    """
    for y in range(4):
        for x in range(4):
            # Extract lane bits into an 80-bit integer
            lane_val = 0
            for z in range(l):
                bit_pos = x + 4*y + 16*z
                bit = (S >> bit_pos) & 1
                lane_val |= bit << (z)  # MSB = z=79

            # Rotate lane
            offset_index = x + 4 * y
            rotation_amount = O[offset_index] % l
            if (inverse == False): 
                rotated_lane = right_rotate_lane(lane_val, rotation_amount, l)
            else:
                rotated_lane = right_rotate_lane(lane_val, -rotation_amount, l)


            # Plug rotated lane back into S
            for z in range(l):
                bit_pos = x + 4*y + 16*z
                new_bit = (rotated_lane >> (z)) & 1
                if new_bit:
                    S |= (1 << bit_pos)
                else:
                    S &= ~(1 << bit_pos)
    
    return S
