# A Demonstration on Quantum Encryption and Decryption







> **A full-stack physics demonstration and cryptographic testbed combining a real-time 3-node Python/Qiskit network simulator (`Receiver.py`, `hacker.py`, `sender.py`), a 3-party GHZ Quantum Secret Sharing engine (`prob 3.py`), and an interactive 2D/3D web monograph (`index.html`).**

**Live Interactive Web Presentation:** `https://your-site-name.netlify.app` *(Replace with your Netlify Drop URL)*

## GitHub "About" Sidebar Descriptions (Short Options)

Choose one of these concise descriptions (under GitHub's 350-character limit) for your repository's **About** sidebar:

* **Option 1 (Comprehensive — 338 chars):** Full-stack Quantum Encryption & Decryption demonstration featuring a 3-node Python/Qiskit TCP network testbed (RSA vs. Shor's QFT Attack vs. Post-Quantum Lattice LWE), a 3-party GHZ & BB84 Quantum Secret Sharing simulator (`Operation Thunderbolt`), and an interactive 2D/3D HTML5 Canvas physics presentation.
* **Option 2 (Action-Oriented — 246 chars):** Interactive physics monograph and Python/Qiskit working models demonstrating Classical RSA, Shor's Algorithm (IBM Quantum QFT), Post-Quantum Lattice Cryptography (LWE), BB84 QKD, and 3-Party GHZ Quantum Secret Sharing.
* **Option 3 (Short & Punchy — 172 chars):** Python/Qiskit cryptographic network simulations and interactive 3D web visualizations for Quantum Encryption, Shor's QFT Attack, BB84 QKD, and Lattice LWE Security.

**Recommended GitHub Topics:**
`quantum-cryptography` `qiskit` `python` `shors-algorithm` `bb84-protocol` `post-quantum-cryptography` `lattice-cryptography` `quantum-secret-sharing` `ghz-state` `bloch-sphere`

## Abstract & Architecture Overview

As fault-tolerant quantum processors harness coherent superposition, non-local entanglement, and the Quantum Fourier Transform (QFT), classical asymmetric protocols face mathematical obsolescence under *Store Now, Decrypt Later (SNDL)* attacks. This repository unites **three complementary components**:

1. **Multi-Node Python TCP Cryptanalysis Testbed (`Receiver.py`, `hacker.py`, `sender.py`):** A live socket-based network simulation where a Sender transmits encrypted payloads to a Receiver while a Hacker node passively taps the line and executes classical brute-force, IBM Quantum QFT period-finding (Shor's Algorithm), and post-quantum lattice attacks (Gaussian Elimination & Babai's Nearest Plane).
2. **Operation Thunderbolt — 3-Party Quantum Secret Sharing (`prob 3.py`):** A Qiskit `AerSimulator` workflow using 120 tripartite GHZ states, dual-channel BB84 Quantum Key Distribution (160 raw qubits/channel), and 3-way XOR One-Time Pad splitting ($K = K_\alpha \oplus K_\beta \oplus K_\gamma$) to protect the 64-bit directive `"THUNDERB"`, detect a compromised commander (Charlie), and generate 10 publication-grade Matplotlib diagnostic plots.
3. **Interactive Web Monograph & 3D Physics Laboratories (`index.html`):** A zero-build single-page web application with KaTeX mathematical typesetting and nine interactive HTML5 Canvas simulations across seven chapters.

## Repository Structure

```text
demonstration-on-quantum-encryption-and-decryption/
├── index.html                                # Main interactive web presentation & 3D/2D simulation suite
├── quantum_encryption_presentation.html      # Archival standalone copy of the web presentation
├── Receiver.py                               # TCP Server: Key Authority & Decryption Node (Modes 1, 2, 3)
├── hacker.py                                 # TCP Client: Eavesdropper & IBM Qiskit Cryptanalysis Node
├── sender.py                                 # TCP Client: Interactive Encryption CLI (QUANTUM SIMULATOR V2.0)
├── prob 3.py                                 # Qiskit Aer simulation: 3-Party GHZ + BB84 QSS & 10 Plot Generator
├── README.md                                 # Project documentation & execution guide
└── LICENSE                                   # MIT License
```

## Part I · Python Working Models (3-Node TCP Cryptographic Testbed)

The three networked scripts (`Receiver.py`, `hacker.py`, and `sender.py`) communicate over TCP sockets (default `127.0.0.1:65432`, or across three separate laptops on a LAN by setting `HOST` in `hacker.py` and `sender.py` to the Receiver's IP address).

### Cryptographic Cases Simulated

| Mode | Cryptographic Regime | Key & Cipher Parameters (`Receiver.py` / `sender.py`) | Adversarial Attack (`hacker.py`) | Empirical Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **Mode 1** | **Classical RSA** | $p = 1,000,003$, $q = 1,000,033$, $N = 1,000,036,000,099$, $e = 65537$, $c_i \equiv m_i^e \pmod N$ | Computes GNFS complexity $L_N[1/3, c]$ and tests linear period search $7^r \equiv 1 \pmod N$ | **Hacker Fails:** Linear search stalls at **7%** (`Estimated time to decrypt: > 2.4 Years`) |
| **Mode 2** | **RSA under Quantum Attack** | Identical 40-bit composite RSA modulus $N = p \cdot q$ and exponent $e = 65537$ | Builds & transpiles a 3-qubit **QFT Phase Extractor** circuit via `QiskitRuntimeService`, extracts eigenphase $s/r = 0.625$ via continued fractions (`5/8`), finds $r = 120$, and isolates $p, q = \gcd(g^{r/2} \pm 1, N)$ | **Hacker Wins:** Private key $d$ recovered and message decrypted in seconds (**Quantum Speedup**) |
| **Mode 3** | **Post-Quantum Lattice (LWE)** | Modulus $q = 97$, dimension $n = 5$, $\mathbf{A} \in \mathbb{Z}_{97}^{5\times 5}$, secret $\mathbf{s}$, noise $\mathbf{e} \in \{-1,0,1\}^5$, public $\mathbf{b} = (\mathbf{A}\mathbf{s} + \mathbf{e}) \bmod 97$ | Attempts Gaussian elimination ($\mathbf{A}\mathbf{s} \equiv \mathbf{b} - \mathbf{e} \pmod{97}$) and **Babai's Nearest Plane Algorithm** / Shortest Vector Problem (SVP) | **Hacker Fails:** Noise disrupts coordinate mapping; SVP stalls at **12%** (`Estimated time to decrypt: > 10,000 Years`) |

### Step-by-Step Execution Order (Important)

`Receiver.py` accepts connections sequentially (`hacker_conn` first, then `sender_conn`). Always launch the three terminals in this exact order:

**1. Install Python Dependencies:**
```bash
pip install numpy matplotlib qiskit qiskit-aer qiskit-ibm-runtime
```

**2. Terminal 1 — Start the Receiver (Server):**
```bash
python Receiver.py
# Output: [*] Receiver online. Waiting for nodes to connect...
```

**3. Terminal 2 — Connect the Hacker Tap (First Client):**
*(Optional: Replace `YOUR_API_TOKEN_HERE` on line 61 of `hacker.py` with your IBM Quantum API token for live cloud simulation).*
```bash
python hacker.py
# Output: [+] Tap established. Listening for packets...
```

**4. Terminal 3 — Launch the Sender CLI (Second Client):**
```bash
python sender.py
# Select Mode 1 (Classical RSA), Mode 2 (Quantum Shor's Attack), or Mode 3 (Post-Quantum Lattice)
# Enter any secret plaintext message to transmit!
```

## Part II · Operation Thunderbolt: 3-Party Quantum Secret Sharing (`prob 3.py`)

`prob 3.py` executes an end-to-end Qiskit `AerSimulator` demonstration of multipartite quantum cryptography protecting the 8-byte (64-bit) classified command `"THUNDERB"` across three generals: **Alpha ($\alpha$)**, **Bravo ($\beta$)**, and **Charlie ($\gamma$)**.

### Four-Phase Protocol Workflow

1. **Phase 1 — Tripartite GHZ Entanglement Generation:** Prepares 120 GHZ triplets in the maximally entangled state $\lvert\Psi_{\text{GHZ}}\rangle = (\lvert 000\rangle + \lvert 111\rangle)/\sqrt{2}$ using $H$ and cascaded $\text{CNOT}$ gates, achieving 100% $Z$-basis correlation across all three generals.
2. **Phase 2 — Dual-Channel BB84 Quantum Key Distribution:** Runs 160-qubit BB84 sessions on Channel A ($\alpha \leftrightarrow \beta$, clean link with $0.0\%$ QBER) and Channel B ($\alpha \leftrightarrow \gamma$, where Charlie acts as a traitor with $0.9$ interception probability, inducing $\sim 25\%$ QBER and triggering the $> 11.0\%$ security alarm).
3. **Phase 3 — 3-Way Galois Field $GF(2)$ Key Splitting:** Splits the 64-bit GHZ master key into three shares ($K = K_\alpha \oplus K_\beta \oplus K_\gamma$) and encrypts `"THUNDERB"` via One-Time Pad ($C = M \oplus K$).
4. **Phase 4 — Threshold Reconstruction Ceremony:** Verifies that single-party ($\alpha$ only) or two-party ($\alpha \oplus \beta$) coalitions yield unreadable noise, whereas uniting all three shares ($\alpha \oplus \beta \oplus \gamma$) reconstructs `"THUNDERB"`.

### Running `prob 3.py` & Generated Diagnostic Plots

```bash
python "prob 3.py"
```

Executing `prob 3.py` automatically generates and saves **10 high-resolution dark-theme analytical plots**:

| Output Filename | Visualization Content |
| :--- | :--- |
| `plot1_protocol_overview.png` | Full 4-phase architecture flowchart across Generals Alpha, Bravo, and Charlie |
| `plot2_ghz_circuits.png` | Gate-level quantum circuit schematics and outcomes for the first 6 GHZ triplets |
| `plot3_ghz_statistics.png` | All-$Z$-basis measurement histogram ($\lvert 000\rangle$ vs. $\lvert 111\rangle$) and rolling 10-triplet correlation rate |
| `plot4_quantum_key_heatmap.png` | 64-bit GHZ quantum random key bitstreams compared across $\alpha$, $\beta$, and $\gamma$ |
| `plot5_secret_splitting.png` | $8 \times 8$ binary matrices of Master Key $K$, Shares $K_\alpha, K_\beta, K_\gamma$, Ciphertext $C$, and XOR verification |
| `plot6_bb84_channels.png` | Side-by-side sifted key comparison for Channel A ($\alpha \leftrightarrow \beta$ clean) vs. Channel B ($\alpha \leftrightarrow \gamma$ compromised) |
| `plot7_encryption_grid.png` | Bitwise One-Time Pad encryption matrix ($\text{Plaintext} \oplus K = \text{Ciphertext}$) |
| `plot8_traitor_detection.png` | QBER threshold bar chart ($11\%$ cutoff), bit-agreement profile, and traitor impact summary |
| `plot9_reconstruction.png` | $2 \times 2$ comparison of $\alpha$ only ($1/3$), $\alpha + \beta$ ($2/3$), $\alpha + \beta + \gamma$ ($3/3$), and raw ciphertext |
| `plot10_security_dashboard.png` | Comprehensive executive dashboard with telemetry cards, share distribution donut chart, and security audit |

## Part III · Interactive Web Monograph & 3D Simulations (`index.html`)

The web frontend (`index.html`) brings the theoretical physics and all working models into an interactive browser environment with zero build steps:

* **Portal:** 3D Atomic Orbital Eigenstates ($\psi_{n,\ell,m}$) & Faceted Hilbert Octahedron
* **Chapter I (Lab I):** Modular Clock Ring ($\mathbb{Z}_N$), GNFS vs. Shor Complexity Curve & 3-Node RSA Simulator
* **Chapter II:** 3D Rotatable Bloch Sphere, Unitary Gates ($H, X, S$) & Born Probability Spectrum
* **Chapter III, III-B & III-C:** Bipartite EPR Bell States, Tripartite GHZ Atomic Lattice & BB84 Polarized Optical Waveguide
* **Chapter IV (Lab II):** 3-Qubit QFT Circuit, Modular Periodicity Echoes ($g^x \bmod N$) & Shor Interference Spectrum
* **Chapter V & V-B (Lab III):** Euclidean Lattice CVP Good/Bad Basis Visualizer, Babai Nearest-Plane LWE Probe & (3,3)-Threshold OTP Matrix
* **Chapter VI & VII:** Comparative Cryptographic Synthesis & Core Quantum Mechanical Concepts

## Project Contributors & Research Team

* **Adhaduk Het** — Registration No. `26BCE1546`
* **Vibhor Srivastava** — Registration No. `26BCE1599`
* **Soham Kulkarni** — Registration No. `26BCE1590`
* **Tanish Sharma** — Registration No. `26BCE1514`
* **Abhiraj Vashishth** — Registration No. `26BCE1600`
* **Swadhin Pranadev Dash** — Registration No. `26BCE1583`
* **Kevin Solanki** — Registration No. `26BCE1562`
* **Rudraksh Pahwa** — Registration No. `26BCE1527`

## License

Distributed under the MIT License. See `LICENSE` for more information.