import cv2
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import img_to_array
from flask import Flask
import numpy as np

root_path = os.path.dirname(os.path.abspath(__file__))
face_classifier = cv2.CascadeClassifier(f'{root_path}/static/haarcascade.xml')
classifier = load_model(f'{root_path}/static/model.h5')
emotion_labels = ['Happy', 'Neutral', 'Sad']


class Video(object):
    def __init__(self):
        self.folder_count = {}
        if os.environ.get('WERKZEUG_RUN_MAIN') or Flask.debug is False:
            self.camera = cv2.VideoCapture(0)
            if not (self.camera.isOpened()):
                print("Could not open video device")
            # Set the resolution
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    def __del__(self):
        self.camera.release()

    def get_frame(self, reset_predictions):
        try:
            success, frame = self.camera.read()
            if success:
                faces = face_classifier.detectMultiScale(frame, 1.3, 5)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                for x, y, w, h in faces:
                    x1, y1 = x+w, y+h
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 255), 1)

                    cv2.line(frame, (x, y), (x+30, y), (255, 0, 255), 6)
                    cv2.line(frame, (x, y), (x, y+30), (255, 0, 255), 6)

                    cv2.line(frame, (x1, y), (x1-30, y), (255, 0, 255), 6)
                    cv2.line(frame, (x1, y), (x1, y+30), (255, 0, 255), 6)

                    cv2.line(frame, (x, y1), (x+30, y1), (255, 0, 255), 6)
                    cv2.line(frame, (x, y1), (x, y1-30), (255, 0, 255), 6)

                    cv2.line(frame, (x1, y1), (x1-30, y1), (255, 0, 255), 6)
                    cv2.line(frame, (x1, y1), (x1, y1-30), (255, 0, 255), 6)

                    roi_gray = gray[y:y + h, x:x + w]
                    roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
                    if np.sum([roi_gray]) != 0:
                        roi = roi_gray.astype('float') / 255.0
                        roi = img_to_array(roi)
                        roi = np.expand_dims(roi, axis=0)
                        prediction = classifier.predict(roi)[0]
                        label = emotion_labels[prediction.argmax()]
                    else:
                        label = "None"

                    if label in self.folder_count:
                        self.folder_count[label] += 1
                    elif reset_predictions:
                        self.folder_count.clear()
                    else:
                        self.folder_count[label] = 1

                    ret, jpg = cv2.imencode('.jpg', frame)
                    return jpg.tobytes()
        except Exception as exp:
            print(exp)

    def get_label(self):
        return self.folder_count

    def reset_label(self):
        return self.folder_count.clear()