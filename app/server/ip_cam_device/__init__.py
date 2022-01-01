import time
from fastapi import HTTPException

from app.models.domain.Error_handler import UnicornException

import cv2

from app.server.detector.Maskdetector import Maskdetector
from app.server.detector.detector import detector

widthResolution = 1280
Resolution = widthResolution / 1280.0
Resolution = 1
fontSize = 48 * Resolution
Round = 20 * Resolution
LineWidth = 2 * Resolution
top = 4 * Resolution
bottom = 4 * Resolution
left = 8 * Resolution
right = 8 * Resolution
pitch = 4 * Resolution
# fontStyle = new Font("Arial", fontsize)
fillRectangleWidth = 180 + left + right;
fillRectangleHeight = 34 + top + bottom;
fillRectangleWidth = fillRectangleWidth * Resolution
fillRectangleHeight = fillRectangleHeight * Resolution


def ip_cam_video_stream(ip: str,
                        port: str,
                        username: str,
                        password: str,
                        stream_name: str):
    try:
        # cap = cv2.VideoCapture("rtsp://root:a1234567@192.168.68.110:554/live1s1.sdp")
        # cap = cv2.VideoCapture(0)
        connect_url = "rtsp://" + username + ":" + password + "@" + ip + ":" + port + "/" + stream_name
        # connect_url = "rtsp://syno:8a5f6849df7afcc21decc4f6a14253a7@192.168.45.211:554/Sms=1.unicast"
        # connect_url = "rtsp://syno:750345c82f060ce8d6662dcc1ec6c86c@192.168.45.211:554/Sms=2.unicast"
        cap = cv2.VideoCapture(0)
        pTime = 0
        while True:
            success, img = cap.read()
            # imgRGB = img
            imgRGB = cv2.flip(img, 1, dst=None)
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(imgRGB, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN,
                        3, (0, 255, 0), 2)
            frame = cv2.imencode('.jpg', imgRGB)[1].tobytes()
            yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
    except Exception as e:
        print(str(e))
        raise UnicornException(name=ip_cam_video_stream.__name__, description=str(e), status_code=500)


def ip_cam_face_detect_stream(ip: str,
                              port: str,
                              username: str,
                              password: str,
                              stream_name: str):
    connect_url = "rtsp://" + username + ":" + password + "@" + ip + ":" + port + "/" + stream_name
    # cap = cv2.VideoCapture(connect_url)
    cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture("C:/Users/ricky/Desktop/videoplayback.mp4")
    pTime = 0
    count = 0
    # mpFaceDetection = mp.solutions.face_detection
    # mpDraw = mp.solutions.drawing_utils
    # faceDetection = mpFaceDetection.FaceDetection(0.75)
    # name_file = "name"
    # for i in range(5):
    #     if os.path.isfile(name_file + str(i) + ".txt"):
    #         os.remove(name_file + str(i) + ".txt")
    # Initialize some variables
    # frame_count = 0
    width = cap.get(3)  # float `width`
    height = cap.get(4)  # float `height`
    size = width, height
    det = detector(size=size)
    Maskdet = Maskdetector()
    while True:
        try:

            success, img = cap.read()
            imgRGB = cv2.flip(img, 1, dst=None)
            # imgRGB = img
            faces = det.forward(imgRGB)

            for bbox in faces:

                faceLeft = bbox[0]
                faceUp = bbox[1]
                faceRight = bbox[2]
                faceDown = bbox[3]

                if faceLeft <= 0:
                    faceLeft = 0

                if faceUp <= 0:
                    faceUp = 0

                face_image = imgRGB[faceUp:faceDown, faceLeft:faceRight]

                # cv2.imwrite('output'+str(count)+'.jpg', face_image)
                result = Maskdet.forward(face_image)
                # print(result)
                # print(bbox)
                cv2.rectangle(imgRGB, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)

                faceCenter = int((faceLeft + faceRight) / 2)
                if result:
                    fillRectangleX = 250
                    withMask = "With Mask"
                    color = (0, 255, 0)
                else:
                    fillRectangleX = 210
                    withMask = "No Mask"
                    color = (0, 0, 255)

                cv2.rectangle(imgRGB,
                              (faceCenter - int(fillRectangleX / 2), faceDown + LineWidth + pitch),
                              (faceCenter + int(fillRectangleX / 2), faceDown + LineWidth + pitch + fontSize),
                              color, -1)

                # cv2.putText(imgRGB, withMask, (faceLeft+left, faceDown + LineWidth + pitch+up), cv2.FONT_HERSHEY_DUPLEX, fontSize, (255, 255, 255), 1,
                #             cv2.LINE_AA)
                cv2.putText(imgRGB, withMask, (faceCenter - int(fillRectangleX / 2), faceDown + fontSize),
                            cv2.FONT_HERSHEY_DUPLEX,
                            1.5, (255, 255, 255), 2)

            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(imgRGB, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN,
                        3, (0, 255, 0), 2)
            frame = cv2.imencode('.jpg', imgRGB)[1].tobytes()

            count += 1
            yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        except Exception as e:
            print(str(e))
            continue
            # raise UnicornException(name=ip_cam_video_stream.__name__, description=str(e), status_code=500)
