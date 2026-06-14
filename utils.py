import cv2
import time
import tkinter as tk
from tkinter import filedialog


def draw_header(frame, colors, current_tool):
    height, width, _ = frame.shape

    cv2.rectangle(frame, (0, 0), (width, 160), (245, 245, 245), -1)

    cv2.putText(frame, "AirScript", (20, 38), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (20, 20, 20), 3)
    cv2.putText(frame, "Gesture Based Virtual Writing System", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (70, 70, 70), 2)

    for i, (color, name) in enumerate(colors):
        cx = 45 + i * 70
        cy = 105
        cv2.circle(frame, (cx, cy), 23, color, -1)
        cv2.circle(frame, (cx, cy), 23, (40, 40, 40), 2)

    cv2.rectangle(frame, (600, 85), (710, 130), (230, 230, 230), -1)
    cv2.rectangle(frame, (600, 85), (710, 130), (80, 80, 80), 2)
    cv2.putText(frame, "CLEAR", (615, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 20, 20), 2)

    cv2.rectangle(frame, (730, 85), (840, 130), (230, 230, 230), -1)
    cv2.rectangle(frame, (730, 85), (840, 130), (80, 80, 80), 2)
    cv2.putText(frame, "SAVE", (760, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 20, 20), 2)

    paint_fill = (180, 230, 255) if current_tool == "PAINT" else (230, 230, 230)
    cv2.rectangle(frame, (860, 85), (990, 130), paint_fill, -1)
    cv2.rectangle(frame, (860, 85), (990, 130), (80, 80, 80), 2)
    cv2.putText(frame, "PAINT", (885, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 20, 20), 2)


def draw_footer(frame, mode, current_color, current_color_name, fps, current_tool):
    height, width, _ = frame.shape

    cv2.rectangle(frame, (0, height - 95), (width, height), (245, 245, 245), -1)

    cv2.putText(frame, f"MODE : {mode}", (20, height - 55), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (20, 20, 20), 2)
    cv2.putText(frame, f"TOOL : {current_tool}", (320, height - 55), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (20, 20, 20), 2)

    cv2.putText(frame, "CURRENT COLOR :", (20, height - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 20, 20), 2)
    cv2.circle(frame, (245, height - 30), 14, current_color, -1)
    cv2.circle(frame, (245, height - 30), 14, (40, 40, 40), 2)

    cv2.putText(frame, current_color_name, (270, height - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (20, 20, 20), 2)
    cv2.putText(frame, f"FPS : {fps}", (width - 145, height - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 20, 20), 2)


def save_canvas(canvas):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    filename = filedialog.asksaveasfilename(
        title="Save AirScript Drawing",
        defaultextension=".png",
        filetypes=[
            ("PNG Image", "*.png"),
            ("JPEG Image", "*.jpg"),
            ("All Files", "*.*"),
        ],
        initialfile=f"airscript_{int(time.time())}.png",
    )

    root.destroy()

    if filename:
        cv2.imwrite(filename, canvas)
        return filename

    return None