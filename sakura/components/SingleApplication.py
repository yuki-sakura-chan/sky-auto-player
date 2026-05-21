# 单实例控制类
from PySide6.QtCore import QObject
from PySide6.QtNetwork import QLocalSocket, QLocalServer


class SingleApplication(QObject):

    # key 是当前程序唯一标识
    def __init__(self, key: str):
        super().__init__()

        # 保存唯一标识
        self.key = key

        # 服务端对象
        self.server = None

    # 检查程序是否已经运行
    def already_running(self) -> bool:

        # 创建客户端 socket
        sock = QLocalSocket()

        # 尝试连接已经存在的程序
        sock.connectToServer(self.key)

        # 等待连接成功
        # 100 = 最多等待100毫秒
        if sock.waitForConnected(100):
            # 给已经运行的程序发送消息
            # b"show" 是字节数据
            sock.write(b"show")

            # 立即发送
            sock.flush()

            # 等待真正写入完成
            sock.waitForBytesWritten(100)

            # 断开连接
            sock.disconnectFromServer()

            # 返回 True
            # 表示程序已经运行
            return True

        # 如果程序异常退出
        # 可能会残留旧 server
        # 删除旧 server
        QLocalServer.removeServer(self.key)

        # 创建本地服务端
        self.server = QLocalServer()

        # 开始监听
        self.server.listen(self.key)

        # 有新连接时触发
        self.server.newConnection.connect(self.on_new_connection)

        # 返回 False
        # 表示当前是第一个实例
        return False

        # 收到新连接

    def on_new_connection(self):

        # 获取连接对象
        sock = self.server.nextPendingConnection()

        # 理论安全检查
        if not sock:
            return

        # 等待数据到来
        sock.waitForReadyRead(100)

        # 读取全部数据
        # bytes -> str
        msg = bytes(sock.readAll()).decode()

        # 如果收到 show 消息
        if msg == "show":
            # 调用显示窗口逻辑
            self.on_show()

        # 断开连接
        sock.disconnectFromServer()

    # 占位函数
    # 后面会替换成窗口显示函数
    def on_show(self):
        pass
