"""Run the lab experiments (A-D given, E is yours) and write figures + results.json.
Run:  python experiments.py   (after completing the TODOs in sfr_lab.py)"""
import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.ticker
import sfr_lab as L
SIG, ANG = 0.6, 5.0
FF = np.linspace(0, 1, 401)
res = {'true_mtf50': L.true_mtf50(SIG, ANG)}
def curve(img): f, m, i = L.sfr(img); return np.interp(FF, f, m), L.mtf50(f, m), i
truth = L.true_mtf(FF, SIG, ANG)
clean = L.render_edge(angle_deg=ANG, sigma=SIG)

# ---- A: validation, noiseless float image
mA, m50A, iA = curve(clean)
fig, ax = plt.subplots(1, 4, figsize=(18, 4.2))
ax[0].imshow(L.to_uint8(clean), cmap='gray', vmin=0, vmax=255); ax[0].set_title(f'Synthetic edge, {ANG}°, σ={SIG} px')
ax[1].plot(iA['x'], iA['esf'], '.-', ms=3); ax[1].set_xlim(-6, 6); ax[1].set_title('ESF (4× oversampled)'); ax[1].set_xlabel('distance [px]')
ax[2].plot(iA['x'], iA['lsf'] / iA['lsf'].max(), '.-', ms=3); ax[2].set_xlim(-6, 6); ax[2].set_title('LSF (windowed)'); ax[2].set_xlabel('distance [px]')
ax[3].plot(FF, truth, 'k', lw=3, alpha=.35, label='ground truth'); ax[3].plot(FF, mA, 'C0', label='measured')
ax[3].plot(FF, 20 * np.abs(mA - truth), 'C3', lw=1, label='|error| × 20'); ax[3].axvline(.5, color='gray', lw=.8)
ax[3].set_xlim(0, 1); ax[3].set_ylim(0, 1.05); ax[3].legend(); ax[3].set_xlabel('cycles/pixel'); ax[3].set_title('MTF')
for a in ax[1:]: a.grid(alpha=.3)
plt.tight_layout(); plt.savefig('fig_A_validation.png', dpi=110); plt.close()
res['A'] = dict(mtf50=m50A, max_err_to_nyquist=float(np.abs(mA - truth)[FF <= .5].max()), angle_est=iA['angle_deg'])

# ---- B: angle sweep
angles = [0, 1, 2, 5, 10, 18.43, 22, 26.57, 30, 40, 45]
B = []
for a in angles:
    m, m50, i = curve(L.render_edge(angle_deg=a, sigma=SIG)); t = L.true_mtf(FF, SIG, a)
    B.append(dict(angle=a, mtf50=m50, true50=L.true_mtf50(SIG, a), max_err=float(np.abs(m - t)[FF <= .5].max()), empty_bins=i['empty_bins']))
res['B'] = B
fig, ax = plt.subplots(figsize=(7, 4))
ax.semilogy([b['angle'] for b in B], [max(b['max_err'], 1e-4) for b in B], 'o-')
for b in B: ax.annotate(f"{b['empty_bins']}", (b['angle'], max(b['max_err'], 1e-4)), textcoords='offset points', xytext=(0, 7), ha='center', fontsize=8)
ax.set_xlabel('edge angle [deg]'); ax.set_ylabel('max |MTF error| up to Nyquist'); ax.grid(alpha=.3, which='both')
ax.set_title('Angle sweep (labels = empty ¼-px bins)'); plt.tight_layout(); plt.savefig('fig_B_angle.png', dpi=110); plt.close()

# ---- C: noise sweep, 30 fixed seeds per level, 8-bit quantised
levels, seeds = [0, 1, 2, 4, 8], range(30)
C = {}
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
for sn, col in zip(levels, plt.cm.viridis(np.linspace(0, .9, len(levels)))):
    cs, ms = [], []
    for s in seeds:
        m, m50, _ = curve(L.to_uint8(L.add_noise(clean, sn, seed=s))); cs.append(m); ms.append(m50)
    cs = np.array(cs); C[sn] = dict(mtf50_mean=float(np.mean(ms)), mtf50_std=float(np.std(ms)),
        floor_0p6_1=float(cs[:, FF > .6].mean()), mtf_nyq_std=float(cs[:, np.argmin(abs(FF - .5))].std()))
    ax[0].plot(FF, cs.mean(0), color=col, label=f'σn={sn} DN (SNR={153/max(sn,1e-9):.0f})' if sn else 'σn=0 (8-bit only)')
    ax[0].fill_between(FF, cs.mean(0) - cs.std(0), cs.mean(0) + cs.std(0), color=col, alpha=.2)
ax[0].plot(FF, truth, 'k--', lw=1, label='truth'); ax[0].set_xlim(0, 1); ax[0].set_ylim(0, 1.05)
ax[0].set_xlabel('cycles/pixel'); ax[0].set_title('MTF vs noise (mean ± 1 std over 30 seeds)'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[1].errorbar(levels, [C[k]['mtf50_mean'] for k in levels], [C[k]['mtf50_std'] for k in levels], fmt='o-', capsize=4, label='MTF50')
ax[1].axhline(res['true_mtf50'], color='k', ls='--', lw=1, label='true MTF50')
ax2 = ax[1].twinx(); ax2.plot(levels, [C[k]['floor_0p6_1'] for k in levels], 's-', color='C3', label='mean MTF 0.6–1 cy/px (noise floor)')
ax2.set_ylabel('noise floor', color='C3'); ax[1].set_xlabel('noise σn [DN]'); ax[1].set_ylabel('MTF50 [cy/px]'); ax[1].grid(alpha=.3)
ax[1].legend(loc='upper left', fontsize=8); ax2.legend(loc='lower right', fontsize=8); ax[1].set_title('MTF50 stays unbiased; spread and floor grow')
plt.tight_layout(); plt.savefig('fig_C_noise.png', dpi=110); plt.close()
res['C'] = {str(k): v for k, v in C.items()}

# ---- D: JPEG quality sweep, with and without the SAME noise (σn=2, seed 0)
Qs = [100, 95, 90, 75, 50, 30, 20, 10, 5]
D = {}
fig, ax = plt.subplots(1, 3, figsize=(19, 4.8))
for sn, ls in [(0, '-'), (2, '--')]:
    base = L.to_uint8(L.add_noise(clean, sn, seed=0)); rows = []
    for q, col in zip(Qs, plt.cm.plasma(np.linspace(0, .85, len(Qs)))):
        dec, bpp = L.jpeg(base, q); m, m50, _ = curve(dec)
        rmse = float(np.sqrt(np.mean((dec - clean) ** 2)))
        rows.append(dict(Q=q, bpp=bpp, mtf50=m50, mtf_nyq=float(np.interp(.5, FF, m)), max_mtf=float(m.max()), rmse_vs_clean=rmse))
        if sn == 0: ax[0].plot(FF, m, color=col, label=f'Q={q} ({bpp:.2f} bpp)')
    D[sn] = rows
    ax[1].plot([r['bpp'] for r in rows], [r['mtf50'] for r in rows], 'o' + ls, label=f'σn={sn} DN')
    ax[2].plot([r['Q'] for r in rows], [r['mtf50'] for r in rows], 'o' + ls, label=f'σn={sn} DN')
ax[0].plot(FF, truth, 'k--', lw=1.2, label='truth'); ax[0].set_xlim(0, 1); ax[0].set_ylim(0, 1.15); ax[0].axvline(.5, color='gray', lw=.8)
ax[0].set_xlabel('cycles/pixel'); ax[0].set_title('JPEG: MTF vs quality (noiseless)'); ax[0].legend(fontsize=7, ncol=2); ax[0].grid(alpha=.3)
for a, xl in [(ax[1], 'bits per pixel'), (ax[2], 'JPEG quality Q')]:
    a.axhline(res['true_mtf50'], color='k', ls=':', lw=1, label='true MTF50'); a.set_xlabel(xl); a.set_ylabel('MTF50 [cy/px]'); a.grid(alpha=.3); a.legend(fontsize=8)
ax[1].set_xscale('log'); ax[1].xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g')); ax[1].xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); ax[1].set_xticks([0.15,0.2,0.3,0.5,1,2,4]); ax[1].set_title('MTF50 vs bitrate'); ax[2].set_title('MTF50 vs Q'); ax[2].invert_xaxis()
plt.tight_layout(); plt.savefig('fig_D_jpeg.png', dpi=110); plt.close()
res['D'] = {str(k): v for k, v in D.items()}

# ---- E: is JPEG linear? same edge at three contrasts, compressed at Q=90 and Q=30
# If JPEG were a linear system, the MTF would not depend on the contrast of the edge:
# a weaker edge would just give a weaker output, and after normalising the MTF to 1 at f=0
# all contrasts would give the same curve. Here we check if that is true.

# The three contrasts we test: (dark level, light level, name of the ratio), all in DN
contrasts = [(20, 200, '10:1'), (51, 204, '4:1'), (120, 150, '1.25:1')]
E = {}                                    # here we save the MTF50 of each of the 6 cases
fig, ax = plt.subplots(figsize=(8, 5))

# Outer loop: the two JPEG qualities (Q=90 = light compression, drawn with a solid line;
# Q=30 = strong compression, drawn with a dashed line)
for q, ls in [(90, '-'), (30, '--')]:
    # Inner loop: the three contrasts, each one gets its own colour
    for (dark, light, lab), col in zip(contrasts, ['C0', 'C1', 'C2']):
        # Make the same edge as before (same angle and same blur), only the dark/light levels change
        img = L.render_edge(angle_deg=ANG, sigma=SIG, dark=dark, light=light)
        # Round to 8 bit (like a real camera image), then compress with JPEG and decode it back
        dec, bpp = L.jpeg(L.to_uint8(img), q)
        # Measure the MTF of the decoded image with our sfr() and find its MTF50
        m, m50, _ = curve(dec)
        # Save the result with a name like 'Q90 4:1'
        E[f'Q{q} {lab}'] = m50
        # Draw this MTF curve, with its MTF50 in the legend
        ax.plot(FF, m, ls, color=col, label=f'Q={q}, {dark}/{light} DN ({lab}): MTF50={m50:.3f}')

# Draw the true MTF for comparison, and a grey line at Nyquist (0.5 cycles/pixel)
ax.plot(FF, truth, 'k:', lw=1.5, label=f'truth: MTF50={res["true_mtf50"]:.3f}')
ax.axvline(.5, color='gray', lw=.8)
# Axis limits, labels, title, grid and legend
ax.set_xlim(0, 1); ax.set_ylim(0, 1.15); ax.set_xlabel('cycles/pixel'); ax.set_ylabel('MTF')
ax.set_title('JPEG: same edge at three contrasts (solid Q=90, dashed Q=30)'); ax.grid(alpha=.3); ax.legend(fontsize=8)
# Save the figure and store the six MTF50 values in the results
plt.tight_layout(); plt.savefig('fig_E_contrast.png', dpi=110); plt.close()
res['E'] = E

json.dump(res, open('results.json', 'w'), indent=1, default=float)
print(json.dumps(res, indent=1, default=lambda o: round(float(o), 4)))
