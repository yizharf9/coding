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
    """Slanted-edge MTF (ISO 12233 style). Returns f [cy/px], MTF, dict of intermediates."""
    img = np.asarray(img, dtype=float)
    a, b = edge_fit(img)                      # edge line: x = a*y + b   (given)
    H, W = img.shape
    y, x = np.mgrid[0:H, 0:W].astype(float)

    # TODO STEP 2 - ESF
    #   d   = perpendicular distance of every pixel centre from the edge line   (hint: multiply by cos(arctan a))
    #   bin all pixels by d into bins of width bw = 1/oversample over [-half_width, +half_width]
    #   esf = mean value in each bin; fill empty bins by linear interpolation and COUNT them
    #   centres = bin centres
    raise NotImplementedError("STEP 2: build the oversampled ESF")

    # TODO STEP 3 - LSF
    #   lsf = derivative of the ESF with the central difference [0.5, 0, -0.5] / bw  (set the two end samples to 0)
    #   multiply by a Hamming window CENTRED ON THE LSF PEAK (not on the array centre)

    # TODO STEP 4 - MTF
    #   F = |rfft(windowed lsf)|,  f = rfftfreq(N, d=bw)   -> cycles/pixel
    #   normalise so that MTF(0) = 1
    #   divide by the frequency response of the central difference, sinc(2 f bw)  (clip it at 0.3)

    info = dict(angle_deg=np.degrees(np.arctan(a)), x=centres, esf=esf, lsf=lsf_windowed,
                empty_bins=n_empty, min_count=min_count_near_edge)
    return f, mtf, info

def mtf50(f, m, level=0.5):
    """STEP 5: frequency where the MTF first drops below 'level' (linear interpolation between samples).
    Return np.nan if it never does."""
    # TODO
    raise NotImplementedError("STEP 5: MTF50")

def true_mtf50(sigma=0.6, angle_deg=0.0):
    f = np.linspace(0, 1, 100001)
    return mtf50(f, true_mtf(f, sigma, angle_deg))
