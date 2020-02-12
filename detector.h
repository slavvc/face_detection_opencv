#include <string>
#include <sstream>
#include <fstream>
#include <opencv2/opencv.hpp>
#include <stdexcept>
#include <cstdlib>
#include <vector>

struct CascadeConfig{
    std::string path;
    int min, max;
    int step;
    double scalefactor;
    bool is_range_type;
    int base;
    int neighbors;
    std::string stream;
};

std::ostream& operator<< (std::ostream& os, CascadeConfig const& cc);

CascadeConfig read_config();

CascadeConfig config(int argc, char** argv);

cv::CascadeClassifier make_detector(CascadeConfig& cascade_config);

std::vector<cv::Rect> detect_objects(
    cv::Mat& image, cv::CascadeClassifier& detector, CascadeConfig& cascade_config
);
