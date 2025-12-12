# build_inverse_dict.py

def left_rotate(val: int, d: int, n: int) -> int:
    """Left rotate an n-bit integer by d positions."""
    d %= n
    return ((val << d) | (val >> (n - d))) & ((1 << n) - 1)


def compute_slice_mapping():
    """
    Builds a dictionary mapping from rotated_slice -> original_slice
    for all 16-bit slices, using the same rotation/xor rule as in mix_slice.
    """
    mapping = {}

    for s in range(1 << 16):  # iterate over all 16-bit values
        rotated_slice_5 = left_rotate(s, 5, 16)
        rotated_slice_12 = left_rotate(s, 12, 16)
        mixed = s ^ rotated_slice_5 ^ rotated_slice_12

        # In case of collisions (non-invertible), store as list
        # if mixed in mapping:
        #     mapping[mixed].append(s)
        # else:
        mapping[mixed] = s

    return mapping


if __name__ == "__main__":
    mapping = compute_slice_mapping()

    # Save mapping to a file
    # import pickle
    # with open("inverse_slice_dict.pkl", "wb") as f:
    #     pickle.dump(mapping, f)

    print(f"Dictionary built with {len(mapping)} unique keys.")
    # collision_count = sum(len(v) > 1 for v in mapping.values())
    # print(f"Number of collisions (non-unique mappings): {collision_count}")
