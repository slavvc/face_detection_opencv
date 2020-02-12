#include "detector.h"

std::ostream& operator<< (std::ostream& os, CascadeConfig const& cc){
    os << "path: " << cc.path << '\n';
    os << "min: " << cc.min << '\n';
    os << "max: " << cc.max << '\n';
    os << "neighbors: " << cc.neighbors << '\n';
    os << "stream: " << cc.stream << '\n';
    os << "step: " << cc.step << '\n';
    os << "base: " << cc.base << '\n';
    os << "scalefactor: " << cc.scalefactor << '\n';
    os << "is_range_type: " << cc.is_range_type << '\n';
    return os;
}


CascadeConfig read_config(std::string path){
    CascadeConfig config;
    std::ifstream ifs(path);
    if(!ifs.is_open()){
        throw std::runtime_error("can not open a cascade config file");
    }
    std::string line;
    for(int i = 0; i < 7; ++i){
        std::getline(ifs, line);
        while(line.size() > 0 && line[0] == '#') std::getline(ifs, line);
        if(i == 0){
            config.path = line;
        }else if(i == 1){
            if (line == std::string("range")){
                config.is_range_type = true;
            }else if(line == std::string("scale")){
                config.is_range_type = false;
            }else{
                std::cout << "wrong config type\n";
                exit(0);
            }
        }else{
            std::istringstream is(line);
            if(i == 2 || i == 3){
                int s;
                is >> s;
                if(i == 2){
                    config.min = s;
                }else{
                    config.max = s;
                }
            }else if(i == 4){
                if(config.is_range_type){
                    int step;
                    is >> step;
                    config.step = step;
                }else{
                    double factor;
                    is >> factor;
                    config.scalefactor = factor;
                }
            }else if(i == 5){
                int base;
                is >> base;
                config.base = base;
            }else{
                int n;
                is >> n;
                config.neighbors = n;
            }
        }
    }

    return config;
}

CascadeConfig config(int argc, char** argv){
    CascadeConfig res;
    cv::CommandLineParser parser(argc, argv,
        "{h help      |                      |}"
        "{file        |                      |}"
        "{args        |                      |}"
        "{stream      |                      |}"
        "{min         | 100                  |}"
        "{max         | 160                  |}"
        "{neighbors   | 3                    |}"
        "{step        | 30                   |}"
        "{base        | 24                   |}"
        "{path        |                      |}"
        "{type        | scale                |}"
        "{factor      | 1.5                  |}"
    );
    if (parser.has("h")){
        parser.printMessage();
        exit(0);
    }
    std::string stream = parser.get<std::string>("stream");
    if(parser.has("file")){
        std::string config_path = parser.get<std::string>("file");
        if (config_path == "true"){
            config_path = "./cascade_config.txt";
        }
        res = read_config(config_path);
        res.stream = stream;
    }else if(parser.has("args")){
        res.stream = stream;
        res.neighbors = parser.get<int>("neighbors");
        if(!parser.has("path")){
            std::cout << "path is needed\n";
            exit(0);
        }
        res.path = parser.get<std::string>("path");
        res.min = parser.get<int>("min");
        res.max = parser.get<int>("max");
        res.step = parser.get<int>("step");
        res.base = parser.get<int>("base");
        res.scalefactor = parser.get<double>("factor");
        if(parser.get<std::string>("type") == "range"){
            res.is_range_type = true;
        }else if(parser.get<std::string>("type") == "scale"){
            res.is_range_type = false;
        }else{
            std::cout << "wrong config type\n";
            exit(0);
        }

        // int w, h;
        // std::istringstream miniss(parser.get<std::string>("min"));
        // miniss >> w;
        // miniss.ignore(1);
        // miniss >> h;
        // res.min = cv::Size(w, h);
        // std::istringstream maxiss(parser.get<std::string>("max"));
        // maxiss >> w;
        // maxiss.ignore(1);
        // maxiss >> h;
        // res.max = cv::Size(w, h);
    }else{
        std::cout << "either args or file is needed\n";
        exit(0);
    }
    std::cout << res;
    return res;
}

cv::CascadeClassifier make_detector(CascadeConfig& cascade_config){
    cv::CascadeClassifier cascade;
    if(!cascade.load(cascade_config.path)){
        throw std::runtime_error("no cascade file");
    }
    return cascade;
}

std::vector<cv::Rect> detect_objects(
    cv::Mat& image, cv::CascadeClassifier& detector, CascadeConfig& cascade_config
){
    cv::Mat gray;
    cvtColor(image, gray, cv::COLOR_BGR2GRAY);
    if (cascade_config.is_range_type){
        std::vector<cv::Rect> objects;
        for(
            int size = cascade_config.min;
            size <= cascade_config.max;
            size += cascade_config.step
        ){
            double factor = size / cascade_config.base;
            cv::Size min(size, size);
            cv::Size max(size, size);
            std::vector<cv::Rect> rects;
            detector.detectMultiScale(
                gray, rects, factor,
                cascade_config.neighbors, 0,
                min, max
            );
            objects.insert(end(objects), begin(rects), end(rects));
        }
        return objects;
    }else{
        std::vector<cv::Rect> objects;
        cv::Size min(cascade_config.min, cascade_config.min);
        cv::Size max(cascade_config.max, cascade_config.max);
        detector.detectMultiScale(
            gray, objects, cascade_config.scalefactor,
            cascade_config.neighbors, 0,
            min, max
        );
        return objects;
    }
}
