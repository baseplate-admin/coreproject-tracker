import socket


def test_udp_support(host, port):
    try:
        # Create a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Set a timeout (in case the tracker is unresponsive)
        udp_socket.settimeout(2)

        # Send a dummy message to the tracker
        message = b"test message"
        udp_socket.sendto(message, (host, port))

        # Try to receive a response (if any)
        response, _ = udp_socket.recvfrom(1024)
        print(f"Received response: {response.decode()}")

        return True
    except socket.timeout:
        print("UDP request timed out. The tracker might not support UDP.")
        return False
    except Exception as e:
        print(f"Error occurred: {e}")
        return False
    finally:
        udp_socket.close()


if __name__ == "__main__":
    # Example tracker address and UDP port
    tracker_host = "localhost"  # Replace with actual tracker address
    tracker_port = 9999  # Replace with actual tracker UDP port

    if test_udp_support(tracker_host, tracker_port):
        print(f"The tracker at {tracker_host}:{tracker_port} supports UDP.")
    else:
        print(f"The tracker at {tracker_host}:{tracker_port} does not support UDP.")
