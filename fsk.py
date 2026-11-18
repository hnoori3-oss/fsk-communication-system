"""Reusable FSK communication simulation functions from the project notebooks."""

import numpy as np


def int_to_bits(b, R=8):
    """convert a positive integer into a sequence of bits
    
    Parameters:
    -----------
    b - integer, must be between 0 and 2^R-1
    R - number of bits (default: 8)

    Returns:
    --------
    NumPy array of length R with only 0s and 1s

    Raises:
    -------
    `ValueError` if n is not between 0 and 2^R-1

    The bits are stored in LSB first order; the least-significant bit is stored in the 
    first position of the resulting array
    """

    if b < 0 or b >= 2**R:
        raise(ValueError(f'{b} cannot be represented with {R} bits.'))
    
    # allocate storage for result; use the smallest possible element size
    res = np.zeros(R, dtype=np.uint8)

    # p = 1; sets the LSB to 1 and all other bits to 0
    p = 1
    for n in range(R):
        # Extract bit in the n-th poition; then, move it to the LSB
        res[n] = (b & p) >> n
        # shift the 1 in p one position to the left
        p = p << 1


    return res


def bits_to_int(bit_seq):
    """Convert a list or array of bits to an integer
    
    Parameters:
    -----------
    bit_seq - a list or array of 0s and 1s

    Returns:
    --------
    positive integer

    Example:
    --------
    bits_to_int([1 0 1 1]) returns 13 (as 13 = 1 + 4 + 8)

    It is assumed that the first bit in `bit_seq` is the LSB
    """
    res = 0
    for n in range(len(bit_seq)):
        res += bit_seq[n] * 2**n

    return res


def string_to_bits( string):
    """Convert a unicode string to an array of bits
    
    Parameters:
    -----------
    string - the unicode string to be converted
    
    Returns:
    --------
    NumPy array of bits

    """

    # turn string into a sequence of bytes
    b = string.encode()

    # allocate storage for output: we need 8 bits for each byte
    # and store bits as unsigned 8-bit integers
    res = np.zeros(8*len(b), dtype=np.uint8)

    # convert each byte to bits and place in output array
    start = 0

    # loop over all bytes
    for c in b:
        # use function  int_to_bits to get bits
        res[start : start+8] = int_to_bits(c)
        start = start + 8

    
    return res


def bits_to_string(bits):
    """Convert a sequence of bits to a string
    
    Parameters:
    -----------
    bits - NumPy array of bits

    Returns:
    --------
    decoded string

    Raises:
    -------
    ValueError if length of bits is not a multiple of 8.
    """

    if ((len(bits) % 8) != 0):
        raise ValueError('not a multiple of 8')

    res = np.zeros(len(bits)//8, dtype = np.uint8)

    for n in range(len(res)):
        res[n] = bits_to_int(bits[8*n : 8*n + 8])


    raw_bytes = res.tobytes()

    return raw_bytes.decode("utf-8", "replace")


def fsk_modulator(bits, f0, f1, T, fs):
    """FSK modulate a sequence of bits
    
    Parameters:
    ------------
    bits - the sequence of bits to be sent (must all be 0 or 1)
    f0 - frequency for 0-bits
    f1 - frequency for 1-bits
    T - bit period
    fs - sample rate

    Returns:
    --------
    Numpy array representing sequence of samples
    """
    N = int(T * fs)
    sig = np.zeros(len(bits) * N)
    tt=np.arange(0, T * len(bits), 1/fs)

    for n in range(len(bits)):
        if bits[n] == 0:
            f=f0
        else:
            f=f1
        sig[n*N:N*(n+1)]= np.cos(2*np.pi*f*tt[n*N:(n+1)*N])
    return sig


def fsk_transmitter(string, f0, f1, T, fs):
    """Modulate a string into an FSK signal
    Parameters:
    ------------
    string - the text to be transmitted
    f0 - frequency for 0-bits
    f1 - frequency for 1-bits
    T - bit period
    fs - sample rate

    Returns:
    --------
    Numpy array representing sequence of samples
    
    """
    bits = string_to_bits(string)

    res = fsk_modulator(bits, f0, f1, T, fs)

    return res


def matched_filter(sig, hh, fsT):
    """matched filter
    
    Parameters:
    -----------
    sig - input signal
    hh - impulse response
    fsT - (integer) number of samples per bit period

    Returns:
    --------
    NumPy array of down-sampled matched filter
    """

    y = np.convolve(sig, hh)
    samples = []
    

    N=fsT

    for n in range(N-1, len(sig), fsT):
        samples.append(y[n])
    return np.array(samples)


def detector(y0, y1):
    """detector for matched filter outputs
    
    Parameters:
    -----------
    y0 - matched filter output for 0 bits
    y1 - matched filter output for 1 bits

    Returns:
    --------
    bit decisions (type np.uint8)
    """
    bits = []

    for n in range(len(y0)):
        if (y0[n] > y1[n]):
            bits.append(0)
        else:
            bits.append(1)

    return np.array(bits, dtype=np.uint8)


def fsk_demodulator(sig, f0, f1, T, fs):
    """FSK demodulator
    
    Parameters:
    -----------
    sig - received signal
    f0 - first FSK frequency
    f1 - second FSK frequency
    T - bit period
    fs - sample rate

    Returns:
    --------
    Numpy vector of bit decsions
    """
    p0=fsk_modulator([0], f0, f1, T, fs)
    p1= fsk_modulator([1], f0, f1, T, fs)

    h0 = np.flip(p0)
    h1= np.flip(p1)
    

    N = int(fs*T)

    bit_zero = matched_filter(sig, h0, N)
    bit_one = matched_filter(sig, h1, N)

    bits = detector(bit_zero, bit_one)

    return bits


def additive_noise_channel(sig, SNR_dB, fsT):
    """simulate additive white Gaussian noise
    
    Parameters:
    -----------
    sig - transmitted signal
    SNR_dB - SNR in dB
    fsT - number of samples per symbol period

    Returns:
    --------
    simulated received signal
    """
    N_bits = len(sig) / fsT

    # energy per bit
    Eb = np.sum( sig ** 2) / N_bits

    # linear SNR
    SNR = 10 ** (SNR_dB/10)

    # noise sample variance
    var_noise = Eb/SNR

    # add noise
    return sig + np.sqrt(var_noise) * np.random.randn(len(sig))
