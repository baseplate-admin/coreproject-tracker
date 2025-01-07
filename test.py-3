import struct


def parse_udp_packet(msg):
    # Step 1: Extract the Protocol Identifier (4 bytes)
    protocol_identifier = struct.unpack(">I", msg[:4])[0]

    # Step 2: Extract the Action (4 bytes)
    action = struct.unpack(">I", msg[4:8])[0]

    # Step 3: Extract the Transaction ID (4 bytes)
    transaction_id = struct.unpack(">I", msg[8:12])[0]

    # Step 4: Extract the Payload (remaining bytes)
    payload = msg[12:]

    # Create a dictionary to hold the parsed data
    params = {
        "protocolIdentifier": hex(protocol_identifier),
        "action": action,
        "transactionId": transaction_id,
        "type": "udp",
        "payload": payload.hex(),
    }

    # Handle specific actions
    if action == 0:  # Connect action
        if len(payload) >= 16:
            connection_id = struct.unpack(">Q", payload[:8])[0]
            params["connectionId"] = hex(connection_id)
        else:
            params["error"] = "Invalid payload for connect action"

    elif action == 1:  # Announce action (this would have more details)
        params["error"] = "Announce action processing not implemented"

    elif action == 2:  # Scrape action (this would also need more processing)
        params["error"] = "Scrape action processing not implemented"

    elif action == 3:  # Error action
        params["error"] = "Error action processing not implemented"

    return params


# Example usage:
msg = b"\x00\x00\x04\x17'\x10\x19\x80\x00\x00\x00\x00\xf4\xa7\xef\x1f"  # Your packet
parsed_data = parse_udp_packet(msg)

# Print the parsed result
print(parsed_data)
