import cv2

print(cv2.__version__)


def identificar_rosto(imagem):
    classificador_face = cv2.CascadeClassifier("classifier/haarcascade_frontalface_default.xml")

    imagem_gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    faces = classificador_face.detectMultiScale(imagem_gray, 1.3, 5)

    for (x,y,w,h) in faces:
        cv2.rectangle(imagem, (x,y), (x+w,y+h), (127,0,255), 2)

    return imagem

cam = cv2.VideoCapture(0)

while True:
    
    cap, frame = cam.read()
    if cap:
        frame = identificar_rosto(frame)
        cv2.imshow("cam", frame)
        
        frame = cv2.resize(frame, None, fx=3, fy=3, interpolation=cv2.INTER_LANCZOS4)
        cv2.imwrite("test.jpg", frame)
    
    if cv2.waitKey(1) == 13:
        break
    
cam.release()
cv2.destroyAllWindows()
