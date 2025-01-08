def bin_to_hex(binary_string):
    # Ensure the input is treated as bytes
    binary_bytes = binary_string.encode(
        "latin1"
    )  # Use 'latin1' encoding to preserve binary data
    return binary_bytes.hex()


def hex_to_bin(hex_str):
    return bytes.fromhex(hex_str).decode("latin1")
