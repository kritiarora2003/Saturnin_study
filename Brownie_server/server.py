# server.py
import socket
import threading
from config import SERVER_HOST, SERVER_PORT

clients = {}  # username -> socket
lock = threading.Lock()


def handle_client(conn, addr):
    print(f"[+] Connection from {addr}")
    f = conn.makefile("r")  # text wrapper for line-based messages

    try:
        # First line is the username
        username = f.readline().strip()
        if not username:
            print("[-] No username, closing")
            return

        with lock:
            clients[username] = conn
        print(f"[+] {username} registered")

        # Now read messages: FROM|TO|CIPHERTEXT_HEX\n
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 2)
            if len(parts) != 3:
                print(f"[-] Bad message from {username}: {line}")
                continue

            from_user, to_user, ct_hex = parts
            print(f"[ROUTE] {from_user} -> {to_user}: {ct_hex[:32]}...")

            with lock:
                target_conn = clients.get(to_user)

            if target_conn:
                try:
                    target_conn.sendall((line + "\n").encode("utf-8"))
                except Exception as e:
                    print(f"[-] Error sending to {to_user}: {e}")
            else:
                print(f"[-] User {to_user} not connected")

    except Exception as e:
        print(f"[-] Error with client {addr}: {e}")
    finally:
        with lock:
            # remove any username which maps to this conn
            for u, c in list(clients.items()):
                if c is conn:
                    del clients[u]
                    print(f"[-] {u} disconnected")
        conn.close()


def main():
    print(f"[SERVER] Starting on {SERVER_HOST}:{SERVER_PORT}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(5)
    print("[SERVER] Listening...")

    try:
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
    finally:
        s.close()


if __name__ == "__main__":
    main()
