import socket
import json
import numpy as np

HOST = '127.0.0.1' # Change to Receiver's IP for multi-device
PORT = 65432

def send_msg(sock, data):
    payload = json.dumps(data).encode('utf-8') + b'<END>'
    sock.sendall(payload)

def recv_msg(sock):
    data = b''
    while b'<END>' not in data:
        chunk = sock.recv(4096)
        if not chunk: return None
        data += chunk
    msg_bytes, _, _ = data.partition(b'<END>')
    return json.loads(msg_bytes.decode('utf-8'))

def text_to_ints(text, chunk_size=4):
    bytes_text = text.encode('utf-8')
    chunks = [bytes_text[i:i+chunk_size] for i in range(0, len(bytes_text), chunk_size)]
    return [int.from_bytes(chunk, 'big') for chunk in chunks]

def text_to_bits(text):
    bytes_data = text.encode('utf-8')
    bits = []
    for byte in bytes_data:
        bits.extend([int(b) for b in f"{byte:08b}"])
    return bits

def get_user_input():
    print("\n========================================")
    print("   QUANTUM ENCRYPTION SIMULATOR V2.0    ")
    print("========================================")
    print("1. Case 1: Classical RSA (Hacker fails)")
    print("2. Case 2: Quantum Shor's Attack (Hacker wins)")
    print("3. Case 3: Post-Quantum Lattice (Hacker fails)")
    print("Type 'exit' to quit.")
    print("========================================")
    
    mode = input("Enter mode (1, 2, 3, or exit): ").lower()
    if mode == 'exit':
        return 'exit', ''
        
    while mode not in ['1', '2', '3']:
        mode = input("Invalid. Enter mode 1, 2, or 3: ")
        
    message = input("Enter the secret message to send: ")
    return mode, message

def start_sender():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((HOST, PORT))
            print("[+] Connected to Receiver.")

            # CONTINUOUS LOOP BEGINS HERE
            while True:
                mode, message = get_user_input()
                if mode == 'exit':
                    print("[*] Disconnecting...")
                    break

                send_msg(client, {'mode': mode})

                pub_key_data = recv_msg(client)
                public_key = pub_key_data['public_key']
                
                print("[*] Encrypting message...")
                
                if mode in ['1', '2']:
                    e, N = public_key[0], public_key[1]
                    message_ints = text_to_ints(message)
                    ciphertext = [pow(m, e, N) for m in message_ints]
                    
                elif mode == '3':
                    q_mod = 97
                    n = 5
                    A = np.array(public_key[0])
                    b = np.array(public_key[1])
                    
                    bits = text_to_bits(message)
                    ciphertext = []
                    for bit in bits:
                        r = np.random.randint(0, 2, n)
                        u = (np.dot(A.T, r) % q_mod).tolist()
                        v = int((np.dot(b, r) + bit * (q_mod // 2)) % q_mod)
                        ciphertext.append([u, v])

                send_msg(client, {'ciphertext': ciphertext})
                print("[+] Encrypted payload successfully transmitted.")

    except Exception as e:
        print(f"\n[!] TRANSMISSION FAILED: {e}")

if __name__ == "__main__":
    start_sender()