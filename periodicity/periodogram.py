import numpy as np
from astropy.stats import LombScargle
from wavelets import WaveletAnalysis


def lombscargle(t, x, dx=None, f0=0, fmax=None, n=5, fap_method=None, fap_level=None, psd=False):
    """Computes the generalized Lomb-Scargle periodogram of a discrete signal x(t)

    Parameters
    ----------
    t: array-like
        time array
    x: array-like
        signal array
    dx: array-like (optional)
        measurement uncertainties for each sample
    f0: float (optional default=0)
        minimum frequency
    fmax: float (optional)
        maximum frequency
        If None is given, defaults to the pseudo-Nyquist limit
    n: float (optional default=5)
        samples per peak
    fap_method: string {None, 'baluev', 'bootstrap'}
        the approximation method to use for highest peak FAP and false alarm levels
        None by default
    fap_level: array-like (optional)
        false alarm probabilities to approximate heights
    psd: bool (optional)
        whether to leave periodogram unnormalized (Fourier Spectral Density)

    Returns
    -------
    ls: astropy.stats.LombScargle object
        the full object for the given dataset
    f: array-like
        frequency array
    a: array-like
        power array
    fap: float
        false alarm probability of highest peak
    fal: float
        false alarm level for a given FAP
    """
    if psd:
        ls = LombScargle(t, x, dy=dx, normalization='psd')
    else:
        ls = LombScargle(t, x, dy=dx)
    if fmax is None:
        T = float(np.median(np.diff(t)))
        fs = 1 / T
        fmax = fs / 2
    f, a = ls.autopower(samples_per_peak=n, minimum_frequency=f0, maximum_frequency=fmax)
    if fap_method is not None:
        assert fap_method in ['baluev', 'bootstrap'], "Unknown FAP method {}".format(fap_method)
        fap = ls.false_alarm_probability(a.max(), method=fap_method, minimum_frequency=f0,
                                         maximum_frequency=fmax, samples_per_peak=n)
        if fap_level is not None:
            fal = ls.false_alarm_level(fap_level, method=fap_method, minimum_frequency=f0,
                                       maximum_frequency=fmax, samples_per_peak=n)
            return ls, f, a, fap, fal
        return ls, f, a, fap
    return ls, f, a


def window(t, n=5):
    """Computes the periodogram of the window function

    Parameters
    ----------
    t: array-like
        times of sampling comb window
    n: float (optional default=5)
        samples per peak
    Returns
    -------
    f: array-like
        frequency array
    a : array-like
        power array
    """
    ls = LombScargle(t, 1, fit_mean=False, center_data=False)
    f, a = ls.autopower(minimum_frequency=0, samples_per_peak=n)
    return f, a


def wavelet(t, x, pmin=0, pmax=None, n_periods=1000):
    """Global Wavelet Power Spectrum using Morlet wavelets

    Parameters
    ----------
    t: array-like
        time array
    x: array-like
        signal array
    pmin: float (optional default=0)
        minimum period
    pmax: float (optional default None)
        maximum period; if None is given, uses default scaling
    n_periods: int (optional default=1000)
        number of trial periods

    Returns
    -------
    wa: wavelets.WaveletAnalysis object
        the full object for the given dataset
    periods: array-like
        trial periods array
    gwps: array-like
        Global Wavelet Power Spectrum (WPS projected on period axis)
    wps: array-like
        Wavelet Power Spectrum
    """
    dt = float(np.median(np.diff(t)))
    wa = WaveletAnalysis(x, t, dt=dt, mask_coi=True, unbias=True)
    periods = wa.fourier_periods
    wps = wa.wavelet_power
    gwps = wa.global_wavelet_spectrum
    return wa, periods, gwps, wps


# TODO: check out Supersmoother (Reimann 1994)
