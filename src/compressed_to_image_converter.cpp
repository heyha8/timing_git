#include <ros/ros.h>
#include <sensor_msgs/CompressedImage.h>
#include <sensor_msgs/Image.h>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>

class CompressedToImage {
public:
    CompressedToImage() {
        // 订阅和发布话题
        sub_ = nh_.subscribe("/alphasense_driver_ros/cam0/debayered/image/compressed", 1, 
                            &CompressedToImage::callback, this);
        pub_ = nh_.advertise<sensor_msgs::Image>("camera/image", 1);
    }

    void callback(const sensor_msgs::CompressedImageConstPtr& msg) {
        try {
            // 解压图像
            cv::Mat image = cv::imdecode(cv::Mat(msg->data), cv::IMREAD_COLOR);
            
            // 转换为ROS Image消息
            cv_bridge::CvImage cv_image;
            cv_image.header = msg->header;
            cv_image.encoding = "bgr8";
            cv_image.image = image;
            
            // 发布
            pub_.publish(cv_image.toImageMsg());
        } catch (cv_bridge::Exception& e) {
            ROS_ERROR("cv_bridge exception: %s", e.what());
        } catch (cv::Exception& e) {
            ROS_ERROR("OpenCV exception: %s", e.what());
        }
    }

private:
    ros::NodeHandle nh_;
    ros::Subscriber sub_;
    ros::Publisher pub_;
};

int main(int argc, char** argv) {
    ros::init(argc, argv, "compressed_to_image_converter");
    CompressedToImage converter;
    ros::spin();
    return 0;
}