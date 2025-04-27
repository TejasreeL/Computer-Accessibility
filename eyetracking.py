import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize camera and face mesh
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# Screen size and cursor init
screen_w, screen_h = pyautogui.size()
screen_x, screen_y = screen_w // 2, screen_h // 2
SMOOTHING = 1.3
DEADZONE = 1

# Blink thresholds
BLINK_THRESHOLD = 0.0035

# Scroll settings
scroll_start_top = None
scroll_start_bottom = None
scroll_delay = 1.0  # seconds

while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    current_time = time.time()

    if output.multi_face_landmarks:
        landmarks = output.multi_face_landmarks[0].landmark
        frame_h, frame_w, _ = frame.shape

        # --- Eye Landmarks ---
        LEFT_EYE_TOP = 159
        LEFT_EYE_BOTTOM = 145
        RIGHT_EYE_TOP = 386
        RIGHT_EYE_BOTTOM = 374

        # Get eye positions
        left_top = landmarks[LEFT_EYE_TOP].y
        left_bottom = landmarks[LEFT_EYE_BOTTOM].y
        right_top = landmarks[RIGHT_EYE_TOP].y
        right_bottom = landmarks[RIGHT_EYE_BOTTOM].y

        left_eye_ratio = abs(left_top - left_bottom)
        right_eye_ratio = abs(right_top - right_bottom)

        # Detect blinks
        left_blink = left_eye_ratio < BLINK_THRESHOLD
        right_blink = right_eye_ratio < BLINK_THRESHOLD

        # --- Blink Actions ---
        if left_blink and not right_blink:
            print("🖱️ Left click")
            pyautogui.click(button='left')
            pyautogui.sleep(0.2)
        elif right_blink and not left_blink:
            print("🖱️ Right click")
            pyautogui.click(button='right')
            pyautogui.sleep(0.2)
        elif left_blink and right_blink:
            # Both eyes blink (do nothing)
            pass

        # Draw eye points for debugging
        for idx in [LEFT_EYE_TOP, LEFT_EYE_BOTTOM, RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM]:
            x = int(landmarks[idx].x * frame_w)
            y = int(landmarks[idx].y * frame_h)
            cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)

        # --- Iris Tracking (Points 474-477) ---
        for id, landmark in enumerate(landmarks[474:478]):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            if id == 1:
                # Convert to screen coords
                new_x = int(landmark.x * screen_w)
                new_y = int(landmark.y * screen_h)

                # Smooth movement
                screen_x += int((new_x - screen_x) * SMOOTHING)
                screen_y += int((new_y - screen_y) * SMOOTHING)

                screen_x = max(DEADZONE, min(screen_w - DEADZONE, screen_x))
                screen_y = max(DEADZONE, min(screen_h - DEADZONE, screen_y))

                pyautogui.moveTo(screen_x, screen_y)

                # Scroll detection using iris.y
                iris_y = landmark.y
                if iris_y < 0.1:  # Top of frame
                    if scroll_start_top is None:
                        scroll_start_top = current_time
                    elif current_time - scroll_start_top > scroll_delay:
                        print("🔼 Scroll Up")
                        pyautogui.press('up')  # fallback scroll
                        scroll_start_top = current_time
                else:
                    scroll_start_top = None

                if iris_y > 0.9:  # Bottom of frame
                    if scroll_start_bottom is None:
                        scroll_start_bottom = current_time
                    elif current_time - scroll_start_bottom > scroll_delay:
                        print("🔽 Scroll Down")
                        pyautogui.press('down')  # fallback scroll
                        scroll_start_bottom = current_time
                else:
                    scroll_start_bottom = None

    # Show camera feed
    cv2.imshow("Eye Controlled Mouse", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key to quit
        break

cam.release()
cv2.destroyAllWindows()
