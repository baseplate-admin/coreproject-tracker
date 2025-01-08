def binary_to_hex(binary_string):
    # Ensure the input is treated as bytes
    binary_bytes = binary_string.encode(
        "latin1"
    )  # Use 'latin1' encoding to preserve binary data
    return binary_bytes.hex()