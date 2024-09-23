### 2024.9.9
* 跑通fyj的代码，记得'source devel/setup.bash',修改ip'sudo ifconfig wlp0s20f3 192.168.1.100 netmask 255.255.255.0'
* 'roslaunch tcp_imu tcp_start.launch'
* 下一步任务：
	* 把imu和启动代码分开
	* 撰写相机的启动代码
	* 雷达驱动的安装，数据的读取与发布


### 2024.9.12
* 设计在终端完成发送指令，启停相机、imu等选项
* MID驱动配置完成，rviz看见点云。
	* 配置文件：'https://github.com/Livox-SDK/livox_ros_driver2'
	* 修改json文件host_net_info的ip为本机ip 192.168.1.100，修改launch文件中雷达sn码为47MDL970020057
	* rviz选择pointcloud2，记得地图基准选择livox_frame
	* 'roslaunch livox_ros_driver2 rviz_MID360.launch'
* 禾赛雷达安装驱动，但topic为空
	* 'roslaunch hesai_lidar hesai_lidar.launch lidar_type:="PandarXT-32" frame_id:="PandarXT-32"'
	* 地图基准为frame_id
	* 记得查看ip地址（192.168.1.202）和端口
