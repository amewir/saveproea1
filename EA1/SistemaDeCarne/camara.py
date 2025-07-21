import cv2

# Check available cameras
for i in range(0, 3):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera found at index {i}")
        ret, frame = cap.read()
        if ret:
            print(f"Frame size: {frame.shape[1]}x{frame.shape[0]}")
        cap.release()
    else:
        print(f"No camera at index {i}")