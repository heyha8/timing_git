
import socket

# 创建一个 socket 对象
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 绑定到指定的 IP 地址和端口
s.bind(('192.168.1.100', 1000))

# 开始监听连接
s.listen(1)

print('Server is listening on 192.168.1.100:1000...')


while True:
    # 接受一个连接
    client, addr = s.accept()

    # 检查连接是否来自 192.168.1.200
    if addr[0] == '192.168.1.200':
        print('Accepted connection from 192.168.1.200')

        while True:
            # 读取数据
            data = client.recv(1024)

            # 如果没有数据，跳出循环
            if not data:
                break

            # 打印接收到的数据
            print('Received:', data)
            print(len(data))

        # 关闭连接
        client.close()

# 关闭 socket
s.close()
