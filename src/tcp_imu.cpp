/*
 * @Author: nyquist1997 3210101752@zju.edu.cn
 * @Date: 2024-08-27 15:54:53
 * @LastEditors: nyquist1997 3210101752@zju.edu.cn
 * @LastEditTime: 2024-09-05 17:47:23
 * @FilePath: /src/serial_imu.cpp
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
// serial_imu.cpp
#include "../include/tcp_parse.h"
#include <boost/asio.hpp>
#include <iostream>
#include <iomanip>
#include <chrono>

using boost::asio::ip::tcp;

#define IMU_SERIAL "/dev/ttyUSB0"
#define BAUD (115200)
#define BUF_SIZE 1024

ros::Publisher IMU_pub;


int main(int argc, char **argv)
{
	int rev = 0;
	ros::init(argc, argv, "tcp_imu_node");
	ros::NodeHandle n;
	std::string tc_ip;
	int tc_port;

	auto now = std::chrono::system_clock::now();
	// 转换为time_t
    auto now_time_t = std::chrono::system_clock::to_time_t(now);
    // 转换为tm结构
    auto now_tm = *std::localtime(&now_time_t);

	auto total_milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();
    // 计算当前秒的毫秒部分
    int current_milliseconds_tens_and_hundreds = (total_milliseconds % 1000)/10;

	std::cout << std::put_time(&now_tm, "%Y-%m-%d %H:%M:%S") << std::endl;

	std::ostringstream oss;
	oss << "#st:" << std::put_time(&now_tm, "%y%m%d%H%M%S") << "." << std::setw(2) << current_milliseconds_tens_and_hundreds << "**";
	std::string time_str = oss.str();
	std::cout << time_str << std::endl;


	ros::param::get("/tcp_imu_node/tc_ip", tc_ip); //获取ip地址
	ros::param::get("/tcp_imu_node/tc_port", tc_port);  //获取端口
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

		while (ros::ok())
		{
			char data[1024];
			boost::system::error_code error;
			size_t length = socket.read_some(boost::asio::buffer(data), error);

			if (error == boost::asio::error::eof)
				break; // Connection closed cleanly by peer.
			else if (error)
				throw boost::system::system_error(error); // Some other error.

			imu_refresh(data);
			std::cout << "timer: " << timer << " " << "pitch: " << pitch << " " << "roll" << roll << " " << "yaw" << yaw << std::endl;
			
		}
		message = "\'#ss:stop************\'";
		boost::asio::write(socket, boost::asio::buffer(message));
	}

	socket.close();
	std::cout << "Connection closed" << std::endl;
	
	return 0;
}
