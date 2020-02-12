import argparse
import cv2
from lxml import etree
import os

def draw(image, data, nm):
    cv2.putText(image, nm, (0, 10), cv2.FONT_HERSHEY_PLAIN, 1, (255,)*3)
    if nm in data:
        for person in data[nm]:
            pid, eyes = person
            cv2.circle(image, tuple(eyes[0]), 5, (0,0,255),1)
            cv2.circle(image, tuple(eyes[1]), 5, (0,255,0),1)
            mx = int((eyes[0][0]+eyes[1][0])/2)-30
            my = int((eyes[0][1]+eyes[1][1])/2)-10
            cv2.putText(image, pid, (mx, my), cv2.FONT_HERSHEY_PLAIN, 1, (255,)*3)


def show(path, data):
    image_names = os.listdir(path)
    for i, image_name in enumerate(sorted(image_names)):
        fn = os.path.join(path, image_name)
        image = cv2.imread(fn)
        nm = os.path.splitext(image_name)[0]
        draw(image, data, nm)
        cv2.imshow('window', image)
        if cv2.waitKey(20) & 0xff == 27:
            break


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
    args = parser.parse_args()

    data = read_xml(args.xml)
    show(args.dir, data)
