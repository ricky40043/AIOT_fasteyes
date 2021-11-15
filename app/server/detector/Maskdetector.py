import os
import cv2
import time

import numpy as np

from app.server.detector.priorbox import PriorBox
from app.server.detector.utils import nms


def get_input_shape(fname: str):
    w = int(fname[:-5].split('_')[-1])
    h = int(0.75 * w)
    return (w, h)


class Maskdetector(object):
    def __init__(self, size=(100, 100)):
        modelPath = "app/server/detector/MaskDetector.onnx"

        # Load the net
        self.net = cv2.dnn.readNet(modelPath)
        self.input_shape = size
        # build the blob
        self.pb = PriorBox(input_shape=self.input_shape, output_shape=(1, 1))

    def forward(self, frame):
        blob = cv2.dnn.blobFromImage(frame, 0.003921568627451,
                                     size=self.input_shape)  # 'size' param resize the output to the given shape

        self.net.setInput(blob)

        t = time.time()
        dets = self.net.forward()
        # print("Elapsed time: {}".format(time.time() - t))
        result = dets[0, 1] > dets[0, 0]
        return result


if __name__ == '__main__':
    # load videocapture
    cap = cv2.VideoCapture(0)
    det = Maskdetector()

    while cap.isOpened:
        _, frame = cap.read()

        faces = det.forward(frame)

        for bbox in faces:
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        cv2.imshow('Detection Results', frame)
        cv2.waitKey(33)

    cv2.destroyAllWindows()
