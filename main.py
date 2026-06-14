import cv2
import numpy as np
import time
import os

from hand_tracker import HandDetector
from utils import draw_header, draw_footer, save_canvas


WIDTH, HEIGHT = 1100, 620
DRAW_TOP = 160
DRAW_BOTTOM = HEIGHT - 95

cap = cv2.VideoCapture(0)
cap.set(3, WIDTH)
cap.set(4, HEIGHT)

cv2.namedWindow("AirScript", cv2.WINDOW_NORMAL)
cv2.resizeWindow("AirScript", WIDTH, HEIGHT)

detector = HandDetector(max_hands=2, detection_confidence=0.7, tracking_confidence=0.7)

colors = [
    ((255, 0, 0), "BLUE"),
    ((0, 255, 0), "GREEN"),
    ((0, 0, 255), "RED"),
    ((0, 0, 0), "BLACK"),
    ((0, 255, 255), "YELLOW"),
    ((255, 0, 255), "PURPLE"),
    ((0, 165, 255), "ORANGE"),
]

current_color = colors[0][0]
current_color_name = colors[0][1]
current_tool = "PEN"

canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
canvas_mask = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)

mode = "HOME"
previous_draw_point = None
previous_drag_point = None
previous_time = 0

save_cooldown = 0
clear_cooldown = 0
paint_cooldown = 0
fill_cooldown = 0

os.makedirs("drawings", exist_ok=True)


def combine_canvas_with_frame(frame, canvas_layer, mask_layer):
    mask_inverse = cv2.bitwise_not(mask_layer)
    frame_background = cv2.bitwise_and(frame, frame, mask=mask_inverse)
    canvas_foreground = cv2.bitwise_and(canvas_layer, canvas_layer, mask=mask_layer)
    return cv2.add(frame_background, canvas_foreground)


def move_canvas(canvas_layer, mask_layer, dx, dy):
    matrix = np.float32([[1, 0, dx], [0, 1, dy]])
    moved_canvas = cv2.warpAffine(canvas_layer, matrix, (WIDTH, HEIGHT))
    moved_mask = cv2.warpAffine(mask_layer, matrix, (WIDTH, HEIGHT))
    return moved_canvas, moved_mask


def flood_fill_shape(seed_x, seed_y, color):
    global canvas, canvas_mask

    if seed_y < DRAW_TOP or seed_y > DRAW_BOTTOM:
        return

    if canvas_mask[seed_y, seed_x] > 0:
        return

    fill_area = cv2.bitwise_not(canvas_mask)
    fill_area[:DRAW_TOP, :] = 0
    fill_area[DRAW_BOTTOM:, :] = 0

    temp = fill_area.copy()
    flood_mask = np.zeros((HEIGHT + 2, WIDTH + 2), dtype=np.uint8)

    cv2.floodFill(temp, flood_mask, (seed_x, seed_y), 128)

    region = temp == 128

    if np.count_nonzero(region) < 20:
        return

    canvas[region] = color
    canvas_mask[region] = 255


while True:
    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (WIDTH, HEIGHT))

    frame = detector.find_hands(frame, draw=True)
    hands = detector.get_all_hands(frame)

    eraser_radius = 40
    eraser_hands = []

    for hand in hands:
        if hand["gesture"] == "ERASE":
            eraser_hands.append(hand)

    now = time.time()

    if eraser_hands:
        mode = "ERASE"
        previous_draw_point = None
        previous_drag_point = None

        for hand in eraser_hands:
            palm_x, palm_y = hand["palm"]
            cv2.circle(canvas, (palm_x, palm_y), eraser_radius, (0, 0, 0), -1)
            cv2.circle(canvas_mask, (palm_x, palm_y), eraser_radius, 0, -1)

    elif hands:
        hand = hands[0]

        gesture = hand["gesture"]
        landmarks = hand["landmarks"]

        pointer_x, pointer_y = landmarks[8][1], landmarks[8][2]
        palm_x, palm_y = hand["palm"]

        if gesture == "DRAW":
            previous_drag_point = None

            if current_tool == "PAINT":
                mode = "PAINT READY"

                if hand["pinching"] and now - fill_cooldown > 0.8:
                    flood_fill_shape(pointer_x, pointer_y, current_color)
                    fill_cooldown = now
                    mode = "PAINT FILL"

            else:
                if hand["pinching"]:
                    mode = "WRITING"

                    if previous_draw_point is None:
                        previous_draw_point = (pointer_x, pointer_y)

                    cv2.line(canvas, previous_draw_point, (pointer_x, pointer_y), current_color, 7)
                    cv2.line(canvas_mask, previous_draw_point, (pointer_x, pointer_y), 255, 7)

                    previous_draw_point = (pointer_x, pointer_y)
                else:
                    mode = "DRAW READY"
                    previous_draw_point = None

            cv2.circle(frame, (pointer_x, pointer_y), 10, current_color, -1)

        elif gesture == "COLOR":
            mode = "COLOR"
            previous_draw_point = None
            previous_drag_point = None

            for i, (color, name) in enumerate(colors):
                cx = 45 + i * 70
                cy = 105

                if cx - 28 < pointer_x < cx + 28 and cy - 28 < pointer_y < cy + 28:
                    current_color = color
                    current_color_name = name
                    current_tool = "PEN"

            if 600 < pointer_x < 710 and 85 < pointer_y < 130:
                if now - clear_cooldown > 1:
                    canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
                    canvas_mask = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
                    clear_cooldown = now

            if 730 < pointer_x < 840 and 85 < pointer_y < 130:
                if now - save_cooldown > 2:
                    save_canvas(canvas)
                    save_cooldown = now

            if 860 < pointer_x < 990 and 85 < pointer_y < 130:
                if now - paint_cooldown > 1:
                    current_tool = "PAINT" if current_tool == "PEN" else "PEN"
                    paint_cooldown = now

        elif gesture == "MOVE":
            mode = "MOVE"
            previous_draw_point = None

            if previous_drag_point is None:
                previous_drag_point = (palm_x, palm_y)

            dx = palm_x - previous_drag_point[0]
            dy = palm_y - previous_drag_point[1]

            if abs(dx) > 2 or abs(dy) > 2:
                canvas, canvas_mask = move_canvas(canvas, canvas_mask, dx, dy)

            previous_drag_point = (palm_x, palm_y)

        else:
            mode = "HOME"
            previous_draw_point = None
            previous_drag_point = None

    else:
        mode = "HOME"
        previous_draw_point = None
        previous_drag_point = None

    output = combine_canvas_with_frame(frame, canvas, canvas_mask)

    draw_header(output, colors, current_tool)

    current_time = time.time()
    fps = int(1 / (current_time - previous_time)) if previous_time else 0
    previous_time = current_time

    draw_footer(output, mode, current_color, current_color_name, fps, current_tool)

    for hand in eraser_hands:
        palm_x, palm_y = hand["palm"]
        cv2.circle(output, (palm_x, palm_y), eraser_radius, (0, 0, 255), 3)

    screenshot_frame = output.copy()

    cv2.imshow("AirScript", output)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    if key == ord("s"):
        cv2.imwrite(f"drawings/screenshot_{int(time.time())}.png", screenshot_frame)

cap.release()
cv2.destroyAllWindows()