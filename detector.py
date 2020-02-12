import argparse
import cv2
config = None

def config(argv):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        dest='subparser', required=True
    )
    config_file = subparsers.add_parser('file')
    config_file.add_argument(
        '-path', type=str, action='store',
        help='config file', default='./cascade_config.txt'
    )
    config_args = subparsers.add_parser('args')
    config_args.add_argument(
        '-path', type=str, action='store',
        help='cascade file', required=True
    )
    config_args.add_argument(
        '-min', type=int, action='store',
        help='min window', required=True
    )
    config_args.add_argument(
        '-max', type=int, action='store',
        help='max window', required=True
    )
    config_args.add_argument(
        '-step', type=int, action='store',
        help='window range step', default=30
    )
    config_args.add_argument(
        '-factor', type=float, action='store',
        help='scaleFactor', default=1.5
    )
    ex_gr = config_args.add_mutually_exclusive_group()
    ex_gr.add_argument(
        '-range', action='store_true',
        help='window range step'
    )
    ex_gr.add_argument(
        '-scale', action='store_true',
        help='window range step'
    )
    config_args.add_argument(
        '-base', type=int, action='store',
        help='cascade base window size', default=24
    )
    config_args.add_argument(
        '-neighbors', type=int, action='store',
        help='min num of neighbors', required=True
    )
    stream = {
        'type':str, 'action':'store',
        'help':'url of a video stream of nothing for webcam'
    }
    config_args.add_argument('-stream', **stream)
    config_file.add_argument('-stream', **stream)

    res = parser.parse_args(argv)
    if res.subparser == 'file':
        config = read_file(res.path)
        config['stream'] = res.stream
        return config
    else:
        config = {}
        config['stream'] = res.stream
        config['path'] = res.path
        if res.range:
            config['type'] = 'range'
            config['step'] = res.step
            config['base'] = res.base
        elif res.scale:
            config['type'] = 'scale'
            config['scalefactor'] = res.factor
        config['neighbors'] = res.neighbors
        config['min'] = res.min
        config['max'] = res.max

        return config

def read_file(path):
    config = {}
    with open(path, 'rt') as f:
        i = 0
        for line in f.readlines():
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            if i == 0:
                config['path'] = line.strip()
            elif i == 1:
                if line not in ['range', 'scale']:
                    print('wrong config type')
                    import sys
                    sys.exit()
                config['type'] = line
            elif i == 2 or i == 3:
                s = int(line)
                config['min' if i == 2 else 'max'] = s
            elif i == 4:
                if config['type'] == 'range':
                    s = int(line)
                    config['step'] = s
                else:
                    s = float(line)
                    config['scalefactor'] = s
            elif i == 5:
                b = int(line)
                config['base'] = b
            elif i == 6:
                n = int(line)
                config['neighbors'] = n
            i += 1
    return config

def make_detector(config):
    path = config['path']
    cascade = cv2.CascadeClassifier()
    if not cascade.load(path):
        raise Exception("no cascade file")
    return cascade

def detect(image, detector, config):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rects = []
    if config['type'] == 'range':
        for size in range(config['min'], config['max'], config['step']):
            factor = (size / config['base'])
            trects = detector.detectMultiScale(
                gray, scaleFactor=factor,
                minSize=(size, size), maxSize=(size, size),
                minNeighbors=config['neighbors']
            )
            rects += list(trects)
            del trects
    else:
        min_size = (config['min'],)*2
        max_size = (config['max'],)*2
        rects = detector.detectMultiScale(
            gray, scaleFactor=config['scalefactor'],
            minSize=min_size, maxSize=max_size,
            minNeighbors=config['neighbors']
        )
    return rects

if __name__ == '__main__':
    import sys
    print(config(sys.argv[1:]))
