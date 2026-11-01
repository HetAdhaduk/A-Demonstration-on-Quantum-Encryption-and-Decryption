# A Demonstration on Quantum Encryption and Decryption






> **An interactive theoretical physics monograph and real-time simulation suite exploring the transition from classical prime-factorization cryptography (RSA) to quantum-mechanical state engineering (Qubits, Bell & GHZ Entanglement, BB84 QKD), offensive quantum cryptanalysis (Shor's QFT Algorithm), and post-quantum Euclidean lattice security (CVP & LWE).**

**Live Interactive Demo:** `https://physics-da.netlify.app` 

## Abstract & Overview

As fault-tolerant quantum processors harness coherent superposition, non-local entanglement, and the Quantum Fourier Transform (QFT), classical asymmetric protocols face mathematical obsolescence under *Store Now, Decrypt Later (SNDL)* attacks. This repository presents a unified theoretical and experimental investigation across **seven chapters** and **three standalone Working Model Laboratories**, combining formal mathematical derivations with nine interactive HTML5 Canvas simulations.

## Interactive Simulations & Working Models

| Chapter / Lab | Cryptographic & Physical Domain | Interactive Simulation Highlights |
| :--- | :--- | :--- |
| **Portal** | Atomic Orbital Eigenstates | 3D hydrogenic standing-wave orbitals ($\psi_{n,\ell,m}$) coupled with a projective Hilbert octahedron |
| **Chapter I · Lab I** | Classical Asymmetric Security (RSA) | Modular clock ring ($\mathbb{Z}_N$), General Number Field Sieve (GNFS) vs. Shor complexity, and 3-node 64-bit RSA transmission where classical brute-force stalls at 7% ($> 2.4\text{ years}$) |
| **Chapter II** | Two-Level Quantum Systems (Qubits) | 3D rotatable Bloch Sphere with live polar ($\theta$) and azimuthal ($\phi$) controls, unitary gates ($H, X, S$), and Born rule measurement collapse |
| **Chapter III** | Bipartite Entanglement & E91 QKD | EPR Bell states ($\lvert\Phi^+\rangle, \lvert\Psi^-\rangle$), CHSH inequality violation ($S = 2\sqrt{2} > 2$), and eavesdropper decoherence detection |
| **Chapter III-B** | Multipartite Entanglement (GHZ) | Tripartite Greenberger–Horne–Zeilinger state ($\lvert\Psi_{\text{GHZ}}\rangle = (\lvert 000\rangle + \lvert 111\rangle)/\sqrt{2}$) across Alpha, Bravo, and Charlie nodes with 120-shot ensemble sampling |
| **Chapter III-C** | No-Cloning & BB84 Optical Waveguide | Dual-channel polarized photon stream ($Z$ and $X$ bases) demonstrating Wootters–Zurek No-Cloning and the 25.0% intercept-resend QBER spike vs. the 11.0% Shor–Preskill cutoff |
| **Chapter IV · Lab II** | Quantum Cryptanalysis (Shor's QFT) | 3-qubit QFT phase estimation circuit, modular periodicity echoes ($g^x \bmod N$), and constructive interference peak extraction cracking RSA in ~1.42 seconds |
| **Chapter V · Lab III** | Post-Quantum Lattice Cryptography | Euclidean Closest Vector Problem (CVP) comparing private orthogonal bases ($\mathbf{R}_1, \mathbf{R}_2$) vs. public skewed bases ($\mathbf{B}_1, \mathbf{B}_2$), plus Learning With Errors ($\mathbf{b} = \mathbf{A}\mathbf{s} + \mathbf{e} \bmod 97$) |
| **Chapter V-B** | (3,3)-Threshold Quantum Secret Sharing | Galois Field $GF(2)$ key splitting ($K = K_\alpha \oplus K_\beta \oplus K_\gamma$) and 64-bit One-Time Pad matrix reconstructing the classified directive `"THUNDERB"` |
| **Chapter VI & VII** | Comparative Synthesis & QM Foundations | Full regime comparison matrix and breakdown of the 6 core quantum mechanical principles powering the project |

## Where Quantum Mechanics Applies in This Project

1. **Quantum Superposition ($\mathcal{H}_2$):** Coherent linear combinations of basis states ($\lvert\psi\rangle = \alpha\lvert 0\rangle + \beta\lvert 1\rangle$) enabling $2^n$ parallel state evaluations in a single unitary step.
2. **Born's Rule & Wavefunction Collapse:** Projective measurement collapsing superposed states with probability $P(\lvert 0\rangle) = \lvert\alpha\rvert^2 = \cos^2(\theta/2)$ to harvest true physical entropy.
3. **Bipartite & Multipartite Entanglement:** Non-separable Bell and tripartite GHZ wavefunctions establishing correlated cryptographic keys across spatially separated nodes without classical key transmission.
4. **The Quantum No-Cloning Theorem:** Unitary linearity forbidding the duplication of unknown quantum states ($\nexists\, U \text{ s.t. } U\lvert\psi\rangle\lvert 0\rangle = e^{i\delta}\lvert\psi\rangle\lvert\psi\rangle$).
5. **Heisenberg Uncertainty & Conjugate Bases:** Non-commuting Pauli observables ($[\hat{\sigma}_z, \hat{\sigma}_x] = 2i\hat{\sigma}_y \neq 0$) ensuring any eavesdropper basis mismatch injects a detectable 25.0% QBER.
6. **Quantum Interference & the Quantum Fourier Transform (QFT):** Phase coherence amplifying periodic modular echoes at $k/Q \approx s/r$ to factor composite RSA moduli in polynomial time $\mathcal{O}((\log N)^3)$.

## Repository Structure

```text
demonstration-on-quantum-encryption-and-decryption/
├── index.html                                # Main interactive presentation & simulation suite
├── quantum_encryption_presentation.html      # Archival standalone copy
├── README.md                                 # Project documentation & theoretical overview
└── LICENSE                                   # MIT License
```


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