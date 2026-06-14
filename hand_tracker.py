import cv2
import mediapipe as mp
import math


class HandDetector:
    def __init__(self, max_hands=2, detection_confidence=0.7, tracking_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            model_complexity=1,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

        self.results = None

    def find_hands(self, frame, draw=True):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)

        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=3),
                    self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2),
                )

        return frame

    def get_all_hands(self, frame):
        if not self.results or not self.results.multi_hand_landmarks:
            return []

        height, width, _ = frame.shape
        detected_hands = []

        for hand_landmarks in self.results.multi_hand_landmarks:
            landmarks = []

            for landmark_id, landmark in enumerate(hand_landmarks.landmark):
                cx = int(landmark.x * width)
                cy = int(landmark.y * height)
                landmarks.append([landmark_id, cx, cy])

            x_values = [point[1] for point in landmarks]
            y_values = [point[2] for point in landmarks]
            area = (max(x_values) - min(x_values)) * (max(y_values) - min(y_values))

            palm_x = int((landmarks[0][1] + landmarks[5][1] + landmarks[9][1] + landmarks[13][1] + landmarks[17][1]) / 5)
            palm_y = int((landmarks[0][2] + landmarks[5][2] + landmarks[9][2] + landmarks[13][2] + landmarks[17][2]) / 5)

            fingers = self.count_fingers(landmarks)
            pinching = self.is_pinching(landmarks)
            gesture = self.classify_gesture(fingers)

            detected_hands.append(
                {
                    "landmarks": landmarks,
                    "area": area,
                    "palm": (palm_x, palm_y),
                    "fingers": fingers,
                    "gesture": gesture,
                    "pinching": pinching,
                }
            )

        detected_hands.sort(key=lambda hand: hand["area"], reverse=True)
        return detected_hands

    def distance(self, point1, point2):
        return math.hypot(point1[1] - point2[1], point1[2] - point2[2])

    def is_pinching(self, landmarks):
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        index_mcp = landmarks[5]
        wrist = landmarks[0]

        pinch_distance = self.distance(thumb_tip, index_tip)
        hand_size = self.distance(wrist, index_mcp)

        return pinch_distance < hand_size * 0.65

    def is_finger_up(self, landmarks, tip, pip, mcp):
        palm = landmarks[0]
        tip_point = landmarks[tip]
        pip_point = landmarks[pip]
        mcp_point = landmarks[mcp]

        tip_above_pip = tip_point[2] < pip_point[2] + 15
        tip_far_from_palm = self.distance(tip_point, palm) > self.distance(pip_point, palm) + 15
        tip_above_mcp = tip_point[2] < mcp_point[2] - 15

        return tip_above_pip and (tip_far_from_palm or tip_above_mcp)

    def count_fingers(self, landmarks):
        fingers = [0, 0, 0, 0, 0]

        wrist = landmarks[0]
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]

        if self.distance(thumb_tip, wrist) > self.distance(thumb_ip, wrist) + 25:
            fingers[0] = 1

        fingers[1] = 1 if self.is_finger_up(landmarks, 8, 6, 5) else 0
        fingers[2] = 1 if self.is_finger_up(landmarks, 12, 10, 9) else 0
        fingers[3] = 1 if self.is_finger_up(landmarks, 16, 14, 13) else 0
        fingers[4] = 1 if self.is_finger_up(landmarks, 20, 18, 17) else 0

        return fingers

    def classify_gesture(self, fingers):
        thumb, index, middle, ring, pinky = fingers

        if thumb and index and middle and ring and pinky:
            return "ERASE"

        if index and middle and ring and not pinky:
            return "MOVE"

        if thumb and index and middle and not ring and not pinky:
            return "MOVE"

        if index and middle and not ring and not pinky:
            return "COLOR"

        if index and not middle and not ring and not pinky:
            return "DRAW"

        return "HOME"