#include <opencv2/opencv.hpp>
#include <opencv2/core/ocl.hpp>
#include <iostream>
#include <chrono>
#include <string>
#include <deque>
#include <vector>
#include <sstream>
#include <algorithm>
#include "detector.h"

using namespace std;
using namespace cv;

#define range(x) begin(x), end(x)

struct Stats{
    struct Rec{
        float fps, dt;
        Rec(float fps, float dt) : fps(fps), dt(dt) {}
    };
    float sum;
    deque<Rec> queue;
};

void update_stats(Stats& stats, float dt){
    float fps = 1 / dt;
    stats.queue.emplace_back(fps, dt);
    stats.sum += dt;
    while(stats.sum > 1. && stats.queue.size() > 1){
        Stats::Rec rec = stats.queue[0];
        stats.queue.pop_front();
        stats.sum -= rec.dt;
    }
}

void draw_stats(Stats const & stats, Mat image){
    vector<string> strs;
    ostringstream os;
    os << fixed << setprecision(2);
    auto cmp = [](Stats::Rec const & a, Stats::Rec const & b){
        return a.fps < b.fps;
    };

    os << "fps: " << stats.queue[stats.queue.size()-1].fps;
    strs.push_back(os.str()); os.str(string());
    os << "min: " << (*min_element(range(stats.queue), cmp)).fps;
    strs.push_back(os.str()); os.str(string());
    os << "max: " << (*max_element(range(stats.queue), cmp)).fps;
    strs.push_back(os.str()); os.str(string());
    os << "sum: " << stats.sum;
    strs.push_back(os.str()); os.str(string());
    os << "len: " << stats.queue.size();
    strs.push_back(os.str()); os.str(string());

    for(int i = 0; i < strs.size(); ++i){
        string s = strs[i];
        putText(
            image, s, Point(0, (i+1)*15),
            FONT_HERSHEY_PLAIN, 1, Scalar(255, 255, 255)
        );
    }
}

void detect(Mat& image, CascadeClassifier& detector, CascadeConfig& cascade_config){
    vector<Rect>&& objects = detect_objects(
        image, detector, cascade_config
    );
    for(Rect rect : objects){
        rectangle(image, rect, Scalar(255, 0, 0));
        ostringstream oss;
        oss << rect.width;
        putText(
            image, oss.str(), rect.tl(),
            FONT_HERSHEY_PLAIN, 1, Scalar(255, 255, 255)
        );
    }
}

void run(CascadeConfig& cascade_config){
    string window_name("window");
    VideoCapture cap;
    if(cascade_config.stream.size() == 0)
        cap.open(0);
    else
        cap.open(cascade_config.stream);
    namedWindow(window_name);
    using seconds = chrono::duration<float, ratio<1,1>>;
    chrono::high_resolution_clock clock;
    auto btime = clock.now();
    Stats stats;
    auto&& detector = make_detector(cascade_config);
    while(true){
        auto duration_dt = clock.now() - btime;
        btime += duration_dt;
        float dt = seconds(duration_dt).count();
        update_stats(stats, dt);
        Mat image;
        if(!cap.read(image))
            break;
        draw_stats(stats, image);
        detect(image, detector, cascade_config);
        imshow(window_name, image);
        if(waitKey(20) == ' ')
            break;
    }
    cap.release();
    destroyWindow(window_name);
}

int main(int argc, char** argv){
    // string url;
    // if(argc != 2){
    //     url = "";
    // }else{
    //     url = argv[1];
    // }
    //setUseOptimized(false);
    setNumThreads(1);
    ocl::setUseOpenCL(false);
    auto cascade_config = config(argc, argv);
    run(cascade_config);
    return 0;
}
