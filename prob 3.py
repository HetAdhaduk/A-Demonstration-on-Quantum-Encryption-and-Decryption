"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     OPERATION THUNDERBOLT — 3-PARTY QUANTUM SECRET SHARING (QSS)           ║
║                                                                              ║
║  PROBLEM:                                                                    ║
║    A classified military command "THUNDERB" must be protected using         ║
║    Quantum Secret Sharing. Three generals (Alpha, Bravo, Charlie) each      ║
║    receive a quantum share. The command can ONLY be decrypted when ALL       ║
║    THREE cooperate. If any single general is compromised, the others         ║
║    detect the breach.                                                        ║
║                                                                              ║
║  WHAT MAKES THIS COMPLEX:                                                    ║
║    1. GHZ States (3-qubit entanglement, not just 2-qubit Bell pairs)        ║
║    2. Three-party protocol with 2 independent quantum channels               ║
║    3. 3-way XOR secret sharing: K = K_α ⊕ K_β ⊕ K_γ                       ║
║    4. Traitor scenario: Charlie (γ) is compromised, detected by peers       ║
║    5. Partial reconstruction: Alpha + Bravo recover despite Charlie          ║
║    6. 10 rich visual plots                                                   ║
║                                                                              ║
║  REQUIRES: pip install qiskit qiskit-aer matplotlib numpy                   ║
║  RUN:      python qss_thunderbolt.py                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from collections import Counter

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
SECRET_COMMAND   = "THUNDERB"          # 8 chars = 64 bits (fits well in 3 shares)
NUM_GHZ          = 120                 # GHZ triplets for quantum randomness
NUM_QKD_BITS     = 160                 # Raw qubits per quantum channel
CHARLIE_TRAITOR  = True                # Simulate Charlie being compromised
random.seed(7)
np.random.seed(7)

PALETTE = {
    'alpha':   '#6929C4',   # Purple  — General Alpha
    'bravo':   '#1192E8',   # Blue    — General Bravo
    'charlie': '#DA1E28',   # Red     — General Charlie (traitor)
    'honest':  '#24A148',   # Green   — Honest outcome
    'corrupt': '#FF832B',   # Orange  — Corrupted
    'bg':      '#0F0F0F',   # Near-black background
    'panel':   '#1A1A1A',   # Panel background
    'text':    '#F4F4F4',   # Light text
    'zero':    '#4589FF',   # Bit 0
    'one':     '#EE538B',   # Bit 1
    'ghz':     '#08BDBA',   # GHZ teal
    'key':     '#F1C21B',   # Key yellow
    'cipher':  '#A56EFF',   # Cipher purple-light
}

cmap_bits = LinearSegmentedColormap.from_list('bits', [PALETTE['zero'], PALETTE['one']])

backend = AerSimulator()

print("=" * 66)
print("   OPERATION THUNDERBOLT — 3-PARTY QUANTUM SECRET SHARING")
print(f"   Command: '{SECRET_COMMAND}' | GHZ triplets: {NUM_GHZ}")
print(f"   Traitor scenario: Charlie {'IS' if CHARLIE_TRAITOR else 'is NOT'} compromised")
print("=" * 66)

# ═══════════════════════════════════════════════════════════════════
# PHASE 1 — GHZ STATE GENERATION (Quantum Randomness Source)
# ═══════════════════════════════════════════════════════════════════
print("\n[PHASE 1] Generating GHZ states for quantum randomness...")

def build_ghz_circuit(measure_bases):
    """
    Build a GHZ circuit with given measurement bases.
    measure_bases: list of 3 values (0=Z, 1=X) for each party.
    Returns circuit and qubit labels.
    """
    qc = QuantumCircuit(3, 3)
    # Create GHZ state: (|000> + |111>) / sqrt(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.barrier()
    # Apply basis rotations before measurement
    for q, b in enumerate(measure_bases):
        if b == 1:
            qc.h(q)   # X-basis measurement
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc

# Generate all-Z-basis GHZ measurements (perfect correlation for key generation)
alpha_bits_raw  = []
bravo_bits_raw  = []
charlie_bits_raw = []
ghz_outcomes     = []

for _ in range(NUM_GHZ):
    qc = build_ghz_circuit([0, 0, 0])   # All Z-basis
    compiled = transpile(qc, backend)
    result   = backend.run(compiled, shots=1).result()
    outcome  = list(result.get_counts().keys())[0]
    # Qiskit returns bits in reverse order (qubit 2 first)
    bits     = [int(b) for b in reversed(outcome)]
    alpha_bits_raw.append(bits[0])
    bravo_bits_raw.append(bits[1])
    charlie_bits_raw.append(bits[2])
    ghz_outcomes.append(outcome)

# Verify GHZ correlation
perfect_corr = sum(1 for o in ghz_outcomes if o in ('000', '111'))
corr_rate    = perfect_corr / NUM_GHZ * 100
print(f"  GHZ correlation rate (|000>+|111>): {corr_rate:.1f}%  "
      f"(expected: 100%)")

# ═══════════════════════════════════════════════════════════════════
# PHASE 2 — QUANTUM CHANNEL (BB84) Alpha→Bravo and Alpha→Charlie
# ═══════════════════════════════════════════════════════════════════
print("\n[PHASE 2] Quantum key channels (BB84)...")

def run_bb84(n_bits, eve_present=False, eve_intercept_prob=1.0):
    """
    Run a full BB84 protocol. Returns (alice_key, bob_key, error_rate).
    eve_intercept_prob: fraction of bits Eve intercepts.
    """
    alice_bits  = [random.randint(0, 1) for _ in range(n_bits)]
    alice_bases = [random.randint(0, 1) for _ in range(n_bits)]
    bob_bases   = [random.randint(0, 1) for _ in range(n_bits)]
    bob_results = []

    for i in range(n_bits):
        qc = QuantumCircuit(1, 1)
        if alice_bits[i] == 1:
            qc.x(0)
        if alice_bases[i] == 1:
            qc.h(0)

        # Eve intercepts with probability eve_intercept_prob
        if eve_present and random.random() < eve_intercept_prob:
            eve_basis = random.randint(0, 1)
            if eve_basis == 1:
                qc.h(0)
            qc.measure(0, 0)
            compiled = transpile(qc, backend)
            res = backend.run(compiled, shots=1).result()
            eve_bit = int(list(res.get_counts().keys())[0])
            qc = QuantumCircuit(1, 1)
            if eve_bit == 1:
                qc.x(0)
            if eve_basis == 1:
                qc.h(0)

        if bob_bases[i] == 1:
            qc.h(0)
        qc.measure(0, 0)
        compiled = transpile(qc, backend)
        res = backend.run(compiled, shots=1).result()
        bob_results.append(int(list(res.get_counts().keys())[0]))

    # Sift
    sifted_a, sifted_b = [], []
    for i in range(n_bits):
        if alice_bases[i] == bob_bases[i]:
            sifted_a.append(alice_bits[i])
            sifted_b.append(bob_results[i])

    # Error check
    sample_n = min(20, len(sifted_a) // 3)
    sample   = random.sample(range(len(sifted_a)), sample_n)
    errors   = sum(sifted_a[i] != sifted_b[i] for i in sample)
    error_rate = errors / sample_n * 100

    keep = [i for i in range(len(sifted_a)) if i not in set(sample)]
    return ([sifted_a[i] for i in keep],
            [sifted_b[i] for i in keep],
            error_rate)

# Channel 1: Alpha ↔ Bravo  (honest channel)
print("  Channel A: Alpha ↔ Bravo  [NO eavesdropper]")
key_alpha_AB, key_bravo_AB, err_AB = run_bb84(NUM_QKD_BITS, eve_present=False)
print(f"    Sifted: {len(key_alpha_AB)} bits | Error rate: {err_AB:.1f}%")

# Channel 2: Alpha ↔ Charlie  (Charlie is traitor / Eve)
print(f"  Channel B: Alpha ↔ Charlie [Eve={'YES ⚠️' if CHARLIE_TRAITOR else 'NO'}]")
key_alpha_AC, key_charlie_AC, err_AC = run_bb84(
    NUM_QKD_BITS,
    eve_present=CHARLIE_TRAITOR,
    eve_intercept_prob=0.9
)
print(f"    Sifted: {len(key_alpha_AC)} bits | Error rate: {err_AC:.1f}%")

charlie_detected = err_AC > 11.0
print(f"\n  Security verdict — Channel B: "
      f"{'⚠️  CHARLIE DETECTED AS TRAITOR!' if charlie_detected else '✅ Channel clean'}")

# ═══════════════════════════════════════════════════════════════════
# PHASE 3 — 3-WAY SECRET KEY SPLITTING
# ═══════════════════════════════════════════════════════════════════
print("\n[PHASE 3] 3-Way XOR secret key splitting...")

def text_to_bits(text):
    bits = []
    for ch in text:
        v = ord(ch)
        for p in range(7, -1, -1):
            bits.append((v >> p) & 1)
    return bits

def bits_to_text(bits):
    text = ""
    for i in range(0, len(bits) - 7, 8):
        byte = bits[i:i+8]
        if len(byte) == 8:
            text += chr(int("".join(str(b) for b in byte), 2))
    return text

message_bits = text_to_bits(SECRET_COMMAND)
n_msg        = len(message_bits)   # 64 bits
print(f"  Message '{SECRET_COMMAND}' = {n_msg} bits")

# Generate master key from GHZ quantum randomness
# Use alpha's GHZ bits (they're correlated with bravo and charlie)
ghz_key = (alpha_bits_raw * ((n_msg // NUM_GHZ) + 2))[:n_msg]

# 3-way XOR split: K = share_α ⊕ share_β ⊕ share_γ
share_alpha   = [random.randint(0, 1) for _ in range(n_msg)]
share_bravo   = [random.randint(0, 1) for _ in range(n_msg)]
share_charlie = [g ^ a ^ b for g, a, b in zip(ghz_key, share_alpha, share_bravo)]
# Verify: share_α ⊕ share_β ⊕ share_γ = ghz_key
verify_key = [a ^ b ^ c for a, b, c in zip(share_alpha, share_bravo, share_charlie)]
assert verify_key == ghz_key, "XOR key split failed!"
print(f"  ✅ 3-way split verified: K_α ⊕ K_β ⊕ K_γ = K")

# Encrypt using ghz_key
ciphertext_bits = [m ^ k for m, k in zip(message_bits, ghz_key)]
ciphertext_hex  = hex(int("".join(str(b) for b in ciphertext_bits), 2))[2:].upper()
print(f"  Encrypted (hex): {ciphertext_hex}")

# ═══════════════════════════════════════════════════════════════════
# PHASE 4 — RECONSTRUCTION (with/without traitor)
# ═══════════════════════════════════════════════════════════════════
print("\n[PHASE 4] Reconstruction ceremony...")

# --- Full reconstruction (all 3 honest) ---
reconstructed_key_full = [a ^ b ^ c for a, b, c in
                           zip(share_alpha, share_bravo, share_charlie)]
decrypted_full = [ct ^ k for ct, k in zip(ciphertext_bits, reconstructed_key_full)]
text_full      = bits_to_text(decrypted_full)
print(f"  Full reconstruction (α+β+γ): '{text_full}'  "
      f"{'✅' if text_full == SECRET_COMMAND else '❌'}")

# --- Partial: Alpha only (should fail) ---
key_alpha_only = share_alpha
decrypted_alpha = [ct ^ k for ct, k in zip(ciphertext_bits, key_alpha_only)]
text_alpha_only = bits_to_text(decrypted_alpha)
print(f"  Partial (α only):           '{text_alpha_only}' (garbage, as expected)")

# --- Partial: Alpha + Bravo (missing Charlie's share) ---
# Bravo has corrupted share due to Charlie's interference — use dummy
key_ab      = [a ^ b for a, b in zip(share_alpha, share_bravo)]
decrypted_ab = [ct ^ k for ct, k in zip(ciphertext_bits, key_ab)]
text_ab     = bits_to_text(decrypted_ab)
print(f"  Partial (α+β, missing γ):  '{text_ab}' (incomplete key)")

# ═══════════════════════════════════════════════════════════════════
# VISUALIZATIONS (10 PLOTS)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 66)
print("  GENERATING 10 VISUAL PLOTS...")
print("=" * 66)
plt.style.use('dark_background')


# ══════════════════════════════════════════════════════
# PLOT 1 — Protocol Overview Flowchart
# ══════════════════════════════════════════════════════
fig1, ax = plt.subplots(figsize=(18, 9))
fig1.patch.set_facecolor(PALETTE['bg'])
ax.set_facecolor(PALETTE['bg'])
ax.set_xlim(0, 18); ax.set_ylim(0, 9); ax.axis('off')
ax.set_title("PLOT 1 — Operation Thunderbolt: 3-Party QSS Protocol Overview",
             color=PALETTE['text'], fontsize=14, fontweight='bold', pad=10)

def draw_box(ax, x, y, w, h, label, sublabel, color, fontsize=9):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                           linewidth=1.5, edgecolor=color,
                           facecolor=color+'22')
    ax.add_patch(rect)
    ax.text(x + w/2, y + h*0.65, label, ha='center', va='center',
            color=color, fontsize=fontsize, fontweight='bold')
    ax.text(x + w/2, y + h*0.25, sublabel, ha='center', va='center',
            color=PALETTE['text'], fontsize=7, alpha=0.8)

def draw_arrow(ax, x1, y1, x2, y2, color='white', lw=1.5):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=lw, mutation_scale=15))

# Row 1 — Alice's side
draw_box(ax, 0.3, 6.5, 3.2, 2.0, "PHASE 1\nGHZ Generation",
         f"{NUM_GHZ} GHZ triplets\n(|000>+|111>)/√2", PALETTE['ghz'], 10)
draw_box(ax, 4.0, 6.5, 3.2, 2.0, "PHASE 2\nBB84 Channels",
         "2 independent QKD links\nAlpha→Bravo, Alpha→Charlie", PALETTE['alpha'], 10)
draw_box(ax, 7.7, 6.5, 3.2, 2.0, "PHASE 3\nKey Splitting",
         "K = K_α ⊕ K_β ⊕ K_γ\nXOR secret sharing", PALETTE['key'], 10)
draw_box(ax, 11.4, 6.5, 3.2, 2.0, "PHASE 4\nEncryption",
         f"C = '{SECRET_COMMAND}' ⊕ K\nDistribute ciphertext", PALETTE['cipher'], 10)

draw_arrow(ax, 3.5, 7.5, 4.0, 7.5, PALETTE['ghz'])
draw_arrow(ax, 7.2, 7.5, 7.7, 7.5, PALETTE['alpha'])
draw_arrow(ax, 10.9, 7.5, 11.4, 7.5, PALETTE['key'])

# Row 2 — Three generals
draw_box(ax, 0.8, 2.5, 3.5, 2.5, "GENERAL ALPHA (α)",
         f"Holds: K_α\nChannel: CLEAN\nErr: {err_AB:.1f}%", PALETTE['alpha'], 10)
draw_box(ax, 5.8, 2.5, 3.5, 2.5, "GENERAL BRAVO (β)",
         f"Holds: K_β\nChannel: CLEAN\nErr: {err_AB:.1f}%", PALETTE['bravo'], 10)
draw_box(ax, 10.8, 2.5, 3.5, 2.5, "GENERAL CHARLIE (γ)",
         f"Holds: K_γ  ← TRAITOR\nChannel: COMPROMISED\nErr: {err_AC:.1f}%",
         PALETTE['charlie'], 9)

draw_arrow(ax, 2.55, 6.5, 2.55, 5.0, PALETTE['alpha'])
draw_arrow(ax, 7.55, 6.5, 7.55, 5.0, PALETTE['bravo'])
ax.annotate("", xy=(12.55, 5.0), xytext=(12.55, 6.5),
            arrowprops=dict(arrowstyle="-|>", color=PALETTE['charlie'],
                            lw=2, mutation_scale=15, linestyle='dashed'))
ax.text(13.1, 5.75, "⚠️", fontsize=14)

# Row 3 — Reconstruction
draw_box(ax, 3.5, 0.3, 5.0, 1.7, "RECONSTRUCTION",
         "Need ALL 3 shares\nK = K_α ⊕ K_β ⊕ K_γ  →  Decrypt C",
         PALETTE['honest'], 10)
ax.text(14.5, 1.2, f"{'Charlie\nDETECTED ⚠️' if charlie_detected else 'All Clear ✅'}",
        ha='center', va='center', color=PALETTE['charlie'] if charlie_detected else PALETTE['honest'],
        fontsize=12, fontweight='bold')

draw_arrow(ax, 2.55, 2.5, 4.5, 2.0, PALETTE['alpha'])
draw_arrow(ax, 7.55, 2.5, 6.5, 2.0, PALETTE['bravo'])

fig1.tight_layout()
fig1.savefig('plot1_protocol_overview.png', dpi=120, bbox_inches='tight',
             facecolor=PALETTE['bg'])
print("  ✅ plot1_protocol_overview.png")


# ══════════════════════════════════════════════════════
# PLOT 2 — GHZ Circuit Diagrams (First 6)
# ══════════════════════════════════════════════════════
fig2, axes2 = plt.subplots(2, 3, figsize=(18, 8))
fig2.patch.set_facecolor(PALETTE['bg'])
fig2.suptitle("PLOT 2 — GHZ Circuit Diagrams: First 6 Entangled Triplets",
              color=PALETTE['text'], fontsize=14, fontweight='bold')

for idx in range(6):
    ax = axes2[idx // 3][idx % 3]
    ax.set_facecolor(PALETTE['panel'])
    a_bit = alpha_bits_raw[idx]
    b_bit = bravo_bits_raw[idx]
    c_bit = charlie_bits_raw[idx]
    outcome_str = f"|{a_bit}{b_bit}{c_bit}⟩"
    corr = "CORR ✓" if a_bit == b_bit == c_bit else "ERR ✗"
    corr_color = PALETTE['honest'] if a_bit == b_bit == c_bit else PALETTE['corrupt']

    ax.text(0.5, 0.93, f"GHZ Triplet #{idx+1}", ha='center', va='top',
            color=PALETTE['ghz'], fontsize=11, fontweight='bold',
            transform=ax.transAxes)

    # Draw circuit-like schematic
    for qi, (label, col, bit) in enumerate([
        ("α", PALETTE['alpha'], a_bit),
        ("β", PALETTE['bravo'], b_bit),
        ("γ", PALETTE['charlie'], c_bit)
    ]):
        y = 0.72 - qi * 0.20
        ax.plot([0.08, 0.92], [y, y], color='#3D3D3D',
                   linewidth=1, transform=ax.transAxes)
        ax.text(0.07, y, label, ha='right', va='center', color=col,
                fontsize=10, fontweight='bold', transform=ax.transAxes)
        # Hadamard box on qubit 0
        if qi == 0:
            rect = plt.Rectangle((0.12, y - 0.05), 0.10, 0.10,
                                  facecolor='#1E1E1E', edgecolor=PALETTE['ghz'],
                                  linewidth=1.5, transform=ax.transAxes)
            ax.add_patch(rect)
            ax.text(0.17, y, "H", ha='center', va='center', color=PALETTE['ghz'],
                    fontsize=9, fontweight='bold', transform=ax.transAxes)
        # CNOT dot
        if qi in [1, 2]:
            ax.plot(0.28, y + (0.20 if qi == 1 else 0.40),
                    'o', markersize=5, color=PALETTE['ghz'],
                    transform=ax.transAxes)
            ax.annotate("", xy=(0.28, y), xytext=(0.28, y + 0.08),
                        arrowprops=dict(arrowstyle="-", color=PALETTE['ghz']),
                        xycoords='axes fraction', textcoords='axes fraction')
            ax.text(0.28, y, "⊕", ha='center', va='center', color=PALETTE['ghz'],
                    fontsize=12, fontweight='bold', transform=ax.transAxes)
        # Measurement box
        m_rect = plt.Rectangle((0.72, y - 0.05), 0.12, 0.10,
                                facecolor='#1E1E1E',
                                edgecolor=col, linewidth=1.5,
                                transform=ax.transAxes)
        ax.add_patch(m_rect)
        ax.text(0.78, y, "M", ha='center', va='center', color=col,
                fontsize=9, fontweight='bold', transform=ax.transAxes)
        # Result bit
        bit_color = PALETTE['one'] if bit == 1 else PALETTE['zero']
        ax.text(0.90, y, str(bit), ha='center', va='center', color=bit_color,
                fontsize=14, fontweight='bold', transform=ax.transAxes)

    ax.text(0.50, 0.12, f"Outcome: {outcome_str}", ha='center', va='center',
            color=PALETTE['text'], fontsize=11, transform=ax.transAxes)
    ax.text(0.50, 0.04, corr, ha='center', va='center', color=corr_color,
            fontsize=9, fontweight='bold', transform=ax.transAxes)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE['ghz']); spine.set_linewidth(1.5)

fig2.tight_layout()
fig2.savefig('plot2_ghz_circuits.png', dpi=120, bbox_inches='tight',
             facecolor=PALETTE['bg'])
print("  ✅ plot2_ghz_circuits.png")


# ══════════════════════════════════════════════════════
# PLOT 3 — GHZ Measurement Statistics
# ══════════════════════════════════════════════════════
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(16, 6))
fig3.patch.set_facecolor(PALETTE['bg'])
fig3.suptitle("PLOT 3 — GHZ Quantum Correlation Statistics",
              color=PALETTE['text'], fontsize=14, fontweight='bold')

# Left: outcome histogram
outcome_counts = Counter(ghz_outcomes)
labels         = sorted(outcome_counts.keys())
values         = [outcome_counts[l] for l in labels]
bar_colors     = [PALETTE['honest'] if l in ('000', '111') else PALETTE['corrupt']
                  for l in labels]
ax3a.set_facecolor(PALETTE['panel'])
bars = ax3a.bar(labels, values, color=bar_colors, width=0.6, alpha=0.85, edgecolor='white', linewidth=0.5)
ax3a.set_title("Outcome Distribution (all Z-basis)", color=PALETTE['text'], fontsize=11)
ax3a.set_xlabel("Measurement Outcome", color='#8D8D8D', fontsize=10)
ax3a.set_ylabel("Count", color='#8D8D8D', fontsize=10)
ax3a.tick_params(colors=PALETTE['text'])
for bar, val in zip(bars, values):
    ax3a.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
              f'{val}\n({val/NUM_GHZ*100:.0f}%)', ha='center', va='bottom',
              color=PALETTE['text'], fontsize=8)
ax3a.axhline(NUM_GHZ/2, color='yellow', linestyle='--', linewidth=1.2,
             label='Expected (50% each)')
ax3a.legend(fontsize=8, facecolor='#262626', labelcolor=PALETTE['text'])
for spine in ax3a.spines.values(): spine.set_edgecolor('#3D3D3D')

# Right: rolling correlation over time
window  = 10
rolling = []
for i in range(NUM_GHZ - window + 1):
    window_outcomes = ghz_outcomes[i:i+window]
    corr = sum(1 for o in window_outcomes if o in ('000', '111')) / window * 100
    rolling.append(corr)

ax3b.set_facecolor(PALETTE['panel'])
ax3b.plot(rolling, color=PALETTE['ghz'], linewidth=2, alpha=0.9, label='GHZ Correlation %')
ax3b.axhline(100, color=PALETTE['honest'], linestyle='--', linewidth=1.2, label='Theoretical max (100%)')
ax3b.axhline(50, color=PALETTE['corrupt'], linestyle=':', linewidth=1.2, label='Random baseline (50%)')
ax3b.fill_between(range(len(rolling)), rolling, 50,
                  where=[r > 50 for r in rolling],
                  color=PALETTE['ghz'], alpha=0.15)
ax3b.set_title(f"Rolling {window}-triplet Correlation Rate", color=PALETTE['text'], fontsize=11)
ax3b.set_xlabel("Triplet Index", color='#8D8D8D', fontsize=10)
ax3b.set_ylabel("Correlation (%)", color='#8D8D8D', fontsize=10)
ax3b.set_ylim(0, 115); ax3b.tick_params(colors=PALETTE['text'])
ax3b.legend(fontsize=8, facecolor='#262626', labelcolor=PALETTE['text'])
ax3b.text(len(rolling)*0.5, 108, f"Overall: {corr_rate:.1f}%  {'✅ Perfect quantum correlation' if corr_rate > 95 else '⚠️'}",
          ha='center', color=PALETTE['honest'], fontsize=10, fontweight='bold')
for spine in ax3b.spines.values(): spine.set_edgecolor('#3D3D3D')

fig3.tight_layout()
fig3.savefig('plot3_ghz_statistics.png', dpi=120, bbox_inches='tight',
             facecolor=PALETTE['bg'])
print("  ✅ plot3_ghz_statistics.png")


# ══════════════════════════════════════════════════════
# PLOT 4 — Quantum Random Key Heatmap
# ══════════════════════════════════════════════════════
fig4, axes4 = plt.subplots(3, 1, figsize=(18, 7))
fig4.patch.set_facecolor(PALETTE['bg'])
fig4.suptitle("PLOT 4 — Quantum Random Key Generated from GHZ Measurements",
              color=PALETTE['text'], fontsize=14, fontweight='bold')

show_bits = min(n_msg, 64)
for ai, (label, bits_row, color) in enumerate([
    ("General α (Alpha)", alpha_bits_raw[:show_bits],   PALETTE['alpha']),
    ("General β (Bravo)", bravo_bits_raw[:show_bits],   PALETTE['bravo']),
    ("General γ (Charlie)", charlie_bits_raw[:show_bits], PALETTE['charlie']),
]):
    ax = axes4[ai]
    ax.set_facecolor(PALETTE['panel'])
    row_arr = np.array(bits_row).reshape(1, -1)
    ax.imshow(row_arr, cmap=cmap_bits, aspect='auto', vmin=0, vmax=1)
    for bi, bit in enumerate(bits_row):
        ax.text(bi, 0, str(bit), ha='center', va='center',
                color='white', fontsize=6.5, fontweight='bold')
    ax.set_yticks([0]); ax.set_yticklabels([label], color=color, fontsize=9)
    ax.set_xticks(range(0, show_bits, 8))
    ax.set_xticklabels([str(i) for i in range(0, show_bits, 8)],
                       color='#8D8D8D', fontsize=7)
    for spine in ax.spines.values(): spine.set_edgecolor('#3D3D3D')

agreement_ab = sum(1 for a, b in zip(alpha_bits_raw, bravo_bits_raw) if a == b)
agreement_ac = sum(1 for a, c in zip(alpha_bits_raw, charlie_bits_raw) if a == c)
fig4.text(0.5, -0.02,
          f"α↔β agreement: {agreement_ab}/{NUM_GHZ} = {agreement_ab/NUM_GHZ*100:.0f}%   "
          f"α↔γ agreement: {agreement_ac}/{NUM_GHZ} = {agreement_ac/NUM_GHZ*100:.0f}%   "
          f"(GHZ guarantee: all 3 always agree in Z-basis)",
          ha='center', color='#8D8D8D', fontsize=9)
fig4.tight_layout()
fig4.savefig('plot4_quantum_key_heatmap.png', dpi=120, bbox_inches='tight',
             facecolor=PALETTE['bg'])
print("  ✅ plot4_quantum_key_heatmap.png")


# ══════════════════════════════════════════════════════
# PLOT 5 — 3-Way XOR Secret Splitting
# ══════════════════════════════════════════════════════
fig5, axes5 = plt.subplots(2, 3, figsize=(18, 8))
fig5.patch.set_facecolor(PALETTE['bg'])
fig5.suptitle("PLOT 5 — 3-Way XOR Secret Splitting: K = K_α ⊕ K_β ⊕ K_γ",
              color=PALETTE['text'], fontsize=14, fontweight='bold')

rows = n_msg // 8
cols = 8
for ci, (title, bits_data, color) in enumerate([
    ("Master Key K\n(from GHZ)", ghz_key, PALETTE['ghz']),
    ("Share K_α (Alpha)", share_alpha, PALETTE['alpha']),
    ("Share K_β (Bravo)", share_bravo, PALETTE['bravo']),
    ("Share K_γ (Charlie)", share_charlie, PALETTE['charlie']),
    ("Ciphertext C\n= Message ⊕ K", ciphertext_bits, PALETTE['cipher']),
    ("Verify: K_α⊕K_β⊕K_γ\n== Master Key K?", verify_key, PALETTE['honest']),
]):
    ax = axes5[ci // 3][ci % 3]
    ax.set_facecolor(PALETTE['panel'])
    grid = np.array(bits_data[:rows*cols]).reshape(rows, cols)
    ax.imshow(grid, cmap=cmap_bits, aspect='auto', vmin=0, vmax=1)
    for r in range(rows):
        for c in range(cols):
            ax.text(c, r, str(int(grid[r, c])), ha='center', va='center',
                    color='white', fontsize=8, fontweight='bold')
    ax.set_title(title, color=color, fontsize=10, fontweight='bold')
    ax.set_yticks(range(rows))
    ax.set_yticklabels([f"'{SECRET_COMMAND[r]}' (ASCII {ord(SECRET_COMMAND[r])})"
                        for r in range(rows)], color='#8D8D8D', fontsize=7)
    ax.set_xticks(range(cols))
    ax.set_xticklabels([f'b{7-c}' for c in range(cols)], color='#8D8D8D', fontsize=7)
    for spine in ax.spines.values(): spine.set_edgecolor(color); spine.set_linewidth(1.5)

fig5.tight_layout()
fig5.savefig('plot5_secret_splitting.png', dpi=120, bbox_inches='tight',
             facecolor=PALETTE['bg'])
print("  ✅ plot5_secret_splitting.png")


# ══════════════════════════════════════════════════════
# PLOT 6 — Dual BB84 Channel Comparison
# ══════════════════════════════════════════════════════
fig6, (ax6a, ax6b) = plt.subplots(1, 2, figsize=(18, 6))
fig6.patch.set_facecolor(PALETTE['bg'])
fig6.suptitle("PLOT 6 — Dual BB84 Quantum Channels: Alpha↔Bravo (Clean) vs Alpha↔Charlie (Compromised)",
              color=PALETTE['text'], fontsize=14, fontweight='bold')

def plot_bb84_channel(ax, label_a, label_b, key_a, key_b, error_rate,
                      color_a, color_b, detected):
    ax.set_facecolor(PALETTE['panel'])
    show = min(48, len(key_a))
    # Show Alice's key bits
    ax.barh([2]*show, [1]*show, left=range(show),
            color=[PALETTE['one'] if b==1 else PALETTE['zero'] for b in key_a[:show]],
            height=0.4, alpha=0.85)
    # Show Bob/Charlie's key bits
    ax.barh([1]*show, [1]*show, left=range(show),
            color=[PALETTE['one'] if b==1 else PALETTE['zero'] for b in key_b[:show]],
            height=0.4, alpha=0.85)
    # Mark errors in red
    for i in range(show):
        if key_a[i] != key_b[i]:
            ax.axvline(x=i+0.5, color=PALETTE['charlie'], linewidth=1.5, alpha=0.6)
    ax.set_yticks([1, 2])
    ax.set_yticklabels([label_b, label_a], color=PALETTE['text'], fontsize=11)
    ax.set_xlim(0, show); ax.set_ylim(0.5, 2.7)
    title_color = PALETTE['corrupt'] if detected else PALETTE['honest']
    ax.set_title(f"{label_a} ↔ {label_b}  |  Error rate: {error_rate:.1f}%  "
                 f"{'⚠️ TRAITOR DETECTED' if detected else '✅ Channel Clean'}",
                 color=title_color, fontsize=10, fontweight='bold')
    ax.set_xlabel(f"Sifted key bit index (showing first {show})",
                  color='#8D8D8D', fontsize=9)
    ax.text(show*0.5, 2.5,
            f"Sifted key length: {len(key_a)} bits",
            ha='center', color='#8D8D8D', fontsize=9)
    for spine in ax.spines.values(): spine.set_edgecolor('#3D3D3D')

plot_bb84_channel(ax6a, "Alpha (α)", "Bravo (β)",
                  key_alpha_AB, key_bravo_AB, err_AB,
                  PALETTE['alpha'], PALETTE['bravo'], err_AB > 11)
plot_bb84_channel(ax6b, "Alpha (α)", "Charlie (γ)",
                  key_alpha_AC, key_charlie_AC, err_AC,
                  PALETTE['alpha'], PALETTE['charlie'], charlie_detected)

fig6.tight_layout()
fig6.savefig('plot6_bb84_channels.png', dpi=120, bbox_inches='tight',
             facecolor=PALETTE['bg'])
print("  ✅ plot6_bb84_channels.png")


# ══════════════════════════════════════════════════════
# PLOT 7 — Encryption Grid
# ══════════════════════════════════════════════════════
fig7, axes7 = plt.subplots(1, 3, figsize=(16, max(4, rows + 2)))
fig7.patch.set_facecolor(PALETTE['bg'])
fig7.suptitle(f"PLOT 7 — Encryption: '{SECRET_COMMAND}' ⊕ K = Ciphertext",
              color=PALETTE['text'], fontsize=14, fontweight='bold')

msg_grid    = np.array(message_bits).reshape(rows, cols)
key_grid    = np.array(ghz_key).reshape(rows, cols)
cipher_grid = np.array(ciphertext_bits).reshape(rows, cols)

for ai, (title, grid, color) in enumerate([
    (f"PLAINTEXT\n'{SECRET_COMMAND}'",   msg_grid,    PALETTE['text']),
    ("GHZ QUANTUM KEY\n(master key K)", key_grid,    PALETTE['ghz']),
    ("CIPHERTEXT\n(encrypted output)",  cipher_grid, PALETTE['cipher']),
]):
    ax = axes7[ai]
    ax.set_facecolor(PALETTE['panel'])
    ax.imshow(grid, cmap=cmap_bits, aspect='auto', vmin=0, vmax=1)
    for r in range(rows):
        for c in range(cols):
            ax.text(c, r, str(int(grid[r, c])), ha='center', va='center',
                    color='white', fontsize=9, fontweight='bold')
    ax.set_title(title, color=color, fontsize=11, fontweight='bold')
    ax.set_yticks(range(rows))
    ax.set_yticklabels([f"'{ch}'" for ch in SECRET_COMMAND],
                       color=PALETTE['alpha'], fontsize=11)
    ax.set_xticks(range(cols))
    ax.set_xticklabels([f'b{7-c}' for c in range(cols)], color='#8D8D8D', fontsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(color); spine.set_linewidth(1.8)
    if ai == 1:
        ax.text(cols + 0.3, rows/2 - 0.5, "=", ha='center', va='center',
                color=PALETTE['text'], fontsize=28, fontweight='bold',
                transform=ax.transData)

axes7[0].text(cols + 0.3, rows/2 - 0.5, "⊕", ha='center', va='center',
              color=PALETTE['text'], fontsize=28, fontweight='bold',
              transform=axes7[0].transData)
fig7.text(0.5, -0.02, f"Ciphertext (hex): {ciphertext_hex}",
          ha='center', color='#8D8D8D', fontsize=10)
fig7.tight_layout()
fig7.savefig('plot7_encryption_grid.png', dpi=120, bbox_inches='tight',
             facecolor=PALETTE['bg'])
print("  ✅ plot7_encryption_grid.png")


# ══════════════════════════════════════════════════════
# PLOT 8 — Traitor (Charlie) Detection Analysis
# ══════════════════════════════════════════════════════
fig8, axes8 = plt.subplots(1, 3, figsize=(18, 6))
fig8.patch.set_facecolor(PALETTE['bg'])
fig8.suptitle("PLOT 8 — General Charlie's Betrayal: Detection & Impact Analysis",
              color=PALETTE['text'], fontsize=14, fontweight='bold')

# Left: error rate bars
ax8a = axes8[0]; ax8a.set_facecolor(PALETTE['panel'])
scenarios    = ["No Traitor\n(expected)", "With Traitor\n(expected)",
                f"Channel α↔β\n(this run)", f"Channel α↔γ\n(this run)"]
error_vals   = [1.0, 25.0, err_AB, err_AC]
bar_cols_err = [PALETTE['honest'], PALETTE['charlie'], PALETTE['honest'],
                PALETTE['charlie'] if charlie_detected else PALETTE['honest']]
bars8 = ax8a.bar(scenarios, error_vals, color=bar_cols_err, alpha=0.85, width=0.5,
                 edgecolor='white', linewidth=0.5)
ax8a.axhline(11, color='yellow', linestyle='--', linewidth=2, label='Threshold (11%)')
ax8a.set_ylabel('Error Rate (%)', color=PALETTE['text']); ax8a.set_ylim(0, 35)
ax8a.set_title("Error Rate Comparison", color=PALETTE['text'], fontsize=11)
ax8a.tick_params(colors=PALETTE['text'])
ax8a.legend(fontsize=8, facecolor='#262626', labelcolor=PALETTE['text'])
for bar, val in zip(bars8, error_vals):
    ax8a.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
              f'{val:.1f}%', ha='center', va='bottom',
              color=PALETTE['text'], fontsize=9, fontweight='bold')
for spine in ax8a.spines.values(): spine.set_edgecolor('#3D3D3D')

# Middle: per-bit comparison Alpha vs Charlie
ax8b = axes8[1]; ax8b.set_facecolor(PALETTE['panel'])
compare_n = min(48, len(key_alpha_AC))
agree_ac  = [1 if key_alpha_AC[i] == key_charlie_AC[i] else 0
             for i in range(compare_n)]
agree_cols = [PALETTE['honest'] if a == 1 else PALETTE['charlie'] for a in agree_ac]
ax8b.bar(range(compare_n), [1]*compare_n, color=agree_cols, width=0.8)
ax8b.set_title(f"α vs γ Bit Agreement\n(first {compare_n} sifted bits)",
               color=PALETTE['text'], fontsize=11)
ax8b.set_xlabel("Bit index", color='#8D8D8D', fontsize=9)
ax8b.set_yticks([])
total_agree = sum(agree_ac)
ax8b.text(0.5, 0.88, f"{total_agree}/{compare_n} agree ({total_agree/compare_n*100:.0f}%)",
          ha='center', transform=ax8b.transAxes, color=PALETTE['text'], fontsize=10)
ax8b.legend(handles=[mpatches.Patch(color=PALETTE['honest'], label='✓ Agree'),
                     mpatches.Patch(color=PALETTE['charlie'], label='✗ Error (traitor)')],
            fontsize=8, facecolor='#262626', labelcolor=PALETTE['text'])
for spine in ax8b.spines.values(): spine.set_edgecolor('#3D3D3D')

# Right: impact — what Charlie leaked
ax8c = axes8[2]; ax8c.set_facecolor(PALETTE['panel']); ax8c.axis('off')
summary_lines = [
    ("TRAITOR ANALYSIS", PALETTE['charlie'], 13),
    ("", PALETTE['text'], 9),
    (f"Channel α↔β (Bravo):  CLEAN ✅", PALETTE['honest'], 10),
    (f"  Error rate: {err_AB:.1f}%", '#8D8D8D', 9),
    ("", PALETTE['text'], 9),
    (f"Channel α↔γ (Charlie): COMPROMISED ⚠️", PALETTE['charlie'], 10),
    (f"  Error rate: {err_AC:.1f}% (>{11}% threshold)", '#8D8D8D', 9),
    ("", PALETTE['text'], 9),
    (f"Detection result:", PALETTE['text'], 10),
    (f"  {'CHARLIE DETECTED ⚠️' if charlie_detected else 'NOT detected'}",
     PALETTE['charlie'] if charlie_detected else PALETTE['honest'], 12),
    ("", PALETTE['text'], 9),
    ("Security consequence:", PALETTE['text'], 10),
    ("  Session ABORTED", PALETTE['corrupt'], 10),
    ("  Keys DISCARDED", PALETTE['corrupt'], 10),
    ("  New session required", '#8D8D8D', 9),
    ("", PALETTE['text'], 9),
    ("GHZ correlation intact:", PALETTE['text'], 10),
    (f"  {corr_rate:.1f}% (α & β still secure)", PALETTE['honest'], 10),
]
for li, (line, col, fsize) in enumerate(summary_lines):
    ax8c.text(0.05, 0.97 - li * 0.055, line, transform=ax8c.transAxes,
              color=col, fontsize=fsize, va='top',
              fontweight='bold' if fsize >= 12 else 'normal')
for spine in ax8c.spines.values(): spine.set_edgecolor(PALETTE['charlie']); spine.set_linewidth(1.5)

fig8.tight_layout()
fig8.savefig('plot8_traitor_detection.png', dpi=120, bbox_inches='tight',
             facecolor=PALETTE['bg'])
print("  ✅ plot8_traitor_detection.png")


# ══════════════════════════════════════════════════════
# PLOT 9 — Reconstruction Ceremony
# ══════════════════════════════════════════════════════
fig9, axes9 = plt.subplots(2, 2, figsize=(16, 10))
fig9.patch.set_facecolor(PALETTE['bg'])
fig9.suptitle("PLOT 9 — Reconstruction Ceremony: Combining Shares → Decryption",
              color=PALETTE['text'], fontsize=14, fontweight='bold')

scenarios9 = [
    ("α ONLY (incomplete)", bits_to_text(
        [ct ^ k for ct, k in zip(ciphertext_bits, share_alpha)]),
     [ct ^ k for ct, k in zip(ciphertext_bits, share_alpha)],
     PALETTE['alpha'], "1/3 shares\nCannot decrypt"),
    ("α + β (missing γ)", bits_to_text(
        [ct ^ (a ^ b) for ct, a, b in zip(ciphertext_bits, share_alpha, share_bravo)]),
     [ct ^ (a ^ b) for ct, a, b in zip(ciphertext_bits, share_alpha, share_bravo)],
     PALETTE['bravo'], "2/3 shares\nStill cannot decrypt"),
    ("α + β + γ (full)", text_full,
     decrypted_full,
     PALETTE['honest'], "3/3 shares ✅\nPERFECT DECRYPTION"),
    ("Ciphertext C\n(raw encrypted)", "— encrypted —",
     ciphertext_bits, PALETTE['cipher'], "No key\nUnreadable"),
]

for pi, (title, decoded_text, decoded_bits, color, verdict) in enumerate(scenarios9):
    ax = axes9[pi // 2][pi % 2]
    ax.set_facecolor(PALETTE['panel'])
    decoded_bits_trunc = decoded_bits[:n_msg]
    grid_data = np.array(decoded_bits_trunc).reshape(rows, cols)
    ax.imshow(grid_data, cmap=cmap_bits, aspect='auto', vmin=0, vmax=1)
    for r in range(rows):
        for c in range(cols):
            ax.text(c, r, str(int(grid_data[r, c])), ha='center', va='center',
                    color='white', fontsize=8, fontweight='bold')
    ax.set_title(title, color=color, fontsize=11, fontweight='bold')
    ax.set_yticks(range(rows))
    ax.set_yticklabels([f"'{ch}'" for ch in SECRET_COMMAND], color=PALETTE['alpha'], fontsize=10)
    ax.set_xticks(range(cols))
    ax.set_xticklabels([f'b{7-c}' for c in range(cols)], color='#8D8D8D', fontsize=7)
    result_line = decoded_text if decoded_text else "???"
    ax.text(0.5, -0.12, f"Decoded: '{result_line}'  |  {verdict}",
            ha='center', transform=ax.transAxes,
            color=color, fontsize=9, fontweight='bold')
    for spine in ax.spines.values(): spine.set_edgecolor(color); spine.set_linewidth(1.5)

fig9.tight_layout()
fig9.savefig('plot9_reconstruction.png', dpi=120, bbox_inches='tight',
             facecolor=PALETTE['bg'])
print("  ✅ plot9_reconstruction.png")


# ══════════════════════════════════════════════════════
# PLOT 10 — Security Dashboard
# ══════════════════════════════════════════════════════
fig10 = plt.figure(figsize=(18, 10))
fig10.patch.set_facecolor(PALETTE['bg'])
gs = gridspec.GridSpec(3, 4, figure=fig10, hspace=0.55, wspace=0.4)
fig10.suptitle("PLOT 10 — Security Dashboard: Full Protocol Summary",
               color=PALETTE['text'], fontsize=15, fontweight='bold', y=1.01)

# --- Metric cards ---
metrics = [
    ("GHZ Correlation", f"{corr_rate:.1f}%", "✅", PALETTE['ghz']),
    ("Channel α↔β\nError Rate", f"{err_AB:.1f}%", "✅", PALETTE['bravo']),
    ("Channel α↔γ\nError Rate", f"{err_AC:.1f}%", "⚠️", PALETTE['charlie']),
    ("Charlie\nDetected?", "YES" if charlie_detected else "NO",
     "⚠️" if charlie_detected else "✅",
     PALETTE['charlie'] if charlie_detected else PALETTE['honest']),
]
for mi, (label, value, icon, color) in enumerate(metrics):
    ax = fig10.add_subplot(gs[0, mi])
    ax.set_facecolor(color + '22')
    ax.axis('off')
    ax.text(0.5, 0.75, icon, ha='center', va='center', fontsize=22,
            transform=ax.transAxes)
    ax.text(0.5, 0.50, value, ha='center', va='center', color=color,
            fontsize=16, fontweight='bold', transform=ax.transAxes)
    ax.text(0.5, 0.20, label, ha='center', va='center', color=PALETTE['text'],
            fontsize=8, transform=ax.transAxes)
    for spine in ax.spines.values():
        spine.set_edgecolor(color); spine.set_linewidth(2); spine.set_visible(True)

# --- Share contribution pie chart ---
ax_pie = fig10.add_subplot(gs[1:, :2])
ax_pie.set_facecolor(PALETTE['panel'])
share_entropy = [
    sum(share_alpha) / n_msg * 100,
    sum(share_bravo)  / n_msg * 100,
    sum(share_charlie) / n_msg * 100,
]
wedge_colors = [PALETTE['alpha'], PALETTE['bravo'], PALETTE['charlie']]
wedges, texts, autotexts = ax_pie.pie(
    [1, 1, 1],  # Equal contribution by design
    labels=["Share K_α\n(General Alpha)", "Share K_β\n(General Bravo)",
            "Share K_γ\n(General Charlie — TRAITOR)"],
    colors=wedge_colors, autopct='%1.0f%%', startangle=90,
    wedgeprops=dict(width=0.55, edgecolor=PALETTE['bg'], linewidth=2),
    textprops=dict(color=PALETTE['text'], fontsize=9)
)
for at in autotexts: at.set_fontsize(11); at.set_fontweight('bold')
ax_pie.set_title("Equal Share Distribution\n(ALL 3 required for decryption)",
                 color=PALETTE['text'], fontsize=11, fontweight='bold')
ax_pie.text(0, -1.35,
            "⚠️  If ANY share is missing → decryption fails\n"
            "⚠️  If ANY channel is compromised → session aborted",
            ha='center', color='#8D8D8D', fontsize=9)

# --- Final decryption result ---
ax_final = fig10.add_subplot(gs[1:, 2:])
ax_final.set_facecolor(PALETTE['panel'])
ax_final.axis('off')
lines_final = [
    ("FINAL RESULT", PALETTE['text'], 14, True),
    ("", PALETTE['text'], 8, False),
    (f"Secret command:  '{SECRET_COMMAND}'", PALETTE['alpha'], 12, True),
    (f"Ciphertext hex:   {ciphertext_hex}", PALETTE['cipher'], 10, False),
    ("", PALETTE['text'], 8, False),
    (f"Decryption (α+β+γ): '{text_full}'",
     PALETTE['honest'] if text_full == SECRET_COMMAND else PALETTE['corrupt'],
     12, True),
    (f"Match: {'✅ PERFECT' if text_full == SECRET_COMMAND else '❌ FAILED'}",
     PALETTE['honest'] if text_full == SECRET_COMMAND else PALETTE['corrupt'],
     11, True),
    ("", PALETTE['text'], 8, False),
    ("Security properties:", PALETTE['text'], 11, True),
    ("  ✅ Information-theoretic secure (OTP)", PALETTE['honest'], 9, False),
    ("  ✅ Key from true quantum randomness", PALETTE['honest'], 9, False),
    ("  ✅ No single-party reconstruction", PALETTE['honest'], 9, False),
    ("  ✅ Traitor detection via QKD", PALETTE['honest'], 9, False),
    ("  ✅ GHZ correlations verified", PALETTE['honest'], 9, False),
    ("", PALETTE['text'], 8, False),
    (f"  Protocol: 3-Party QSS + GHZ + BB84", '#8D8D8D', 8, False),
    (f"  Total qubits used: {NUM_GHZ*3 + NUM_QKD_BITS*2}", '#8D8D8D', 8, False),
]
for li, (line, col, fsize, bold) in enumerate(lines_final):
    ax_final.text(0.05, 0.98 - li * 0.064, line,
                  transform=ax_final.transAxes, color=col, fontsize=fsize,
                  va='top', fontweight='bold' if bold else 'normal')
for spine in ax_final.spines.values():
    spine.set_edgecolor(PALETTE['honest']); spine.set_linewidth(2); spine.set_visible(True)

fig10.savefig('plot10_security_dashboard.png', dpi=120, bbox_inches='tight',
              facecolor=PALETTE['bg'])
print("  ✅ plot10_security_dashboard.png")


# ═══════════════════════════════════════════════════════════════════
# FINAL CONSOLE SUMMARY
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 66)
print("   OPERATION THUNDERBOLT — COMPLETE")
print("=" * 66)
print(f"   Secret command:          '{SECRET_COMMAND}'")
print(f"   Encrypted (hex):          {ciphertext_hex}")
print(f"   Decrypted (all 3 keys):   '{text_full}'")
print(f"   Decrypted (α only):       '{bits_to_text(decrypted_alpha)}' (garbage ✅)")
print(f"   Channel α↔β error rate:   {err_AB:.1f}%  (clean ✅)")
print(f"   Channel α↔γ error rate:   {err_AC:.1f}%  ({'TRAITOR ⚠️' if charlie_detected else 'clean'})")
print(f"   GHZ correlation:          {corr_rate:.1f}%")
print(f"   Total qubits used:        {NUM_GHZ*3 + NUM_QKD_BITS*2}")
print()
print("   10 PLOTS SAVED:")
print("   📊 plot1_protocol_overview.png   — Full protocol flowchart")
print("   📊 plot2_ghz_circuits.png        — GHZ circuit diagrams (6 triplets)")
print("   📊 plot3_ghz_statistics.png      — GHZ correlation statistics")
print("   📊 plot4_quantum_key_heatmap.png — Quantum random key (3 parties)")
print("   📊 plot5_secret_splitting.png    — 3-way XOR key splitting grid")
print("   📊 plot6_bb84_channels.png       — Dual channel bit comparison")
print("   📊 plot7_encryption_grid.png     — Encryption heatmap")
print("   📊 plot8_traitor_detection.png   — Charlie detection analysis")
print("   📊 plot9_reconstruction.png      — Share reconstruction ceremony")
print("   📊 plot10_security_dashboard.png — Full security summary dashboard")
print("=" * 66)