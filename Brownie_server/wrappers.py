from config import BASE_KEY_HEX

from twinkle_implementation.twinkle_prf import (
    round_encryption as _twinkle_encrypt_block,
    round_decryption as _twinkle_decrypt_block,
)

def twinkle_encrypt_block(block_hex: str, key_hex: str) -> str:
    """Encrypt one 64-bit block (16 hex chars) using Twinkle."""
    K = int(key_hex, 16)        # convert 64-bit key from hex string → int
    IV = int(block_hex, 16)     # convert block from hex string → int

    out_int = _twinkle_encrypt_block(K, IV)

    # Convert back to hex, padded to 16 hex chars (64 bits)
    return f"{out_int:016x}"


def twinkle_decrypt_block(block_hex: str, key_hex: str) -> str:
    """Decrypt one 64-bit block (16 hex chars) using Twinkle."""
    K = int(key_hex, 16)
    IV = int(block_hex, 16)

    out_int = _twinkle_decrypt_block(K, IV)

    return f"{out_int:016x}"


from saturnin import encrypt_toy_debug as _saturnin_encrypt_block
from saturnin import decrypt_toy_debug as _saturnin_decrypt_block


def hex32_to_nibbles(block_hex: str):
    assert len(block_hex) == 8
    return [int(block_hex[i], 16) for i in range(8)]


def nibbles_to_hex32(state):
    assert len(state) == 8
    return ''.join(f"{x:X}" for x in state)

def saturnin_encrypt_block(block_hex: str, key_hex: str) -> str:
    # 32-bit block → 8 nibbles
    plaintext = hex32_to_nibbles(block_hex)

    # 32-bit key → 8 nibbles
    key = hex32_to_nibbles(key_hex)

    # encrypt
    out_state = _saturnin_encrypt_block(plaintext, key)

    # convert back to 32-bit hex
    return nibbles_to_hex32(out_state)


def saturnin_decrypt_block(block_hex: str, key_hex: str) -> str:
    ciphertext = hex32_to_nibbles(block_hex)
    key = hex32_to_nibbles(key_hex)

    out_state = _saturnin_decrypt_block(ciphertext, key)

    return nibbles_to_hex32(out_state)


def expand_key_32_to_64(base_key_hex: str) -> str:
    base_key_hex = base_key_hex.lower()
    assert len(base_key_hex) == 8  # 32 bits = 8 hex chars

    k1 = base_key_hex
    k2 = base_key_hex[::-1]  # simple permutation
    return k1 + k2           # 16 hex chars = 64 bits


# ---------- helpers for padding and hex conversion ----------

def pkcs7_pad(data: bytes, block_size: int) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    if pad_len == 0:
        pad_len = block_size
    return data + bytes([pad_len] * pad_len)


def pkcs7_unpad(data: bytes, block_size: int) -> bytes:
    if not data:
        return data
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        # if padding corrupted, you can raise or just return as-is
        return data
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        return data
    return data[:-pad_len]


def text_to_hex(msg: str) -> str:
    return msg.encode("utf-8").hex()


def hex_to_text(h: str) -> str:
    return bytes.fromhex(h).decode("utf-8", errors="ignore")


# ---------- Saturnin message encryption (32-bit block, 32-bit key) ----------

def saturnin_encrypt_message(plaintext: str, base_key_hex: str = BASE_KEY_HEX) -> str:
    key_hex = base_key_hex.lower()
    assert len(key_hex) == 8  # 32-bit key

    block_size_bytes = 4      # 32-bit block
    data = plaintext.encode("utf-8")
    data_padded = pkcs7_pad(data, block_size_bytes)

    ct_hex = ""
    for i in range(0, len(data_padded), block_size_bytes):
        block = data_padded[i:i + block_size_bytes]     # 4 bytes
        block_hex = block.hex()                         # 8 hex chars
        ct_block_hex = saturnin_encrypt_block(block_hex, key_hex)
        ct_hex += ct_block_hex

    return ct_hex


def saturnin_decrypt_message(ciphertext_hex: str, base_key_hex: str = BASE_KEY_HEX) -> str:
    key_hex = base_key_hex.lower()
    assert len(key_hex) == 8

    block_size_bytes = 4
    block_size_hex = block_size_bytes * 2  # 8

    if len(ciphertext_hex) % block_size_hex != 0:
        raise ValueError("Ciphertext length not multiple of block size for Saturnin")

    pt_bytes = b""
    for i in range(0, len(ciphertext_hex), block_size_hex):
        ct_block_hex = ciphertext_hex[i:i + block_size_hex]
        pt_block_hex = saturnin_decrypt_block(ct_block_hex, key_hex)
        pt_bytes += bytes.fromhex(pt_block_hex)

    pt_bytes = pkcs7_unpad(pt_bytes, block_size_bytes)
    return pt_bytes.decode("utf-8", errors="ignore")


# ---------- Twinkle message encryption (64-bit block, 64-bit key) ----------

def twinkle_encrypt_message(base_key_hex: str = BASE_KEY_HEX, plaintext: str = "") -> str:
    print("[DEBUG] base_key_hex passed to encryption:", base_key_hex, " len =", len(base_key_hex))
    key64_hex = expand_key_32_to_64(base_key_hex)
    assert len(key64_hex) == 16  # 64-bit key

    block_size_bytes = 8         # 64-bit block
    data = plaintext.encode("utf-8")
    data_padded = pkcs7_pad(data, block_size_bytes)

    ct_hex = ""
    for i in range(0, len(data_padded), block_size_bytes):
        block = data_padded[i:i + block_size_bytes]     # 8 bytes
        block_hex = block.hex()                         # 16 hex
        ct_block_hex = twinkle_encrypt_block(block_hex, key64_hex)
        ct_hex += ct_block_hex

    return ct_hex


def twinkle_decrypt_message(base_key_hex: str = BASE_KEY_HEX, ciphertext_hex: str = "") -> str:
    key64_hex = expand_key_32_to_64(base_key_hex)
    assert len(key64_hex) == 16

    block_size_bytes = 8
    block_size_hex = block_size_bytes * 2  # 16

    if len(ciphertext_hex) % block_size_hex != 0:
        raise ValueError("Ciphertext length not multiple of block size for Twinkle")

    pt_bytes = b""
    for i in range(0, len(ciphertext_hex), block_size_hex):
        ct_block_hex = ciphertext_hex[i:i + block_size_hex]
        pt_block_hex = twinkle_decrypt_block(ct_block_hex, key64_hex)
        pt_bytes += bytes.fromhex(pt_block_hex)

    pt_bytes = pkcs7_unpad(pt_bytes, block_size_bytes)
    return pt_bytes.decode("utf-8", errors="ignore")
