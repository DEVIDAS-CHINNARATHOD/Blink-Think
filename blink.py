import cv2
import pyttsx3
import time
import threading

# Initialize text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    threading.Thread(target=lambda: engine.say(text) or engine.runAndWait()).start()

# Haar cascade for face and eyes
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Video capture
cap = cv2.VideoCapture(0)

blink_times = []
eye_closed_time = None
action_taken = None  # 'food' or 'water'

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    eyes_detected = False
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        if len(eyes) >= 1:
            eyes_detected = True
            break

    current_time = time.time()

    if not eyes_detected:
        if eye_closed_time is None:
            eye_closed_time = current_time
    else:
        if eye_closed_time is not None:
            duration = current_time - eye_closed_time

            if duration >= 2 and action_taken != "food":
                # Eye closed for 2+ seconds = Food
                cv2.putText(frame, "Food", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                speak("Food kavali")
                action_taken = "food"
                blink_times.clear()  # reset
            elif duration < 1:


                
                # A quick blink
                blink_times.append(current_time)
                blink_times = [t for t in blink_times if current_time - t < 1.2]
                if len(blink_times) >= 2 and action_taken != "water":
                    cv2.putText(frame, "Water", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)
                    speak("Water kavali")
                    action_taken = "water"
                    blink_times.clear()

            eye_closed_time = None

    # Reset action after a few seconds
    if action_taken and (time.time() - (eye_closed_time or current_time) > 5):
        action_taken = None

    if action_taken:
        cv2.putText(frame, action_taken.capitalize(), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (200, 200, 255), 3)

    cv2.imshow("Blink-to-Speech", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
