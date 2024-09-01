__all__ = ['Server']
import logging
import socket
import asyncio
from .http import HTTP
from .ws import WebSocket

class Server():
    def __new__(cls, *args, **kwargs):
        if not hasattr(Server, 'instance'):
            Server.instance = super().__new__(cls, *args, **kwargs)
        return Server.instance

    def config(self, config: dict = {}):
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 6655)
        self.backlog = config.get('backlog', 0)
        self.http_config = config.get('http', {})
        self.ws_config = config.get('websocket', {})
        self.pool = {}
        self.logger = logging.getLogger('asynsrv')
        log_attr = ['debug','info','warning','error','critical','exception']
        for attr in log_attr:
            setattr(self, attr, getattr(self.logger, attr))

    def router(self):
        pass
        
    async def handler(self, conn, addr):
        type = 'http'
        alive = self.http_config.get('keep-alive',)
        try:
            while True:
                self.debug(f'Accept connection from {addr}')
                print('accept conn')
                request = await self.loop.sock_recv(conn, 1024)
                if b'exit' in request[:20]:
                    self.stop()
                http_response_body = "Hello World"
                http_response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html; charset=UTF-8\r\n"
                    f"Content-Length: {len(http_response_body)}\r\n"
                    "\r\n"
                    f"{http_response_body}"
                )
                await self.loop.sock_sendall(conn, http_response.encode('utf-8'))
                conn.close()
                break
        except asyncio.CancelledError:
            conn.close()
    
    async def accept(self):
        try:
            while True:
                conn, addr = await self.loop.sock_accept(self.socket)
                self.loop.create_task(self.handler(conn, addr))
        except asyncio.CancelledError:
            self.debug('Stop accepting connections')

    def start(self):
        if not hasattr(self, 'loop'):
            self.loop = asyncio.new_event_loop()
        if not hasattr(self, 'socket'):
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            while True:
                try:
                    self.socket.bind((self.host, self.port))
                    break
                except OSError:
                    self.info(f'Port {self.port} is occupied. '\
                            f'Try to start server on port {self.port + 1}')
                    self.port = self.port + 1
            self.info(f'Start server at {self.host}:{self.port}')
            if self.backlog > 0:
                self.socket.listen(self.backlog)
            else:
                self.socket.listen()
                self.debug(f'Use default socket backlog: {socket.SOMAXCONN}')
            self.socket.setblocking(False)
        self.task = self.loop.create_task(self.accept())
        self.loop.run_until_complete(self.task)
        self.cleanup()

    def cleanup(self):
        self.debug('Start clean-up process')
        tasks = [task for task in asyncio.all_tasks(self.loop)]
        if len(tasks) != 0:
            for task in tasks:
                print(task)
                task.cancel()
            self.loop.run_until_complete(asyncio.gather(*tasks))
        delattr(self, 'task')
        self.loop.close()
        delattr(self, 'loop')
        self.socket.close()
        delattr(self, 'socket')
        self.info('Server stop')


    def stop(self):
        if hasattr(self, 'task'):
            self.task.cancel()