#include <opencv2/opencv.hpp>
#include <opencv2/core/ocl.hpp>
#include <iostream>
#include <chrono>
#include <string>
#include <vector>
#include <sstream>
#include <algorithm>
#include <sys/stat.h>
#include "detector.h"

using namespace std;
using namespace cv;

#define range(x) begin(x), end(x)


void detect(
    Mat& image, CascadeClassifier& detector,
    long long timestamp, CascadeConfig cascade_config
){
    vector<Rect>&& objects = detect_objects(
        image, detector, cascade_config
    );
    for(int i = 0; i < objects.size(); ++i){
        Rect rect = objects[i];
        Mat crop;
        Point center(
            rect.x + rect.width / 2.0,
            rect.y + rect.height / 2.0
        );
        getRectSubPix(image, rect.size(), center, crop);
        ostringstream os;
        os << "./faces/face_" << timestamp << '_' << i << ".jpg";
        imwrite(os.str(), crop);
    }
}

void run(CascadeConfig cascade_config){
    VideoCapture cap;
    if(cascade_config.stream.size() == 0)
        cap.open(0);
    else
        cap.open(cascade_config.stream);

    auto&& detector = make_detector(cascade_config);
    while(true){
        Mat image;
        if(!cap.read(image))
            break;

        double timestamp = chrono::system_clock::now()
                                .time_since_epoch().count();
        timestamp *= chrono::system_clock::duration::period::num * 1000.0;
        timestamp /= chrono::system_clock::duration::period::den;
        detect(image, detector, timestamp, cascade_config);
    }
    cap.release();
}

int main(int argc, char** argv){
    // if(argc != 2){
    //     cout << "usage: " << argv[0] << " <url>\n";
    //     return 0;
    // }
    // string url(argv[1]);
    mkdir("./faces", 0777);
    //setUseOptimized(false);
    setNumThreads(1);
    ocl::setUseOpenCL(false);
    auto cascade_config = config(argc, argv);
    run(cascade_config);
    return 0;
}
