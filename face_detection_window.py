#! /usr/bin/env python

import cv2
import time
from collections import deque
import detector
import sys

def draw_stats(im, stats):
    queue, queue_sum = stats['queue'], stats['queue_sum']
    for i, s in enumerate([
            'fps: %.02f'%(queue[-1][0]),
            'min: %.02f'%(min(x[0] for x in queue)),
            'max: %.02f'%(max(x[0] for x in queue)),
            'sum: %.02f'%(queue_sum),
            'len: %d'%(len(queue))
    ]):
        cv2.putText(
            im, s, (0,15*(1+i)),
            cv2.FONT_HERSHEY_PLAIN, 1, (255,)*3
        )

def update_stats(stats, dt):
    queue, queue_sum = stats['queue'], stats['queue_sum']
    fps = 1/dt
    queue.append((fps, dt))
    queue_sum += dt
    while queue_sum > 1 and len(queue) > 1:
        fps, dt = queue.popleft()
        queue_sum -= dt
    stats['queue_sum'] = queue_sum



def detect(image, cascade, config):
    for rect in detector.detect(image, cascade, config):
        x, y, w, h = rect
        p1 = (x, y)
        p2 = (x+w, y+h)
        cv2.rectangle(image, p1, p2, (255, 0, 0), 1)

def func(config):
    window_name = 'window'
    cap = cv2.VideoCapture()
    if config['stream'] is None:
        cap.open(0)
    else:
        cap.open(config['stream'])

    cv2.namedWindow(window_name)
    try:
        tm = time.time()
        stats = {
            'queue': deque(),
            'queue_sum': 0
        }
        cascade = detector.make_detector(config)
        while True:
            dt = time.time() - tm
            tm += dt
            if dt > 1/10:
                for _ in range(int(dt / (1/10))):
                    cap.grab()
            ret, frame = cap.read()
            if not ret:
                break
            update_stats(stats, dt)
            draw_stats(frame, stats)
            detect(frame, cascade, config)
            cv2.imshow(window_name, frame)
            if cv2.waitKey(20) == ord(' '):
                break
    finally:
        cap.release()
        cv2.destroyWindow(window_name)

if __name__ == '__main__':
    config = detector.config(sys.argv[1:])
    func(config)
