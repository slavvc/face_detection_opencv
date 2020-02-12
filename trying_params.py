import measure_params as mp
import detector
import yaml

def seq(a, b, f, base):
    arr = []
    while base <= b:
        if base >= a:
            arr.append(base)
        base *= f
    return arr

def count(min_sizes, max_sizes, scales, base):
    size_set = set()
    cnt = 0
    for min_s in range(*min_sizes):
        for max_s in range(*max_sizes):
            for scale in scales:
                r = frozenset(seq(min_s, max_s, scale, base))
                if len(r) == 0 or len(r) > 3:
                    continue
                if r in size_set:
                    continue
                size_set.add(r)
                cnt += 1
    return cnt


if __name__ == "__main__":

    imdir = "./data/P1E_S3_C1/"
    groundtruth = mp.read_xml("./data/P1E_S3_C1.xml")
    config = {
        "path": "../face_detection_data/outdir/cascade/cascade.xml",
        "type": "scale",
        "min": 85,
        "max": 160,
        "scalefactor": 1.5,
        "neighbors": 1,
        "base": 24
    }
    cascade = detector.make_detector(config)
    min_sizes = (75, 120, 3)
    max_sizes = (130, 200, 10)
    scales = [x/20 for x in range(21, 39)]
    cnt = count(min_sizes, max_sizes, scales, config['base'])
    data = {}
    i = 0
    size_set = set()
    for min_size in range(*min_sizes):
        for max_size in range(*max_sizes):
            for scale in scales:
                sizes = frozenset(seq(min_size, max_size, scale, config['base']))
                if len(sizes) > 3 or len(sizes) == 0:
                    continue
                if sizes in size_set:
                    continue
                size_set.add(sizes)
                print(min_size, max_size, scale, '{}/{}'.format(i+1, cnt))
                config["min"] = min_size
                config["max"] = max_size
                config["scalefactor"] = scale
                m = mp.measure(imdir, groundtruth, cascade, config, 0.5)
                print([m[2], 1/m[3]])
                data[(min_size, max_size, scale)] = [m[2], 1/m[3]]
                i+=1

    with open("./params.yaml", "wt") as f:
        yaml.dump(data, f)
