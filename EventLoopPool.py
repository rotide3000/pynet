
from threading import Thread, Lock
from queue import Queue
# from select import epoll
import select

class TcpConnection:
    def getSocket(self):
        pass

    def setLoop(self, loop):
        pass

class EventLoop:
    def __init__(self):
        self.__lock = Lock()

        self.__ep = select.epoll()

        self.__input = []
        self.__output = []
        self.__funcs = []

        self.__isLoop = False

    def loop(self):
        self.__isLoop = True
        # self.__ep.


    def unLoop(self):
        if self.__isLoop:
            self.__isLoop = False

    def runInLoop(self, task):
        self.__isLoop = True
        while self.__isLoop:
            self.__ep.poll(10)
        

    def modify(self, newConn:TcpConnection, eventMask):
        readable, writeable, exception = self.__ep.modify(newConn.getFd(), eventMask)
        pass

    def register(self, newConn:TcpConnection):
        self.__ep.register(newConn.getFd(), select.EPOLLIN)

    def unRegister(self, newConn:TcpConnection):
        self.__ep.unregister(newConn.getFd())

class EventLoopThread(Thread):
    def __init__(self, threadName, queues:Queue):
        Thread(self)
        self.__threadName = threadName
        self._queues = queues
        self.__loop = EventLoop()
        self.__sockToConn = {}

    def run(self):
        self.__loop.loop()

    def stop(self):
        self.__loop.unLoop()


    def accpetTcpConn(self):
        newConn = self._queues.get(1)
        self.__sockToConn[newConn.getSocket()] = newConn

        self.__loop.register(newConn)
        newConn.setLoop(self.__loop)

    def getConnCount(self):
        return len(self.__sockToConn.keys())

class EventLoopThreadPool:
    def __init__(self, threadNum, ):
        self.__queue = Queue(10)
        self.__threadPool = []
        self.isStop = False
        self.__threadNum = threadNum

    def start(self):
        self.isStop = False

        for i in self.__threadNum:
            loopThread = EventLoopThread('thread:' + i, self.__queue)
            self.__threadPool.append(loopThread)

        for loopThread in self.__threadPool:
            loopThread.start()

    def stop(self):
        if self.isStop:
            return
        self.isStop = True

        for loopThread in self.__threadPool:
            loopThread.stop()
        for loopThread in self.__threadPool:
            loopThread.join()

    def accpetTcpConn(self, conn:TcpConnection):
        self.__queue.put(conn, True)
        loopThread = min(self.__threadPool, key=lambda loopThread: loopThread.getConnCount())
        loopThread.accpetTcpCon()
