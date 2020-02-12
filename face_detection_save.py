#! /usr/bin/env python

import cv2
import datetime
import os, sys
import detector

def detect(image, cascade, timestamp, config):
    for i, rect in enumerate(detector.detect(image, cascade, config)):
        x, y, w, h = rect
        crop = cv2.getRectSubPix(
            image, (w, h),
            (x + w/2, y + h/2),
        )
        cv2.imwrite('./faces/face_%d_%d.jpg'%(timestamp, i), crop)

def func(config):
    cap = cv2.VideoCapture()
    if config['stream'] is None:
        cap.open(0)
    else:
        cap.open(config['stream'])

    cascade = detector.make_detector(config)
    while True:
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        ret, frame = cap.read()
        if not ret:
            break
        detect(frame, cascade, timestamp, config)
    cap.release()

if __name__ == '__main__':

    config = detector.config(sys.argv[1:])
    if not os.path.isdir('./faces'):
        os.mkdir('./faces')
    func(config)
