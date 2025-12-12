def left_rotate(num: int, d: int, n: int) -> int:
    """Left rotate num by d bits for an n-bit number."""
    d %= n  # in case d >= n
    return ((num << d) | (num >> (n - d))) & ((1 << n) - 1)


def right_rotate(num: int, d: int, n: int) -> int:
    """Right rotate num by d bits for an n-bit number."""
    d %= n
    return ((num >> d) | (num << (n - d))) & ((1 << n) - 1)


def whitening_key(K):
    """
    Calculates the whitening keys k0 and k1 from the master key K.

    Args:
        K (int): The 1280-bit integer master key.

    Returns:
        tuple: A tuple containing two 1280-bit integers, (k0, k1).
    """
    rho = 64  # The internal state size
    
    # k0 is set to K
    k0 = K
    
    # k1 is calculated as (K >>> 1) XOR (K >>> rho-1)
        
    k1 = right_rotate(K, 1, rho) ^ (K >> (rho - 1))
    
    return k0, k1