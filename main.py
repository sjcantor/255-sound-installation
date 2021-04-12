import numpy as np
# import cv2
from cv2 import cv2 # fuck you VS code
import random

# Playing Audio
import simpleaudio as sa

# Capture video from camera
cap = cv2.VideoCapture(0)

# Get an initial frame to measure difference when loop starts
_, lastframe = cap.read()

# Update lastframe every x frames
BUFFER = 10
# Frequencies
FREQ_ARRAY = np.array([440, 466.16, 493.88, 523.25, 554.37, 587.33, 622.25, 659.25, 698.46, 739.99, 783.99, 830.61, 880.00])


def get_intensity(input_arr):
    """
    Returns intensity of given array on a scale from 0 to 1
    """
    total = sum(input_arr)
    if total == 0:
        return 0

    # Use 40,000,000 for max intensity (number derived from experimentation)
    max_intensity = 40000000
    # Return the percentage of the input array with respect to the maximum intensity
    # Use the min() function with 1 to cap the percentage at 100%
    return min(total / max_intensity,  1)

def populate_note_array(intensity):
    """
    Given an intensity of the colors, fill elements in a 
    note array using the intensity as probability
    """
    # Notes array size (16 represents 2 bars with eight notes)
    size = 20
    notes = []

    for i in range(size):
        if random.random() <= intensity:
            notes.append(np.random.choice(FREQ_ARRAY))
        else:
            notes.append(0)
    
    return notes

def play_notes(notes, sample_rate=44100, T=0.1):

    t = np.linspace(0, T, int(T * sample_rate), False)

    # generate sine wave notes inside a tuple (this is UGLY)
    note_tuple = ()
    for freq in notes:
        new_note_tuple = note_tuple + (np.sin(freq * t * 2 * np.pi),)
        note_tuple = new_note_tuple

    # concatenate notes
    audio = np.hstack(note_tuple)
    # normalize to 16-bit range
    audio *= 32767 / np.max(np.abs(audio))
    # convert to 16-bit data
    audio = audio.astype(np.int16)

    # start playback
    play_obj = sa.play_buffer(audio, 1, 2, sample_rate)

    # wait for playback to finish before exiting
    # play_obj.wait_done()

def downsample(input_arr):
    # "Downsample" array to reasonable size
    # Let's use 8th notes, so 8 notes per bar
    # For 2 bars, sample 16 notes
    # Array of any size --> Array of size 16
    # while len(color_arr) > 32:
    #     # Cut out every other element
    #     color_arr = color_arr[::2]
    # while len(color_arr) > 16:
    #     # Remove the least bright color
    #     color_arr = np.delete(color_arr, color_arr.argmin())

    # 10% chance to set note to zero (to add spaces in our melodies)
    # for i in range(len(color_arr)):
    #     if random.random() < 0.1:
    #         color_arr[i] = 0
    pass



frame_count = 0

while(cap.isOpened()):
    # Take each frame
    _, frame = cap.read()
    frame_count += 1


    # Find difference between frames
    diff = cv2.absdiff(frame, lastframe)

    # Clip the lower color spectrum (close to black)
    # and clip whites (small motion changes)
    lower_bound = 60
    upper_bound = 230
    lower_black = np.array([lower_bound, lower_bound, lower_bound])
    upper_black = np.array([upper_bound, upper_bound, upper_bound])
    diff_mask = cv2.inRange(diff, lower_black, upper_black)
    diff = cv2.bitwise_and(diff, diff, mask=diff_mask)

    # Remove black pixels/0s
    color_arr = diff[np.nonzero(diff)]

    # Calculate "intensity" of array based on amount of color
    intensity = get_intensity(color_arr)

    # Create array of notes using intensity
    notes = populate_note_array(intensity)

    # Console output
    if len(color_arr > 0):
        print(f'intensity: {intensity}, note array: {notes}\n')

    # Graphics
    cv2.imshow('frame',frame)
    cv2.imshow('lastframe', lastframe)
    cv2.imshow('difference', diff)

    # Update reference point when buffer is reached
    if frame_count % BUFFER == 0:
        # Play notes
        play_notes(notes)
        
        lastframe = frame

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

# When everything done, release the capture
cap.release()

cv2.destroyAllWindows()