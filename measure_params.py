#! /usr/bin/env python

import argparse
import os
import detector
from lxml import etree
import cv2
import tqdm
import time

def is_eyes_in_rect(eyes, rect):
    x, y, w, h = rect
    res = True
    for eye in eyes:
        res = res and (
            x  <= eye[0] and y  <= eye[1] and
            x+w > eye[0] and y+h > eye[1]
        )

    return res

def compare(rects, persons):
    found_rects = 0
    found_persons = 0
    for rect in rects:
        for _, eyes in persons:
            if is_eyes_in_rect(eyes, rect):
                found_rects += 1
                break
    for _, eyes in persons:
        for rect in rects:
            if is_eyes_in_rect(eyes, rect):
                found_persons += 1
                break
    FP = len(rects) - found_rects
    FN = len(persons) - found_persons
    TP = found_rects
    return TP, FP, FN, len(persons), found_persons

def measure(imdir, data, cascade, config, part=1):
    TP = 0
    FP = 0
    FN = 0
    total_persons = 0
    found_persons = 0
    image_names = sorted(os.listdir(imdir))
    len_image_names = int(len(image_names)*part)
    image_names = image_names[:len_image_names]
    sum_dt = 0
    for i, image_name in tqdm.tqdm(
        enumerate(image_names), total=len(image_names)
    ):
        fn = os.path.join(imdir, image_name)
        image = cv2.imread(fn)
        nm = os.path.splitext(image_name)[0]
        basetime = time.time()
        rects = detector.detect(image, cascade, config)
        dt = time.time() - basetime
        sum_dt += dt
        tp, fp, fn, tot_pers, found_pers = compare(
            rects, data[nm] if nm in data else []
        )
        TP += tp
        FP += fp
        FN += fn
        total_persons += tot_pers
        found_persons += found_pers
    return (
        (TP, FP, FN), TP/(TP+FP+FN),
        found_persons/ total_persons,
        sum_dt/len(image_names)
    )

def read_xml(path):
    res = {}
    with open(path, 'rt') as f:
        tree = etree.XML(f.read())
    frames = tree.xpath('//frame')
    for frame in frames:
        n = frame.attrib['number']
        l = []
        for person in frame.xpath('./person'):
            person_id = person.attrib['id']
            left_eye = person.xpath('./leftEye')[0]
            right_eye = person.xpath('./rightEye')[0]
            eyes = [
                [int(left_eye.attrib[attr]) for attr in ['x', 'y']],
                [int(right_eye.attrib[attr]) for attr in ['x', 'y']]
            ]
            l.append([person_id, eyes])
        res[n] = l
    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-dir', action='store', type=str, required=True)
    parser.add_argument('-xml', action='store', type=str, required=True)
    parser.add_argument('-config', action='store', type=str, required=True)
    parser.add_argument('-part', action='store', type=float, default=1)
    args = parser.parse_args()

    data = read_xml(args.xml)
    config = detector.read_file(args.config)
    cascade = detector.make_detector(config)
    m = measure(args.dir, data, cascade, config, args.part)
    print('config: ', config)
    print(m[0])
    print('CSI: ', m[1])
    print('average dt: ', m[3])
    print('average fps: ', 1/m[3])
    print('probability: ', m[2])
