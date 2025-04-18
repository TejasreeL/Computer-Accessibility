import cv2
import mediapipe as mp
import pyautogui

# Initialize camera
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# Screen and tracking parameters
screen_w, screen_h = pyautogui.size()
screen_x, screen_y = screen_w // 2, screen_h // 2  # Start at center
SMOOTHING = 1.3  # Lower = faster response (1.0-1.5 recommended)
DEADZONE = 1    # 1px soft border
BOUNCE_BACK = 5 # How far cursor rebounds from edges

while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    
    if output.multi_face_landmarks:
        landmarks = output.multi_face_landmarks[0].landmark
        frame_h, frame_w, _ = frame.shape
        
        # Iris tracking (points 474-477)
        for id, landmark in enumerate(landmarks[474:478]):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            
            if id == 1:  # Primary tracking point
                # Convert to screen coordinates
                new_x = int(landmark.x * screen_w)
                new_y = int(landmark.y * screen_h)
                
                # Apply smoothing
                screen_x += int((new_x - screen_x) * SMOOTHING)
                screen_y += int((new_y - screen_y) * SMOOTHING)
                
                # 1px boundary control with bounce
                screen_x = max(DEADZONE, min(screen_w - DEADZONE, screen_x))
                screen_y = max(DEADZONE, min(screen_h - DEADZONE, screen_y))
                
                # Move cursor
                pyautogui.moveTo(screen_x, screen_y)
        
        # Blink detection (points 145 & 159)
        left_eye = [landmarks[145], landmarks[159]]
        for landmark in left_eye:
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)
            
        # Click when eyes close (threshold adjustable)
        if (left_eye[0].y - left_eye[1].y) < 0.004:
            pyautogui.click()
            pyautogui.sleep(0.2)  # Debounce delay
    
    # Display
    cv2.imshow("Eye Controlled Mouse", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cam.release()
cv2.destroyAllWindows()