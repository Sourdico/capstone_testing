import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from playsound import playsound
import time
import ctypes
#import for speech recognition
import speech_recognition as sr
import sounddevice as sd
import soundfile as sf

from threading import Thread
import random
import time
# Rest of our code
global audio_file_name
rec_word = False
global record_is_processing
YesBaby = 0
No = 0

def play_audio():
    playsound(audio_file_name)
    
################################

# Initialize the recognizer
r = sr.Recognizer()

# Variable to indicate whether recording is in progress
recording_in_progress = False

# Function to recognize words from voice input
def recognize_words():
    global recording_in_progress

    with sd.InputStream(callback=process_audio):
        print("Speak a word (top, bottom, left, right):")

        recording_in_progress = True
        print("Recording...")

        recording = sd.rec(int(5 * 16000), samplerate=16000, channels=1)
        sd.wait()

        recording_in_progress = False
        print("Recording finished.")

        sf.write('audio.wav', recording, 16000)

        try:
            audio = sr.AudioFile('audio.wav')
            with audio as source:
                audio_data = r.record(source)

            print("Processing...")

            word = r.recognize_google(audio_data)
            if word.lower() in ["top", "bottom", "left", "right"]:
                global rec_word
                rec_word=word
                print("You said:", word)
            else:
                print("Please speak one of the specified words: top, bottom, left, right.")
        except sr.UnknownValueError:
            print("Sorry, I could not understand your speech.")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        except FileNotFoundError:
            print("Audio file not found.")
    global record_is_processing
    record_is_processing=False
        

# Callback function for processing audio data
def process_audio(indata, frames, time, status):
    if recording_in_progress:
        print(".", end='', flush=True)

################################
def display_image(image_path, size_cm):
    print(image_path)
    img = cv2.imread(image_path)

    # Calculate the new size in pixels
    new_width = int(size_cm / 2.54 * img.shape[1])
    new_height = int(size_cm / 2.54 * img.shape[0])

    # Resize the image to the desired size
    img = cv2.resize(img, (new_width, new_height))

    cv2.imshow("Image", img)
    cv2.waitKey(1)

def hide_image():
    cv2.destroyWindow("Image")

def random_image():
    image_names = ['top', 'left', 'right', 'bottom']
    return random.choice(image_names)


def check_distance_and_display_image(d_ft, show_image, image_folder, image_file, image_size_cm):
    global recording_in_progress
    global rec_word
    #global YesBaby
    #global No
    accurate_word = random_image()
    if d_ft >= 5:
        if not show_image:
            show_image = True
            #time.sleep(1)
            display_image(image_folder + accurate_word + '.png', image_size_cm)
        if not recording_in_progress:
         recording_in_progress=True
         T = Thread(target=recognize_words)
         T.start()                 
    else:
        if show_image:
            show_image = False
            hide_image()
    
    if rec_word and accurate_word:
        print('recorded word: ', rec_word)
        if rec_word == accurate_word:
            YesBaby += 1
            print('Yes ')
        else:
            No += 1
            print('No ')
        rec_word = None
        
    return show_image

def face_detection():
    cap = cv2.VideoCapture(1)
    detector = FaceMeshDetector(maxFaces=1)
    audio_file = "Audio/please_get_into_the_camera_frame.wav"
    image_folder = "Image/"
    image_file = "left.png"
    no_face_detected_time = None
    W, f = 6.3, 840
    show_image = False
    image_size_cm = 0.6  # Desired image size in centimeters

    while True:
        success, img = cap.read()
        img, faces = detector.findFaceMesh(img, draw=False)

        if not faces:
            if no_face_detected_time is None:
                no_face_detected_time = time.time()
            else:
                current_time = time.time()
                if current_time - no_face_detected_time >= 5:
                    no_face_detected_time = current_time+4
                    global audio_file_name
                    audio_file_name = audio_file
                    T= Thread(target=play_audio)
                    T.start()
                    
                show_image = check_distance_and_display_image(d_ft, show_image, image_folder, image_file, image_size_cm)
        else:
            no_face_detected_time = None
            face = faces[0]

            pointLeft = face[145]
            pointRight = face[374]
            w, _ = detector.findDistance(pointLeft, pointRight)
            d_cm = (W * f) / w
            d_ft, d_in = convert_cm_to_feet_inches(d_cm)

            show_image = check_distance_and_display_image(d_ft, show_image, image_folder, image_file, image_size_cm)
            display_depth(img, d_cm, d_ft, d_in, face)

        cv2.imshow("Video", img)
        cv2.waitKey(1)
        print(YesBaby,' ',No)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def convert_cm_to_feet_inches(cm):
    # 1 foot = 30.48 cm, 1 inch = 2.54 cm
    total_inches = cm / 2.54
    feet = int(total_inches // 12)
    inches = int(total_inches % 12)
    return feet, inches

def display_depth(img, depth_cm, depth_ft, depth_in, face):
    if depth_ft <= 5:
        depth_text = f' Speak {int(depth_cm)}cm ({depth_ft}\'{depth_in}\'\')'
    else:
        depth_text = f'{int(depth_cm)}cm ({depth_ft}\'{depth_in}\'\')'

    cv2.putText(img, depth_text, (face[10][0] - 100, face[10][1] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

def main():
    face_detection()

if __name__ == "__main__":
    main()
