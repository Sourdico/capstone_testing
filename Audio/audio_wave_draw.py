import wave
import numpy as np
import matplotlib.pyplot as plt

# Open the WAV file
wav_obj = wave.open('please_get_into_the_camera_frame.wav', 'rb')

# Get the sample frequency
sample_freq = wav_obj.getframerate()

# Get the number of samples
n_samples = wav_obj.getnframes()

# Calculate the duration of the audio file in seconds
t_audio = n_samples / sample_freq

# Read the audio data
audio_data = wav_obj.readframes(n_samples)

# Convert the audio data to an array
audio_array = np.frombuffer(audio_data, dtype=np.int16)

# Create a time array
time_array = np.linspace(0, t_audio, n_samples)

# Plot the waveform
plt.figure(figsize=(10, 4))
plt.plot(time_array, audio_array)
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.title('Audio - Please Get Into The Camera Frame. Make sure camera can capture your face.')
plt.grid(True)
plt.show()
