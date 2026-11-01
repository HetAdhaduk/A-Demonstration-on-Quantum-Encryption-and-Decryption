import socket
import json
import time
import sys
import random
import math

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService

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

# --- VISUAL HACKER EFFECTS ---
def type_text(text, speed=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed + random.uniform(0, 0.01))
    print()

def progress_bar(duration, description="Processing", stall_at=None, stall_msg=""):
    length = 40
    steps = 100
    sleep_time = duration / steps
    
    for i in range(steps + 1):
        if stall_at and i == stall_at:
            time.sleep(0.5)
            type_text(f"\n[!] {stall_msg}", speed=0.04)
            return False
            
        filled = int(length * i // 100)
        bar = '█' * filled + '-' * (length - filled)
        sys.stdout.write(f'\r[*] {description} |{bar}| {i}% ')
        sys.stdout.flush()
        time.sleep(sleep_time)
    print()
    return True

def visual_decrypt_effect(target_text):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*!?"
    sys.stdout.write("[+] Decrypting: ")
    for i in range(len(target_text)):
        for _ in range(5):
            sys.stdout.write('\r[+] Decrypting: ' + target_text[:i] + random.choice(chars))
            sys.stdout.flush()
            time.sleep(0.02)
    sys.stdout.write('\r[+] Decrypting: ' + target_text + '\n')

def ints_to_text(int_list):
    text = ""
    for num in int_list:
        byte_len = (num.bit_length() + 7) // 8
        text += num.to_bytes(max(1, byte_len), 'big').decode('utf-8')
    return text

# --- QISKIT CLOUD PING ---
def run_qiskit_qft():
    try:
        # REPLACE WITH YOUR ACTUAL IBM QUANTUM API TOKEN
        service = QiskitRuntimeService(channel="ibm_quantum", token="YOUR_API_TOKEN_HERE")
    except Exception as e:
        type_text(f"[!] IBM Connection Failed: {e}")
        return

    backend = service.least_busy(simulator=True, operational=True)
    qc = QuantumCircuit(3, 3)
    
    qc.h(2)
    qc.cp(math.pi/2, 1, 2)
    qc.cp(math.pi/4, 0, 2)
    qc.h(1)
    qc.cp(math.pi/2, 0, 1)
    qc.h(0)
    qc.swap(0, 2)
    qc.measure([0,1,2], [0,1,2])
    
    print("\n[*] Quantum Circuit Generated (QFT Phase Extractor):")
    print(qc.draw(output='text'))
    
    compiled_circuit = transpile(qc, backend)
    job = backend.run(compiled_circuit, shots=1024)
    
    sys.stdout.write(f"[*] Pinging IBM Cloud ({backend.name}). Awaiting results ")
    spinner = ['|', '/', '-', '\\']
    while not job.in_final_state():
        for symbol in spinner:
            sys.stdout.write(f"\b{symbol}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\b[+]\n")
    
    counts = job.result().get_counts(qc)
    print(f"[+] Wavefunction Collapsed. Measurement Counts: {counts}")

def start_hacker():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((HOST, PORT))
            print("[+] Tap established. Listening for packets...\n")

            while True:
                mode_payload = recv_msg(client)
                if not mode_payload: break
                mode = mode_payload['mode']
                
                public_key = recv_msg(client)['public_key']
                ciphertext = recv_msg(client)['ciphertext']
                
                print("\n========================================")
                type_text("         INCOMING DATA INTERCEPTED      ", speed=0.03)
                print("========================================")

                if mode == '1':
                    type_text("[>] TARGET: Classical RSA (CPU Brute Force)")
                    N_target = public_key[1]
                    type_text(f"[*] Intercepted Modulus (N): {N_target}")
                    
                    type_text("\n[*] Calculating GNFS Time Complexity...")
                    type_text("    -> Formula: L_N[1/3, c] = exp( c * (ln N)^(1/3) * (ln ln N)^(2/3) )")
                    ln_N = math.log(N_target)
                    ln_ln_N = math.log(ln_N)
                    complexity = math.exp(1.9229 * (ln_N**(1/3)) * (ln_ln_N**(2/3)))
                    
                    type_text(f"    -> Modulus Bits: {N_target.bit_length()} bits")
                    type_text(f"    -> Required Math Operations: ~{int(complexity)*1000} ops")
                    type_text("    -> Processing nodes: 1 (Local CPU)")
                    time.sleep(1)

                    type_text("\n[*] Initiating Classical Period Finding: g^r = mN + 1")
                    type_text("[*] Choosing random integer g = 7")
                    for r in range(1, 6):
                        type_text(f"    [-] Testing r={r}: 7^{r} = {7**r}. Does {7**r} = m({N_target}) + 1? False.")
                        time.sleep(0.15)
                    
                    progress_bar(
                        duration=6, 
                        description="Linear Search for period 'r'", 
                        stall_at=7, 
                        # ADDED EXPLICIT TIME TO DECRYPT HERE
                        stall_msg="FATAL: Computation scaling exponentially. Estimated time to decrypt: > 2.4 Years."
                    )

                elif mode == '2':
                    type_text("[>] TARGET: RSA (Quantum Shor's Algorithm)")
                    N_target = public_key[1]
                    e_target = public_key[0]
                    
                    print("\n--- INITIATING QUANTUM ATTACK SEQUENCE ---")
                    # START LIVE TIMER
                    attack_start_time = time.time()
                    
                    time.sleep(0.5)
                    type_text("[*] STEP 1: SUPERPOSITION")
                    type_text("    -> Applying Hadamard (H) gates to Qubits.")
                    time.sleep(0.5)
                    
                    type_text("\n[*] STEP 2: QUANTUM ENTANGLEMENT")
                    type_text("    -> Applying Controlled-Phase (CP) gates.")
                    time.sleep(0.5)
                    
                    type_text("\n[*] STEP 3: QUANTUM FOURIER TRANSFORM (QFT)")
                    run_qiskit_qft()
                    
                    type_text("\n[*] STEP 4: CLASSICAL POST-PROCESSING (Continued Fractions)")
                    measured_phase = 0.625
                    type_text(f"    -> Extracted Phase (s/r) from Quantum Register: {measured_phase}")
                    type_text("    -> Convergents generated: [1/1, 1/2, 2/3, 3/5, 5/8]")
                    
                    r_simulated = 120 
                    type_text(f"    -> Denominator resolves to Period r = {r_simulated}")
                    
                    p_hacked = next((i for i in range(2, math.isqrt(N_target) + 1) if N_target % i == 0), 0)
                    q_hacked = N_target // p_hacked
                    
                    type_text(f"    -> Applying formula: p, q = GCD(g^(r/2) ± 1, N)")
                    type_text(f"[+] Primes successfully isolated: p = {p_hacked}, q = {q_hacked}")
                    
                    phi = (p_hacked - 1) * (q_hacked - 1)
                    d_hacked = pow(e_target, -1, phi)
                    
                    decrypted_ints = [pow(c, d_hacked, N_target) for c in ciphertext]
                    print("\n========================================")
                    visual_decrypt_effect(ints_to_text(decrypted_ints))
                    
                    # END LIVE TIMER
                    attack_end_time = time.time()
                    elapsed_time = attack_end_time - attack_start_time
                    
                    # PRINT FINAL TIME METRIC
                    type_text(f"[+] MISSION COMPROMISED.")
                    type_text(f"[!] Total time to decrypt: {elapsed_time:.2f} seconds (Quantum Speedup Achieved)", speed=0.05)
                    print("========================================\n")

                elif mode == '3':
                    type_text("[>] TARGET: Post-Quantum Lattice Cryptography (LWE)")
                    q_mod = 97
                    
                    type_text("\n[*] ATTEMPTING LINEAR ALGEBRA ATTACK (Gaussian Elimination)...")
                    type_text(f"    -> Constructing system: A * s = b - e (mod {q_mod})")
                    time.sleep(0.5)
                    
                    for i in range(4):
                        row = [random.randint(10, 90) for _ in range(5)]
                        eq = f"{row[0]}s1 + {row[1]}s2 + {row[2]}s3 + {row[3]}s4 + {row[4]}s5"
                        ans = random.randint(10, 90)
                        type_text(f"    -> Eq {i+1}: {eq} ≡ {ans} + e{i+1} (mod {q_mod})")
                        time.sleep(0.15)
                    
                    type_text("\n[*] Applying row reduction (mod 97)...")
                    time.sleep(1)
                    type_text("    -> ERROR: Unknown error terms 'e' create system with infinite solutions.")
                    
                    type_text("\n[*] SWITCHING TO BABAI'S NEAREST PLANE ALGORITHM...")
                    A_matrix = public_key[0]
                    type_text(f"    -> Target Point b = {public_key[1]}")
                    for i in range(1, 4):
                        type_text(f"    [-] Iteration {i}: Projecting target to nearest grid plane...")
                        time.sleep(0.3)
                        type_text("        ERROR: Distance missed origin by margin > error threshold.")
                        
                    type_text("\n[!] Lattice noise is disrupting coordinate mapping.")
                    
                    progress_bar(
                        duration=8, 
                        description="Solving Shortest Vector Problem (SVP)", 
                        stall_at=12, 
                        # ADDED EXPLICIT TIME TO DECRYPT HERE
                        stall_msg="FATAL: Grid complexity exceeds decryption bounds. Estimated time to decrypt: > 10,000 Years."
                    )
                
                print("[*] Listening for next packet...\n")

    except Exception as e:
        print(f"\n[!] ATTACK TERMINATED: {e}")

if __name__ == "__main__":
    start_hacker()