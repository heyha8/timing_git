#include "../include/tcp_parse.h"
#include <boost/asio.hpp>
#include <iostream>
#include <iomanip>
#include <chrono>
#include <thread>

using boost::asio::ip::tcp;
ros::Publisher IMU_pub;

int main(int argc, char **argv)
{
	int rev = 0;
	ros::init(argc, argv, "tcp_start_node");
	ros::NodeHandle n;
	std::string tc_ip;
	int tc_port;

	auto now = std::chrono::system_clock::now();
	// 转换为time_t
    auto now_time_t = std::chrono::system_clock::to_time_t(now);
    // 转换为tm结构
    auto now_tm = *std::gmtime(&now_time_t);

	auto total_milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();
    // 计算当前秒的毫秒部分
    int current_milliseconds_tens_and_hundreds = (total_milliseconds % 1000)/10;

	std::cout << std::put_time(&now_tm, "%Y-%m-%d %H:%M:%S") << std::endl;

	std::ostringstream oss;
	oss << "#st:" << std::put_time(&now_tm, "%d%m%y%H%M%S") << "." << std::setw(2) << current_milliseconds_tens_and_hundreds << "**";
	std::string time_str = oss.str();
	std::cout << time_str << std::endl;

	ros::param::get("/tcp_start_node/tc_ip", tc_ip); //获取ip地址
	ros::param::get("/tcp_start_node/tc_port", tc_port);  //获取端口
	IMU_pub = n.advertise<sensor_msgs::Imu>("/imu", 20);

	std::cout<<"tc_ip: "<<tc_ip<<" "<<"tc_port: "<<tc_port<<std::endl;

	boost::asio::io_service io_service;

	tcp::acceptor acceptor(io_service, tcp::endpoint(boost::asio::ip::address::from_string(tc_ip), tc_port));

	std::cout << "Server is listening on "<< tc_ip<<":"<<tc_port << std::endl;

	tcp::socket socket(io_service);
	acceptor.accept(socket);

	std::string remote_ip = socket.remote_endpoint().address().to_string();
	if (remote_ip == "192.168.1.200")
	{
		ROS_INFO_STREAM("Accepted connection from 192.168.1.200");

		std::string message = time_str;
		boost::asio::write(socket, boost::asio::buffer(message));
		message = "\'#ss:start************\'";
		boost::asio::write(socket, boost::asio::buffer(message));

        std::atomic<int> imu_flag(0);
		// 启动线程处理用户输入
		std::thread input_thread([&socket, &imu_flag]() {
			while (ros::ok()) {
				int user_input;
				std::cout << "Enter 1 to start PPS, 2 to stop, 3 to start camera, 4 to stop, 5 to start imu, 6 to stop, 7 to set time: ";
				std::cin >> user_input;

				std::string user_message;
				switch (user_input) {
					case 1:
						user_message = "\'#ss:start************\'";
						break;
					case 2:
						user_message = "\'#ss:stop************\'";
						break;
					case 3:
						user_message = "\'#ss:camstart************\'";
						break;
					case 4:
						user_message = "\'#ss:camstop*************\'";
						break;
					case 5:
						imu_flag.store(1);  // 使用 atomic 的 store 来设置值
						break;
					case 6:
						imu_flag.store(0);  // 使用 atomic 的 store 来设置值
						break;
					case 7: {
						std::cout << "Enter your custom message: ";
						std::cin.ignore();  // 忽略之前的换行符
						std::getline(std::cin, user_message);  // 读取完整的用户输入消息
						break;
					}
					default:
						std::cout << "Invalid input. Please enter a valid option (1-7)." << std::endl;
						continue;
				}

				// 如果是case 7用户手动输入消息，确保不发送空消息
				if (!user_message.empty()) {
					// 发送消息到客户端
					boost::asio::write(socket, boost::asio::buffer(user_message));
					std::cout << "Message sent: " << user_message << std::endl;
				}
			}
		});


		// 主线程处理IMU数据接收
		while (ros::ok())
		{   if(imu_flag.load() == 1){
                char data[1024];
                boost::system::error_code error;
                size_t length = socket.read_some(boost::asio::buffer(data), error);

                if (error == boost::asio::error::eof)
                    break; // Connection closed cleanly by peer.
                else if (error)
                    throw boost::system::system_error(error); // Some other error.

                // 处理IMU数据
                imu_refresh(data);
            }
		}

		// 关闭用户输入线程
		input_thread.join();

		message = "\'#ss:stop************\'";
		boost::asio::write(socket, boost::asio::buffer(message));
	}

	socket.close();
	std::cout << "Connection closed" << std::endl;

	return 0;
}

std::string getFormattedTime() {
    // 获取当前时间点
    auto now = std::chrono::system_clock::now();
    // 转换为time_t
    auto now_time_t = std::chrono::system_clock::to_time_t(now);
    // 转换为tm结构
    auto now_tm = *std::localtime(&now_time_t);
    
    // 计算自 epoch 以来的总毫秒数
    auto total_milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();
    // 计算当前秒的毫秒部分 (十分位和百分位)
    int current_milliseconds_tens_and_hundreds = (total_milliseconds % 1000) / 10;

    // 创建字符串输出流
    std::ostringstream oss;
    // 格式化时间并插入到字符串中
    oss << "#st:" << std::put_time(&now_tm, "%y%m%d%H%M%S") << "." 
        << std::setw(2) << std::setfill('0') << current_milliseconds_tens_and_hundreds << "**";
    
    // 返回格式化后的时间字符串
    return oss.str();
}