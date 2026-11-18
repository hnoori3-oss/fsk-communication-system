"""Example: transmit and recover text through a noisy FSK channel."""
import numpy as np
import matplotlib.pyplot as plt
from fsk import additive_noise_channel, bits_to_string, fsk_demodulator, fsk_transmitter, string_to_bits

text = "Information"
f0, f1 = 4000, 7000
T, fs = 0.02, 22050
snr_db = 20

transmitted = fsk_transmitter(text, f0, f1, T, fs)
received = additive_noise_channel(transmitted, snr_db, fs * T)
recovered_bits = fsk_demodulator(received, f0, f1, T, fs)
expected_bits = string_to_bits(text)

print(f"Transmitted: {text}")
print(f"Recovered:   {bits_to_string(recovered_bits)}")
print(f"Bit errors:  {np.count_nonzero(recovered_bits != expected_bits)} / {len(expected_bits)}")

plt.specgram(received, Fs=fs)
plt.xlabel("Time (s)")
plt.ylabel("Frequency (Hz)")
plt.title(f"Received FSK Signal at {snr_db} dB SNR")
plt.colorbar(label="Power/frequency (dB/Hz)")
plt.tight_layout()
plt.show()
