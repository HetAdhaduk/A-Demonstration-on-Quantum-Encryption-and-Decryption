import socket
import json
import time
import numpy as np

HOST = '0.0.0.0'
PORT = 65432

def send_msg(sock, data):
    """Safely packages and sends data with an end delimiter."""
    payload = json.dumps(data).encode('utf-8') + b'<END>'
    sock.sendall(payload)

def recv_msg(sock):
    """Safely receives data until the end delimiter is found."""
    data = b''
    while b'<END>' not in data:
        chunk = sock.recv(4096)
        if not chunk:
            return None
        data += chunk
    msg_bytes, _, _ = data.partition(b'<END>')
    return json.loads(msg_bytes.decode('utf-8'))

def ints_to_text(int_list):
    text = ""
    for num in int_list:
        byte_len = (num.bit_length() + 7) // 8
        text += num.to_bytes(max(1, byte_len), 'big').decode('utf-8')
    return text

def bits_to_text(bit_list):
    bit_string = ''.join(str(b) for b in bit_list)
    bytes_list = [int(bit_string[i:i+8], 2) for i in range(0, len(bit_string), 8)]
    return bytes(bytes_list).decode('utf-8')

def start_receiver():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print("[*] Receiver online. Waiting for nodes to connect...")

        hacker_conn, sender_conn = None, None

        try:
            hacker_conn, addr1 = server.accept()
            print("[!] Hacker successfully tapped into the network.")

            sender_conn, addr2 = server.accept()
            print("[+] Sender connected.\n")

            # CONTINUOUS LOOP BEGINS HERE
            while True:
                print("----------------------------------------")
                print("[*] Waiting for incoming transmission...")
                
                mode_payload = recv_msg(sender_conn)
                if not mode_payload:
                    print("[-] Sender disconnected. Shutting down loop.")
                    break
                
                mode = mode_payload['mode']
                send_msg(hacker_conn, {'mode': mode})
                time.sleep(0.1)

                print(f"[*] Simulation Mode {mode} detected. Generating keys...")
                if mode in ['1', '2']:
                    p, q = 1000003, 1000033
                    N = p * q
                    phi = (p - 1) * (q - 1)
                    e = 65537
                    d = pow(e, -1, phi)
                    public_key = [e, N]
                    private_key = [d, N]
                    print(f"[*] RSA Public Key Generated: e={e}, N={N}")
                    
                elif mode == '3':
                    q_mod = 97
                    n = 5
                    s = np.random.randint(0, q_mod, n)
                    A = np.random.randint(0, q_mod, (n, n))
                    e_noise = np.random.randint(-1, 2, n)
                    b = (np.dot(A, s) + e_noise) % q_mod
                    
                    public_key = [A.tolist(), b.tolist()]
                    private_key = s.tolist()
                    print("[*] Lattice Public Key Matrix (A) and Vector (b) generated.")

                # Send Keys
                send_msg(sender_conn, {'public_key': public_key})
                send_msg(hacker_conn, {'public_key': public_key})

                # Receive Ciphertext
                cipher_payload = recv_msg(sender_conn)
                ciphertext_list = cipher_payload['ciphertext']
                print("[*] Received encrypted payload. Forwarding copy to Hacker...")
                
                # Forward to Hacker
                send_msg(hacker_conn, {'ciphertext': ciphertext_list})

                # Decrypt
                if mode in ['1', '2']:
                    d, N = private_key[0], private_key[1]
                    decrypted_ints = [pow(c, d, N) for c in ciphertext_list]
                    final_message = ints_to_text(decrypted_ints)
                elif mode == '3':
                    s = np.array(private_key)
                    q_mod = 97
                    decrypted_bits = []
                    for u_list, v in ciphertext_list:
                        u = np.array(u_list)
                        dec = (v - np.dot(s, u)) % q_mod
                        if abs(dec - (q_mod // 2)) < (q_mod // 4):
                            decrypted_bits.append(1)
                        else:
                            decrypted_bits.append(0)
                    final_message = bits_to_text(decrypted_bits)

                print(f"\n[+] FINAL SECURE DECRYPTED MESSAGE: {final_message}")

        except Exception as e:
            print(f"\n[!] NETWORK SEVERED: {e}")
        finally:
            if hacker_conn: hacker_conn.close()
            if sender_conn: sender_conn.close()
            print("[*] Receiver offline.")

if __name__ == "__main__":
    start_receiver()