"""
sfr_lab.py  -  Slanted-edge MTF lab: STUDENT VERSION

Complete every block marked  TODO  (search for "TODO"). Do not change the function signatures:
experiments.py calls them.

Synthetic edge with a KNOWN MTF  ->  noise  ->  JPEG  ->  slanted-edge SFR  ->  compare with truth.
Requires: numpy, scipy, pillow, matplotlib
"""
import io
import numpy as np
from scipy.special import erf
from PIL import Image

# ----------------------------------------------------------------------------- 1. synthetic target
def render_edge(size=256, angle_deg=5.0, sigma=0.6, dark=51, light=204, offset=0.3, ss=8):
    """Near-vertical edge (dark left, light right) rotated by angle_deg from vertical.
    Optics = Gaussian PSF with std 'sigma' [px]  -> blurred edge is exactly a normal CDF.
    Sensor  = 100%-fill-factor square pixel      -> integrated by ss x ss supersampling.
    Returns a float image in DN (0..255), no noise, no quantisation."""
    t = np.deg2rad(angle_deg)
    sub = (np.arange(ss) + 0.5) / ss - 0.5                 # sub-pixel sample offsets
    y, x = np.mgrid[0:size, 0:size].astype(float)
    cx = size / 2 + offset
    acc = np.zeros((size, size))
    for dy in sub:
        for dx in sub:
            X, Y = x + dx, y + dy
            d = (X - cx) * np.cos(t) - (Y - size / 2) * np.sin(t)   # signed distance to the edge line
            acc += 0.5 * (1 + erf(d / (np.sqrt(2) * sigma)))
    return dark + (light - dark) * acc / ss**2

def true_mtf(f, sigma=0.6, angle_deg=0.0):
    """Ground truth along the edge normal: Gaussian optics x square-pixel aperture.
    A square pixel seen along a direction tilted by angle_deg has MTF sinc(f cos t) * sinc(f sin t).
    f in cycles/pixel."""
    t = np.deg2rad(angle_deg)
    return np.exp(-2 * np.pi**2 * sigma**2 * f**2) * np.abs(np.sinc(f * np.cos(t)) * np.sinc(f * np.sin(t)))

def add_noise(img, sigma_n, seed=0):
    """Additive white Gaussian noise [DN] with a FIXED seed -> identical noise in every condition."""
    if sigma_n == 0:
        return img.copy()
    return img + np.random.default_rng(seed).normal(0, sigma_n, img.shape)

def to_uint8(img):
    return np.clip(np.round(img), 0, 255).astype(np.uint8)

def jpeg(img_u8, quality):
    """Grey-scale JPEG round trip with Pillow. Returns (decoded image, bits per pixel)."""
    buf = io.BytesIO()
    Image.fromarray(img_u8, mode='L').save(buf, format='JPEG', quality=quality, subsampling=0)
    bpp = 8 * buf.tell() / img_u8.size
    return np.asarray(Image.open(io.BytesIO(buf.getvalue())), dtype=float), bpp

# ----------------------------------------------------------------------------- 2. slanted-edge SFR
def edge_fit(img, win=8):
    """STEP 1: locate the edge in every row and fit a straight line x = a*y + b.
    Per row: derivative along x, find its peak, take the centroid within +-win px of the peak
    (a window keeps noise far from the edge out of the centroid)."""
    img = np.asarray(img, dtype=float)       # uint8 would wrap around in np.diff!
    dx = np.diff(img, axis=1)
    dx = np.abs(np.apply_along_axis(lambda r: np.convolve(r, np.ones(3) / 3, 'same'), 1, dx))
    xs = np.arange(dx.shape[1]) + 0.5
    rows = np.arange(img.shape[0])
    xc = np.empty(len(rows))
    for r in rows:
        p = np.argmax(dx[r]); lo, hi = max(p - win, 0), min(p + win + 1, dx.shape[1])
        w = dx[r, lo:hi]
        xc[r] = (w * xs[lo:hi]).sum() / w.sum()
    a, b = np.polyfit(rows, xc, 1)
    resid = xc - (a * rows + b)                              # reject outlier rows, refit once
    keep = np.abs(resid) < 3 * np.std(resid) + 1e-9
    return np.polyfit(rows[keep], xc[keep], 1)

def sfr(img, oversample=4, half_width=24):
    """ Slanted-edge MTF (ISO 12233 style). Returns f [cy/px], MTF, dict of intermediates.
    oversample=4 constructs an ESF with quarter-pixel bins.
    half_width limits the analyzed distance to +/- half_width pixels."""
    img = np.asarray(img, dtype=float)
    a, b = edge_fit(img)                      # edge line: x = a*y + b   (given)
    H, W = img.shape
    y, x = np.mgrid[0:H, 0:W].astype(float)

    # STEP 2 - ESF: build an oversampled Edge Spread Function
    # Measure the signed perpendicular distance from each pixel center to the
    # line x - a*y - b = 0; the denominator converts it to Euclidean distance
    d = (x - a * y - b) / np.sqrt(1 + a**2)

    # Define the bin width and centres
    bw = 1.0 / oversample
    n_bins = int(2 * half_width / bw)
    centres = -half_width + (np.arange(n_bins) + 0.5) * bw

    # Assign pixels to bins according to their distance
    bin_idx = np.floor((d + half_width) / bw).astype(int)
    valid = (bin_idx >= 0) & (bin_idx < n_bins)

    # Count pixels and sum their intensities in each bin
    counts = np.bincount(bin_idx[valid], minlength=n_bins)
    sums = np.bincount(
        bin_idx[valid],
        weights=img[valid],
        minlength=n_bins
    )

    # Calculate mean intensity for each non-empty bin
    non_empty = counts > 0
    esf = np.zeros(n_bins, dtype=float)
    esf[non_empty] = sums[non_empty] / counts[non_empty]

    # Record how many subpixel bins lack any measured pixel centres
    # This quantity is used in the angle-sweep experiment
    n_empty = int(np.sum(~non_empty))

    if np.count_nonzero(non_empty) < 2:
        raise ValueError("Not enough non-empty bins to build ESF")

    # Linearly interpolate empty bins between observed samples outside that range
    # np.interp uses the nearest observed endpoint value
    esf = np.interp(centres, centres[non_empty], esf[non_empty])

    # Track the least populated bin within one pixel of the detected edge
    # Low sample counts can make the ESF more sensitive to noise
    min_count_near_edge = int(np.min(counts[np.abs(centres) <= 1.0]))

    # STEP 3 - LSF: differentiate the ESF and apply a centred Hamming window
    # The central-difference stencil approximates the spatial derivative
    # dividing by bw expresses it per pixel rather than per ESF sample
    lsf = np.convolve(esf, [0.5, 0, -0.5], mode='same') / bw

    # Set the first and last samples to zero
    lsf[0] = 0.0
    lsf[-1] = 0.0

    # Use the strongest absolute slope to locate the LSF peak
    peak_idx = np.argmax(np.abs(lsf))

    # Create a Hamming window centered on the LSF peak
    n = np.arange(len(lsf))
    hamming_window = 0.54 + 0.46 * np.cos(
        2 * np.pi * (n - peak_idx) / (len(lsf) - 1)
    )

    # Apply the Hamming window to the LSF
    lsf_windowed = lsf * hamming_window

    # STEP 4 - MTF: Fourier-transform the windowed LSF
    # RFFT returns nonnegative frequencies for real input, abs takes magnitude
    # Apply the FFT to the windowed LSF
    F = np.abs(np.fft.rfft(lsf_windowed))

    # Convert FFT bins into spatial frequencies, in cycles/pixel
    f = np.fft.rfftfreq(len(lsf_windowed), d=bw)

    # Normalize the MTF so that MTF(0) = 1
    if F[0] == 0:
        raise ValueError("Cannot normalize MTF: zero DC component")

    mtf = F / F[0]

    # Compensate for attenuation introduced by the central-difference stencil
    # Its normalized frequency response is sinc(2 * f * bw)
    correction = np.sinc(2 * f * bw)
    # Prevent very small denominators from amplifying numerical noise excessively
    correction = np.maximum(correction, 0.3)

    # Apply derivative correction
    mtf = mtf / correction

    # Save diagnostics for the validation and angle/noise/JPEG experiments:
    # fitted angle, ESF distances/values, windowed LSF, and ESF bin counts
    info = dict(angle_deg=np.degrees(np.arctan(a)), x=centres, esf=esf, lsf=lsf_windowed,
                empty_bins=n_empty, min_count=min_count_near_edge)
    return f, mtf, info

def mtf50(f, m, level=0.5):
    """STEP 5: Find the first downward MTF crossing of the given level.
       Interpolate between adjacent frequency samples for sub-bin precision.
       If no crossing exists, return NaN.
       """
    # Locate frequencies where the MTF has reached or fallen below the target
    below = np.where(m <= level)[0]

    # Return NaN if MTF never reaches the target level
    if len(below) == 0:
        return np.nan

    # Select the first crossing
    i = below[0]

    # Handle the case where the first sample is already below the level
    if i == 0:
        return float(f[0])

    # Get the two samples surrounding the crossing
    f1, f2 = f[i - 1], f[i]
    m1, m2 = m[i - 1], m[i]

    # Use linear interpolation to estimate the exact crossing frequency
    f50 = f1 + (level - m1) * (f2 - f1) / (m2 - m1)

    return float(f50)


def true_mtf50(sigma=0.6, angle_deg=0.0):
    f = np.linspace(0, 1, 100001)
    return mtf50(f, true_mtf(f, sigma, angle_deg))
