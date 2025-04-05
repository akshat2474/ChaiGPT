import sys
import os
import time
import pickle
import requests
import cv2
import face_recognition
from PIL import Image
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QImage

class CameraApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cap = None
        self.is_camera_running = False
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_face_encodings()  # Load face encodings at initialization

    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout()

        # Greeting and ASCII Art
        self.greeting_label = QtWidgets.QLabel("Welcome!\nHello, I am ChaiGPT")
        self.greeting_label.setAlignment(QtCore.Qt.AlignCenter)
        self.greeting_label.setWordWrap(True)
        self.layout.addWidget(self.greeting_label)

        self.ascii_art = QtWidgets.QLabel("╱|、 \n"
                                          "(˚ˎ 。7  \n"
                                          " |、˜〵   \n"
                                          "   じしˍ,)ノ")
        self.ascii_art.setAlignment(QtCore.Qt.AlignCenter)
        self.ascii_art.setStyleSheet("font-family: monospace;")
        self.layout.addWidget(self.ascii_art)

        # Login Section
        self.login_frame = QtWidgets.QGroupBox("Login")
        self.login_layout = QtWidgets.QVBoxLayout()
        self.login_frame.setLayout(self.login_layout)

        self.password_label = QtWidgets.QLabel("Enter Password:")
        self.login_layout.addWidget(self.password_label)

        self.password_entry = QtWidgets.QLineEdit()
        self.password_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_layout.addWidget(self.password_entry)

        self.password_button = QtWidgets.QPushButton("Submit Password")
        self.login_layout.addWidget(self.password_button)

        self.facial_recog_button = QtWidgets.QPushButton("Start Facial Recognition")
        self.login_layout.addWidget(self.facial_recog_button)

        self.login_layout.addStretch(1)

        self.layout.addWidget(self.login_frame)

        # Chatbot Section
        self.chatbot_frame = QtWidgets.QGroupBox("Chatbot")
        self.chatbot_layout = QtWidgets.QVBoxLayout()
        self.chatbot_frame.setLayout(self.chatbot_layout)

        self.cam_lbl = QtWidgets.QLabel()
        self.cam_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.chatbot_layout.addWidget(self.cam_lbl)

        self.status_lbl = QtWidgets.QLabel("")
        self.status_lbl.setStyleSheet("color: red;")
        self.chatbot_layout.addWidget(self.status_lbl)

        self.take_image_button = QtWidgets.QPushButton("Take Image")
        self.chatbot_layout.addWidget(self.take_image_button)

        self.upload_image_button = QtWidgets.QPushButton("Upload Image")
        self.chatbot_layout.addWidget(self.upload_image_button)

        self.chat_box = QtWidgets.QTextEdit()
        self.chat_box.setReadOnly(True)
        self.chatbot_layout.addWidget(self.chat_box)

        self.user_input = QtWidgets.QLineEdit()
        self.chatbot_layout.addWidget(self.user_input)

        self.send_button = QtWidgets.QPushButton("Send")
        self.chatbot_layout.addWidget(self.send_button)

        self.layout.addWidget(self.chatbot_frame)
        self.chatbot_frame.setVisible(False)

        self.setLayout(self.layout)

        # Connect buttons
        self.facial_recog_button.clicked.connect(self.start_facial_recognition)
        self.password_button.clicked.connect(self.verify_password)
        self.take_image_button.clicked.connect(self.capture_image)
        self.upload_image_button.clicked.connect(self.upload_image)
        self.send_button.clicked.connect(self.handle_send_message)

        self.user_input.installEventFilter(self)

    def load_face_encodings(self):
        # Load known face encodings and names from the pickle file
        with open('known_faces.pkl', 'rb') as f:
            self.known_face_encodings, self.known_face_names = pickle.load(f)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.KeyPress and
                event.key() == QtCore.Qt.Key_Return and source is self.user_input):
            self.handle_send_message()
            return True
        return super().eventFilter(source, event)

    def start_facial_recognition(self):
        self.login_frame.setVisible(False)  # Hide the login frame
        self.chatbot_frame.setVisible(True)  # Show chatbot frame
        self.start_camera()  # Start the camera feed

    def verify_password(self):
        entered_password = self.password_entry.text()
        if entered_password == 'ak':  # Replace with your actual password check
            self.start_facial_recognition()
        else:
            self.status_lbl.setText("Incorrect Password")

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.status_lbl.setText("Error: Camera could not be opened.")
            return
        self.is_camera_running = True
        self.update_camera()

    def update_camera(self):
        if self.is_camera_running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)  # Flip the image horizontally
                self.detect_face(frame)  # Face recognition functionality

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                q_img = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], frame_rgb.strides[0], QImage.Format_RGB888)
                self.cam_lbl.setPixmap(QtGui.QPixmap.fromImage(q_img))
            self.cam_lbl.setScaledContents(True)

            # Call this function again after a short delay
            QtCore.QTimer.singleShot(10, self.update_camera)

    def detect_face(self, frame):
        # Convert frame to RGB for face_recognition
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Get face locations and encodings
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare face with known faces
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.4)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]

            # Draw rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, f"Access Granted: {name}" if name != "Unknown" else "Access Denied",
                        (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

    def capture_image(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            pictures_dir = os.path.join(os.path.dirname(__file__), 'pictures')
            if not os.path.exists(pictures_dir):
                os.makedirs(pictures_dir)
            filename = f"captured_image_{int(time.time())}.jpg"
            file_path = os.path.join(pictures_dir, filename)
            cv2.imwrite(file_path, frame)
            self.status_lbl.setText(f"Image saved: {file_path}")

    def upload_image(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png;*.jpg;*.jpeg)", options=options)
        if file_path:
            img = Image.open(file_path)
            if file_path.lower().endswith(".png"):
                filename = f"converted_image_{int(time.time())}.jpg"
                img = img.convert("RGB")
                file_path = os.path.join(os.path.dirname(__file__), 'pictures', filename)
                img.save(file_path, "JPEG")
                self.status_lbl.setText(f"PNG image converted and saved as JPG: {file_path}")
            else:
                filename = f"uploaded_image_{int(time.time())}.jpg"
                file_path = os.path.join(os.path.dirname(__file__), 'pictures', filename)
                img.save(file_path)
                self.status_lbl.setText(f"Image saved: {file_path}")

    def handle_send_message(self):
        user_message = self.user_input.text()
        if user_message.strip() == "":
            return
        self.chat_box.append(f"You: {user_message}")
        self.user_input.clear()

        response = self.get_chatbot_response(user_message)
        self.chat_box.append(f"ChaiGPT: {response}")

    def get_chatbot_response(self, user_message):
        # Send message to your chatbot API here, return response
        return "I'm a chatbot, how can I assist you?"

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    camera_app = CameraApp()
    camera_app.show()
    sys.exit(app.exec_())

