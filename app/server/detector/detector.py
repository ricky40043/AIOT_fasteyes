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


class detector(object):
    def __init__(self, confTh=0.85, nmsTh=0.3, size=(640, 480)):

        modelPath = "app/server/detector/YuFaceDetectNet_320.onnx"

        # Load the net
        self.net = cv2.dnn.readNet(modelPath)

        # build the blob
        self.input_shape = get_input_shape(modelPath)

        self.pb = PriorBox(input_shape=self.input_shape, output_shape=size)
        self.confTh = confTh
        self.nmsTh = nmsTh

    def forward(self, frame):
        blob = cv2.dnn.blobFromImage(frame, size=self.input_shape)  # 'size' param resize the output to the given shape
        self.net.setInput(blob)
        t = time.time()
        loc, conf, iou = self.net.forward(['loc', 'conf', 'iou'])
        # print("Elapsed time: {}".format(time.time() - t))

        dets = self.pb.decode(np.squeeze(loc, axis=0), np.squeeze(conf, axis=0), np.squeeze(iou, axis=0))

        # Ignore low scores
        idx = np.where(dets[:, -1] > self.confTh)[0]
        dets = dets[idx]

        return [] if dets.shape[0] <= 0 else nms(dets, self.nmsTh)[:750, :4].astype(np.int)


if __name__ == '__main__':
    # load videocapture
    cap = cv2.VideoCapture(0)
    det = detector()

    while cap.isOpened:
        _, frame = cap.read()

        faces = det.forward(frame)

        for bbox in faces:
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        cv2.imshow('Detection Results', frame)
        cv2.waitKey(33)

    cv2.destroyAllWindows()
