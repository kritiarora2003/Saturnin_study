# client_sreya.py
import socket
import threading
from config import SERVER_HOST, SERVER_PORT, BASE_KEY_HEX
from wrappers import twinkle_encrypt_message, saturnin_decrypt_message

MY_NAME = "sreya"
PEER_NAME = "kriti"


def recv_loop(sock: socket.socket):
    f = sock.makefile("r")
    for line in f:
        line = line.strip()
        if not line:
            continue
        from_user, to_user, ct_hex = line.split("|", 2)
        if to_user != MY_NAME:
            continue  # not for me (shouldn't happen in 2-user case)

        # Kriti -> Sreya messages are encrypted with SATURNIN
        try:
            plaintext = saturnin_decrypt_message(ct_hex, BASE_KEY_HEX )
        except Exception as e:
            print(f"[!] Decryption error: {e}")
            continue

        print(f"\n{from_user}: {plaintext}")
        print("> ", end="", flush=True)


def send_loop(sock: socket.socket):
    while True:
        try:
            msg = input("> ")
        except EOFError:
            break
        if not msg:
            continue
        # Sreya sends using TWINKLE
        ct_hex = twinkle_encrypt_message(BASE_KEY_HEX, msg)
        line = f"{MY_NAME}|{PEER_NAME}|{ct_hex}\n"
        try:
            sock.sendall(line.encode("utf-8"))
            print("[DEBUG] Sending ciphertext:", ct_hex, "len =", len(ct_hex))
        except Exception as e:
            print(f"[!] Send error: {e}")
            break


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))
    # Send my username first
    sock.sendall((MY_NAME + "\n").encode("utf-8"))
    print(f"[CLIENT] Connected as {MY_NAME} to {SERVER_HOST}:{SERVER_PORT}")

    t_recv = threading.Thread(target=recv_loop, args=(sock,), daemon=True)
    t_recv.start()

    send_loop(sock)
    sock.close()


if __name__ == "__main__":
    main()
