
from .mix_slice import mix_slice
from .whitening_key import whitening_key
from .round_constant import round_constants
from .lane_rotation import lane_rotation
from .sbox import sbox

def load_test_vectors(filename="test_vectors.txt"):
    """
    Load test vectors from a file containing lines: K,IV
    Both K and IV are hexadecimal integers.
    
    Returns:
        list of tuples: [(key, iv), ...]
    """
    vectors = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) != 2:
                continue  # skip malformed lines
            key = int(parts[0], 16)
            iv = int(parts[1], 16)
            vectors.append((key, iv))
    return vectors

def round_function(S, RC, O0, O1):
    """
    Performs one full round of the Twinkle round function.
    
    Args:
        S (int): 1280-bit state.
        RC (int): Round constant for this round.
        O0, O1 (list[int]): Lane rotation offsets.
    
    Returns:
        int: Updated state after one round.
    """


    S = sbox(S,4)
    S = lane_rotation(S,O0,4)
    S = mix_slice(S,4)
    S = lane_rotation(S,O1,4)
    S ^= RC
    return S

def round_function_inverse(S, RC, O0, O1):
    """
    Performs one full round of the Twinkle round function in inverse.
    """
    S ^= RC
    S = lane_rotation(S,O1,4,True)
    S = mix_slice(S,4,True)
    S = lane_rotation(S,O0,4,True)
    S = sbox(S,4,True)
    
    return S



def round_encryption(K, IV):
    """
    Performs one round of the Twinkle round function.
    """

    # Lane rotation tables
    O0 = [20, 24, 38, 77, 49, 66, 30, 40, 76, 15, 46, 50, 17, 18, 61, 62]
    O1 = [63, 45, 34, 39, 32, 43, 60, 66, 54, 26, 55, 36, 61, 12, 15, 35]
    
    # Whitening
    k0, k1 = whitening_key(K)
    

    S = IV ^ k0
    
    
    # Round constants
    RC = round_constants()

    # Round function
    S = round_function(S, 0, O0, O1)
    # S = round_function(S, 0, O0, O1)

    O = S ^ k1
    
    
    return O

def round_decryption(K, IV):
    """
    Performs one round of the Twinkle round function.
    """

    # Lane rotation tables
    O0 = [20, 24, 38, 77, 49, 66, 30, 40, 76, 15, 46, 50, 17, 18, 61, 62]
    O1 = [63, 45, 34, 39, 32, 43, 60, 66, 54, 26, 55, 36, 61, 12, 15, 35]
    
    # Whitening
    k0, k1 = whitening_key(K)
    

    S = IV ^ k1
    
    
    # Round constants
    RC = round_constants()

    # Round function
    S = round_function_inverse(S, 0, O0, O1)
    # S = round_function_inverse(S, 0, O0, O1)
    
    O = S ^ k0

    
    return O

         


                    

if __name__ == "__main__":

    vectors = load_test_vectors()
    

    for K, IV in vectors:

        print(f"hex(K):{hex(K)}, hex(IV):{hex(IV)}")
        print(f"Encryption: {hex(round_encryption(K, IV))}")
        print(f"Decryption: {hex(round_decryption(K, round_encryption(K, IV)))}")




