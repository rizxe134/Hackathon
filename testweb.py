import cv2
cap = cv2.VideoCapture(0) # 0 is usually the first USB cam
while True:
    ret, frame = cap.read()
    cv2.imshow('USB Camera Preview', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): # Press 'q' to exit
        break
cap.release()
cv2.destroyAllWindows()
``` [11, 15]
