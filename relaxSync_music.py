import sounddevice as sd
import numpy as np
import random
from scipy.io.wavfile import read

# Global variables
buffer_size = 1024  # Number of frames per callback
active_tracks = []  # List to store (audio data, current playback position)

samplerate = None
current_position = 0  # Global synchronized playback position

# Function to load audio files
def load_audio(filename):
    global samplerate
    filename = "stem/" + filename  # Add path prefix
    print(f"Loading: {filename}")
    sr, data = read(filename)
    samplerate = sr if samplerate is None else samplerate
    data = data / np.max(np.abs(data), axis=0)  # Normalize to range [-1, 1]
    if len(data.shape) > 1:  # Convert to mono if audio is stereo
        data = np.mean(data, axis=1)
    return data

# Real-time callback for playback
def callback(outdata, frames, time, status):
    if status:
        print(status)
    global active_tracks, current_position

    mix = np.zeros(frames)  # Initialize the mixing buffer
    

    for i, (track, position) in enumerate(active_tracks):
        remaining_frames = len(track) - position  # Number of frames remaining
        if remaining_frames >= frames:
            mix += track[position:position + frames]
            active_tracks[i] = (track, position + frames)  # Update playback position
        else:
            mix[:remaining_frames] += track[position:]
            active_tracks[i] = (track, 0 + (frames - remaining_frames))  # Restart track

    current_position += frames  # Update global position
    # print(len(active_tracks))
    # print(current_position)
    # print(mix.shape)
    outdata[:, 0] = mix  # Write the mixed audio into the output buffer

    # Remove completed tracks from the active list
    active_tracks[:] = [(track, pos) for track, pos in active_tracks if pos < len(track)]

# Function to add a track at the current position
def add_track(track):
    global current_position
    print("Adding a new track...")
    active_tracks.append((track, current_position))  # Set the start position as the current global position

# Function to remove the last track
def remove_track():
    global active_tracks
    if active_tracks:
        print("Removing the last added track...")
        track_list.append(active_tracks.pop())
    else:
        print("No tracks to remove!")

# Main function
def main():
    global samplerate, current_position, track_list
    # Load audio files
    track1 = load_audio("Tides of Ocean_m1_1.wav")
    track2 = load_audio("Tides of Ocean_m2_1.wav")
    track3 = load_audio("Tides of Ocean_chord_1.wav")
    track4 = load_audio("Tides of Ocean_bass_1.wav")
    track_list = [track1, track2, track3, track4]

    # Start the audio stream
    print("Press '+' to add a track, '-' to remove the last track, and 'q' to quit.")
    stream = sd.OutputStream(callback=callback, samplerate=samplerate, channels=1, blocksize=buffer_size)

    try:
        with stream:
            while True:
                user_input = input("Enter command (+/-/q): ").strip()
                if user_input == "+":
                    if len(active_tracks) <= 3:
                        track_i = random.randrange(len(track_list))
                        add_track(track_list.pop(track_i))
                elif user_input == "-":
                    remove_track()
                elif user_input == "q":
                    print("Exiting program...")
                    break
                else:
                    print("Invalid input. Use '+' to add, '-' to remove, 'q' to quit.")
    except KeyboardInterrupt:
        print("\nPlayback stopped.")
    finally:
        print("Program exited.")

# Run the program
if __name__ == "__main__":
    main()
