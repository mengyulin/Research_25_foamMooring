
import matplotlib.pyplot as plt
import numpy as np

# 輸入波浪參數與水槽長度
waveHeight     = 0.02      # 波高 (m)
wavePeriod     = 0.903     # 波週期 (s)
waveLength     = 1.2566    # 波長 (m)
wavePhaseDeg   = 0.0       # Incident wave phase φ_η (deg) at the body reference; 0 means η(t)=a cos(ωt)
tankLength     = 10.0      # 水槽長度 (固定值) (m)
bodyHalfWidth  = 0.1       # 浮體半寬度 (固定值) (m)
coM            = -0.0126   # 浮體重心位置 (固定值) (m)

(time, surge, ymotion, heave) = np.loadtxt('./Plots/logs/t_vs_CoM', unpack=True)
(time2, y1, y2, y3, y4, y5, y6, y7, y8, y9) = np.loadtxt('./Plots/logs/t_vs_orientation', unpack=True)

# Pitch (deg) reconstructed from rotation matrix using atan2 for signed, continuous angle.
# Assume y1..y9 correspond to rotation matrix R in row-major order:
# R = [[y1, y2, y3],
#      [y4, y5, y6],
#      [y7, y8, y9]]
R11, R21, R31 = y1, y4, y7
pitch_rad = np.arctan2(-R31, np.sqrt(R11**2 + R21**2))  # ZYX convention
pitch_deg = np.degrees(pitch_rad)

heave = heave - coM  # Adjust heave to body reference point at z=0

#========================================================================================
#========================================================================================
#========================================================================================


# === Configuration for steady-state detection ===
# STEADY_CYCLES = number of cycles to use for FFT (always take the last N cycles).
# We still detect the steady-state start, but if the steady segment contains more than N cycles,
# we only use the *last* N cycles for FFT. If fewer, use whatever is available in the steady segment.
STEADY_CYCLES = 3   # e.g., 6 for last 6 cycles
RMS_TOL = 0.05         # 5% relative change threshold between consecutive windows
CONSEC_WINDOWS = 3     # require this many consecutive windows to satisfy tolerance
CYCLES_PER_WINDOW = 1.0
HOP_FRAC = 0.25        # hop = HOP_FRAC * window_length

def _rms(x: np.ndarray) -> float:
    x = np.asarray(x)
    if x.size == 0:
        return 0.0
    x = x - x.mean()
    return float(np.sqrt(np.mean(x * x)))

def dominant_frequency_estimate(time, signal):
    """Coarse dominant frequency estimate from the whole record (robust to small
    transients). Returns f_peak (Hz) or 0.0 if not resolvable.
    """
    time = np.asarray(time).ravel()
    signal = np.asarray(signal).ravel()
    if time.size < 2 or signal.size < 2:
        return 0.0
    dt = float(np.median(np.diff(time)))
    N = signal.size
    x = signal - np.mean(signal)
    w = np.hanning(N)
    cg = w.mean() if w.mean() != 0 else 1.0
    X = np.fft.rfft(x * w)
    freq = np.fft.rfftfreq(N, dt)
    amp = (2.0 / (N * cg)) * np.abs(X)
    if amp.size <= 1:
        return 0.0
    idx_peak = int(np.argmax(amp[1:])) + 1
    return float(freq[idx_peak])

def find_steady_segment(time, signal, f_est,
                        rms_tol=RMS_TOL,
                        cycles_per_window=CYCLES_PER_WINDOW,
                        hop_frac=HOP_FRAC,
                        consecutive=CONSEC_WINDOWS):
    """Return (t_ss, idx_ss): steady-state start time/index using sliding RMS.
    We slide a window of ~ one period and look for `consecutive` windows whose
    RMS changes by less than `rms_tol`.
    If detection fails, return the original start.
    """
    time = np.asarray(time).ravel()
    signal = np.asarray(signal).ravel()
    if time.size < 4 or f_est <= 0:
        return time[0], 0
    dt = float(np.median(np.diff(time)))
    T = 1.0 / f_est
    win_len = max(4, int(round(cycles_per_window * T / dt)))
    hop = max(1, int(round(hop_frac * win_len)))
    N = signal.size
    # Guard: if window bigger than data, bail out
    if win_len >= N:
        return time[0], 0
    # Precompute window RMS along the record
    rms_vals = []
    starts = []
    for start in range(0, N - win_len + 1, hop):
        seg = signal[start:start + win_len]
        rms_vals.append(_rms(seg))
        starts.append(start)
    # Look for `consecutive` windows meeting tolerance
    for k in range(consecutive, len(rms_vals)):
        ok = True
        for j in range(k - consecutive + 1, k + 1):
            r0 = rms_vals[j - 1]
            r1 = rms_vals[j]
            denom = max(abs(r0), 1e-16)
            if abs(r1 - r0) / denom > rms_tol:
                ok = False
                break
        if ok:
            idx_ss = starts[k - consecutive + 1]
            return time[idx_ss], idx_ss
    # Fallback: no steady region found
    return time[0], 0

def trim_to_n_cycles_from_end(time, signal, f, n_cycles):
    """Trim arrays to the last n_cycles based on frequency f (Hz)."""
    if f <= 0:
        return time, signal
    T = 1.0 / f
    t_end = time[-1]
    t_start = t_end - n_cycles * T
    mask = time >= t_start
    return time[mask], signal[mask]

# === Fit main-frequency sinusoid for overlay ===
def fit_main_sinusoid(time, signal, f, use_steady=True):
    """Least-squares fit of a sinusoid at frequency f to (time, signal).
    Model: y(t) ≈ c + a*cos(2π f t) + b*sin(2π f t)
    Returns (y_hat_full, idx_ss, amplitude, phase), where phase φ satisfies
    R*cos(2π f t - φ) with R = sqrt(a^2+b^2) and φ = atan2(b, a).
    If use_steady is True, the fit is done over the detected steady segment
    (same criteria as FFT steady-state) and then evaluated on the *full* time
    vector so it can be overlaid for comparison.
    """
    time = np.asarray(time).ravel()
    signal = np.asarray(signal).ravel()
    if time.size < 2 or signal.size < 2:
        return np.full_like(time, np.nan, dtype=float), 0, 0.0, 0.0
    f_use = float(f) if f and f > 0 else dominant_frequency_estimate(time, signal)
    idx_ss = 0
    if use_steady and f_use > 0:
        _, idx_ss = find_steady_segment(time, signal, f_use)
    t_fit = time[idx_ss:]
    y_fit = signal[idx_ss:]
    if t_fit.size < 2:
        return np.full_like(time, np.nan, dtype=float), 0, 0.0, 0.0
    w = 2.0 * np.pi * f_use
    C = np.cos(w * t_fit)
    S = np.sin(w * t_fit)
    # Design matrix: [1, cos, sin]
    M = np.column_stack([np.ones_like(t_fit), C, S])
    coeffs, *_ = np.linalg.lstsq(M, y_fit, rcond=None)
    c, a, b = coeffs
    R = float(np.sqrt(a*a + b*b))
    phi = float(np.arctan2(b, a))  # y ≈ c + R*cos(w t - phi)
    # Evaluate on full time for overlay
    y_hat_full = c + a*np.cos(w * time) + b*np.sin(w * time)
    return y_hat_full, idx_ss, R, phi

# === Helper functions ===
def compute_fft(time, signal):
    """Compute single-sided amplitude spectrum with Hann window and return
    (freq, amp, f_peak, amp_peak). The amplitude is in the same units as the
    input signal (m or deg). DC is handled separately.
    """
    # Ensure 1D arrays
    time = np.asarray(time).ravel()
    signal = np.asarray(signal).ravel()

    # Guard: need at least 2 samples
    if time.size < 2 or signal.size < 2:
        return np.array([0.0]), np.array([0.0]), 0.0, 0.0

    # Uniform dt from median to be robust to tiny jitter
    dt = float(np.median(np.diff(time)))
    fs = 1.0 / dt
    N = signal.size

    # Detrend (remove mean) + Hann window
    x = signal - np.mean(signal)
    w = np.hanning(N)
    cg = w.mean() if w.mean() != 0 else 1.0  # coherent gain of window
    xw = x * w

    # rFFT and single-sided amplitude spectrum
    X = np.fft.rfft(xw)
    freq = np.fft.rfftfreq(N, dt)

    amp = (2.0 / (N * cg)) * np.abs(X)
    # Correct DC term (no doubling)
    if amp.size > 0:
        amp[0] = np.abs(X[0]) / (N * cg)

    # Identify dominant peak excluding DC
    if amp.size > 1:
        idx_peak = int(np.argmax(amp[1:])) + 1
    else:
        idx_peak = 0
    f_peak = float(freq[idx_peak]) if freq.size else 0.0
    amp_peak = float(amp[idx_peak]) if amp.size else 0.0

    # === Steady-state detection and enforced last-N-cycles trimming ===
    # 1) Coarse frequency from the whole record (robust to early transients)
    f_coarse = f_peak if f_peak > 0 else dominant_frequency_estimate(time, signal)

    # 2) Find steady start using sliding RMS over ~1 period
    t_ss, idx_ss = find_steady_segment(time, signal, f_coarse)
    time_ss = time[idx_ss:]
    sig_ss  = signal[idx_ss:]

    # 3) Choose a reference frequency for trimming
    f_ref = f_coarse
    if not (isinstance(f_ref, (int, float)) and f_ref > 0):
        try:
            f_ref = 1.0 / float(wavePeriod)  # fall back to theoretical frequency if available
        except Exception:
            f_ref = dominant_frequency_estimate(time_ss if time_ss.size >= 2 else time, signal)

    # 4) Always trim to the last STEADY_CYCLES cycles within the steady segment when possible
    time_fft = time_ss
    sig_fft  = sig_ss
    if isinstance(STEADY_CYCLES, (int, float)) and STEADY_CYCLES and f_ref > 0:
        # If steady segment exists, take last N cycles from it; otherwise fall back to whole record
        base_time = time_ss if time_ss.size >= 2 else time
        base_sig  = sig_ss  if time_ss.size >= 2 else signal
        time_trim, sig_trim = trim_to_n_cycles_from_end(base_time, base_sig, f_ref, int(STEADY_CYCLES))
        if time_trim.size >= 2:
            time_fft, sig_fft = time_trim, sig_trim

    # 5) Recompute FFT on the selected segment (trimmed or steady)
    if time_fft.size >= 2:
        dt_trim = float(np.median(np.diff(time_fft)))
        N_trim = sig_fft.size
        x_trim = sig_fft - np.mean(sig_fft)
        w_trim = np.hanning(N_trim)
        cg_trim = w_trim.mean() if w_trim.mean() != 0 else 1.0
        X_trim = np.fft.rfft(x_trim * w_trim)
        freq_trim = np.fft.rfftfreq(N_trim, dt_trim)
        amp_trim = (2.0 / (N_trim * cg_trim)) * np.abs(X_trim)
        if amp_trim.size > 0:
            amp_trim[0] = np.abs(X_trim[0]) / (N_trim * cg_trim)
        if amp_trim.size > 1:
            idx_peak_trim = int(np.argmax(amp_trim[1:])) + 1
        else:
            idx_peak_trim = 0
        f_peak = float(freq_trim[idx_peak_trim]) if freq_trim.size else 0.0
        amp_peak = float(amp_trim[idx_peak_trim]) if amp_trim.size else 0.0
        freq = freq_trim
        amp = amp_trim

    return freq, amp, f_peak, amp_peak


def annotate_peak(ax, f_peak, amp_peak, unit):
    ax.axvline(f_peak, linestyle='--', linewidth=1)
    ax.annotate(
        f"f₁ = {f_peak:.4g} Hz\nA₁ = {amp_peak:.4g} {unit}",
        xy=(f_peak, amp_peak), xytext=(5, 10), textcoords='offset points',
        arrowprops=dict(arrowstyle='->', lw=1), fontsize=8
    )


# === Time histories ===
fig1, (ax11, ax12, ax13) = plt.subplots(3, 1, dpi=300, layout='constrained')

ax11.plot(time, surge, linewidth=1)
ax11.set_xlabel('Time (s)')
ax11.set_ylabel('Surge (m)')
ax11.set_xlim(time.min(), time.max())
ax11.set_title('Surge')
ax11.grid(True, linewidth=0.3)

ax12.plot(time, heave, linewidth=1)
ax12.set_xlabel('Time (s)')
ax12.set_ylabel('Heave (m)')
ax12.set_xlim(time.min(), time.max())
ax12.set_title('Heave')
ax12.grid(True, linewidth=0.3)

ax13.plot(time2, pitch_deg, linewidth=1)
ax13.set_xlabel('Time (s)')
ax13.set_ylabel('Pitch (deg)')
ax13.set_xlim(time2.min(), time2.max())
ax13.set_title('Pitch')
ax13.grid(True, linewidth=0.3)


# === FFTs ===
freq_surge, amp_surge, f1_surge, A1_surge = compute_fft(time, surge)
freq_heave, amp_heave, f1_heave, A1_heave = compute_fft(time, heave)
freq_pitch, amp_pitch, f1_pitch, A1_pitch = compute_fft(time2, pitch_deg)

# === Overlay main-frequency sinusoid on time histories using theoretical frequency (1/T) ===
f_theory = 1.0 / float(wavePeriod)

yhat_surge, i_ss_surge, R_surge, phi_surge = fit_main_sinusoid(time, surge, f_theory, use_steady=True)
if np.isfinite(yhat_surge).any():
    ax11.plot(time[i_ss_surge:], yhat_surge[i_ss_surge:], linestyle='--', linewidth=1)

yhat_heave, i_ss_heave, R_heave, phi_heave = fit_main_sinusoid(time, heave, f_theory, use_steady=True)
if np.isfinite(yhat_heave).any():
    ax12.plot(time[i_ss_heave:], yhat_heave[i_ss_heave:], linestyle='--', linewidth=1)

yhat_pitch, i_ss_pitch, R_pitch, phi_pitch = fit_main_sinusoid(time2, pitch_deg, f_theory, use_steady=True)
if np.isfinite(yhat_pitch).any():
    ax13.plot(time2[i_ss_pitch:], yhat_pitch[i_ss_pitch:], linestyle='--', linewidth=1)

# === RAO computation (single case) ===
# Use incident Stokes II fundamental amplitude a = H/2 as normalization
inc_amp = 0.5 * float(waveHeight)
inc_phase = np.deg2rad(float(wavePhaseDeg))  # reference η(t)=a cos(ωt - φ_η)

# Guard for zero/near-zero incident amplitude
if inc_amp <= 0:
    print("[RAO] Warning: incident amplitude is non-positive; cannot compute RAO.")
    rao_surge_mag = rao_heave_mag = rao_pitch_mag = np.nan
    rao_surge_phase = rao_heave_phase = rao_pitch_phase = np.nan
else:
    # Convert pitch amplitude to radians for RAO (rad/m)
    R_pitch_rad = np.deg2rad(R_pitch)

    rao_surge_mag = R_surge / inc_amp              # m/m
    rao_heave_mag = R_heave / inc_amp              # m/m
    rao_pitch_mag = R_pitch_rad / inc_amp          # rad/m

    # Phase of RAO = φ_resp - φ_eta
    rao_surge_phase = np.degrees(phi_surge - inc_phase)
    rao_heave_phase = np.degrees(phi_heave - inc_phase)
    rao_pitch_phase = np.degrees(phi_pitch - inc_phase)

# Frequencies for reference
f_incident = 1.0 / float(wavePeriod)

# Print RAO summary
print("\n[RAO] Results (surge and heave are normalized by a = H/2, pitch is normalized by a/b):")
print(f"  Incident: H = {waveHeight:.6g} m, a = {inc_amp:.6g} m, T = {wavePeriod:.6g} s, f = {f_incident:.6g} Hz, φ_η = {wavePhaseDeg:.3f} deg")
print(f"  Surge : |RAO| = {rao_surge_mag:.6g} m/m,  ∠RAO = {rao_surge_phase:.3f} deg  (fit amp = {R_surge:.6g} m)")
print(f"  Heave : |RAO| = {rao_heave_mag:.6g} m/m,  ∠RAO = {rao_heave_phase:.3f} deg  (fit amp = {R_heave:.6g} m)")
print(f"  Pitch : |RAO| = {rao_pitch_mag*bodyHalfWidth:.6g} m/m, ∠RAO = {rao_pitch_phase:.3f} deg  (fit amp = {R_pitch:.6g} deg)")

# === RAO frequency check: measured (steady dominant) vs theory (1/T) ===
print("\n[RAO] Frequency check (steady dominant vs theory 1/T):")
f_theory = 1.0 / float(wavePeriod)

def _freq_check(label, f_meas, f_ref):
    if f_meas is None or not np.isfinite(f_meas) or f_meas <= 0:
        print(f"  {label}: f_meas unavailable")
        return
    df = f_meas - f_ref
    rel = abs(df) / f_ref * 100.0 if f_ref > 0 else np.nan
    print(f"  {label}: f_meas = {f_meas:.6g} Hz  |  f_theory = {f_ref:.6g} Hz  |  Δf = {df:.3e} Hz  ({rel:.3f}%)")

# Use dominant frequencies from steady segments computed above
_freq_check("Surge FFT(main)", f1_surge, f_theory)
_freq_check("Heave FFT(main)", f1_heave, f_theory)
_freq_check("Pitch FFT(main)", f1_pitch, f_theory)

# Save CSV for this case
try:
    import csv
    with open('RAO_single_case.csv', 'w', newline='') as fcsv:
        w = csv.writer(fcsv)
        w.writerow(["quantity","value","unit"]) 
        w.writerow(["H",        f"{waveHeight:.8g}",      "m"]) 
        w.writerow(["a",        f"{inc_amp:.8g}",         "m"]) 
        w.writerow(["T",        f"{wavePeriod:.8g}",      "s"]) 
        w.writerow(["f_inc",    f"{f_incident:.8g}",      "Hz"]) 
        w.writerow(["phi_eta",  f"{wavePhaseDeg:.8g}",    "deg"]) 
        w.writerow(["R_surge",  f"{R_surge:.8g}",         "m"]) 
        w.writerow(["R_heave",  f"{R_heave:.8g}",         "m"]) 
        w.writerow(["R_pitch",  f"{R_pitch:.8g}",         "deg"]) 
        w.writerow(["RAO_surge_mag", f"{rao_surge_mag:.8g}", "m/m"]) 
        w.writerow(["RAO_heave_mag", f"{rao_heave_mag:.8g}", "m/m"]) 
        w.writerow(["RAO_pitch_mag", f"{rao_pitch_mag:.8g}", "rad/m"]) 
        w.writerow(["RAO_surge_phase", f"{rao_surge_phase:.8g}", "deg"]) 
        w.writerow(["RAO_heave_phase", f"{rao_heave_phase:.8g}", "deg"]) 
        w.writerow(["RAO_pitch_phase", f"{rao_pitch_phase:.8g}", "deg"]) 
    print("[RAO] Saved RAO_single_case.csv")
except Exception as e:
    print(f"[RAO] CSV save failed: {e}")

# Optional: legends for clarity
# ax1.legend(["Data", "Main freq fit"], loc="best", fontsize=8)
# ax2.legend(["Data", "Main freq fit"], loc="best", fontsize=8)
# ax3.legend(["Data", "Main freq fit"], loc="best", fontsize=8)

fig2, (bx1, bx2, bx3) = plt.subplots(3, 1, dpi=300, layout='constrained')

bx1.plot(freq_surge, amp_surge, linewidth=1)
bx1.set_xlabel('Frequency (Hz)')
bx1.set_ylabel('Amplitude (m)')
bx1.set_title('Surge Spectrum (single-sided)')
bx1.grid(True, linewidth=0.3)
bx1.set_xlim(0, 10)
annotate_peak(bx1, f1_surge, A1_surge, 'm')

bx2.plot(freq_heave, amp_heave, linewidth=1)
bx2.set_xlabel('Frequency (Hz)')
bx2.set_ylabel('Amplitude (m)')
bx2.set_title('Heave Spectrum (single-sided)')
bx2.grid(True, linewidth=0.3)
bx2.set_xlim(0, 10)
annotate_peak(bx2, f1_heave, A1_heave, 'm')

bx3.plot(freq_pitch, amp_pitch, linewidth=1)
bx3.set_xlabel('Frequency (Hz)')
bx3.set_ylabel('Amplitude (deg)')
bx3.set_title('Pitch Spectrum (single-sided)')
bx3.grid(True, linewidth=0.3)
bx3.set_xlim(0, 10)
annotate_peak(bx3, f1_pitch, A1_pitch, 'deg')

# Optional: limit x-axis to Nyquist or a reasonable max (auto by default)
# for ax in (bx1, bx2, bx3):
#     ax.set_xlim(0, max(ax.get_xlim()[1], 1.0))

# === Print summary to console ===
print('\nDominant frequencies and amplitudes (single-sided):')
print(f"  Surge: f1 = {f1_surge:.6g} Hz, A1 = {A1_surge:.6g} m")
print(f"  Heave: f1 = {f1_heave:.6g} Hz, A1 = {A1_heave:.6g} m")
print(f"  Pitch: f1 = {f1_pitch:.6g} Hz, A1 = {A1_pitch:.6g} deg")

plt.show()

fig2.savefig('./Plots/FFT_spectrum.pdf', format='pdf', bbox_inches='tight')
fig1.savefig('./Plots/FFT_time_series.pdf', format='pdf', bbox_inches='tight')