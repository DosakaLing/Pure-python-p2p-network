import socket,json,time,threading
from utils import msgcreater
class p2pclient():
    def __init__(self,addr,msgqueue,localserverip,localserverport,clients_to,timeout=5):
        self.addr = addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.msgqueue = msgqueue
        self.flag = self.connect_to_server(clients_to)
        if self.flag:
            content = localserverip+":"+str(localserverport)
            handshake = msgcreater.createmsg('network','handshake_peer','from',content,True)
            self.sock.send(handshake)
            self.sock.setblocking(0)
            threading.Thread(target=self.send_heartbeat).start()
            threading.Thread(target=self.on_receive).start()

    def send_heartbeat(self):
        import time
        while self.flag:
            time.sleep(2)
            data = msgcreater.createmsg('network','heartbeat','','',True)
            try:
                self.sock.send(data)
            except Exception as e:
                self.update()
                self.msgqueue.put(msgcreater.createmsg('network','lost_peer','to',self.addr))
    def connect_to_server(self,clients_to):
        try:
            if (self.addr not in list(clients_to.keys())) and len(clients_to)<=10:
                self.sock.connect(self.addr)
                print('connected to:{}'.format(str(self.sock.getpeername())))
                msg = msgcreater.createmsg('network','new_peer','to',self.sock)
                self.msgqueue.put(msg)
                return True
            else:
                return False
        except:
            return False
    def on_receive(self):
        total_data = []
        timeout = 5
        begin = time.time()
        while 1:
            if total_data and time.time() - begin > timeout:
                break
            elif time.time() - begin > timeout * 2:
                break
            try:
                data = self.sock.recv(8192)
                if data:
                    data = data.decode('utf8')
                    data = json.loads(data)
                    if data['type'] == 'heartbeat_reply':
                        self.msgqueue.put(data)
                        # print('heart_reply')
                        pass
                    elif data['type'] != 'heartbeat_reply':
                        #print('receive data from server:')
                        self.msgqueue.put(data)
                    total_data.append(data)
                    begin = time.time()
                    # print('---------------------\nreceive from--->',addr,'\ncontent is  --->',data,'\n---------------------')
                else:
                    time.sleep(0.1)
            except Exception as e:
                pass
        self.update()
        self.msgqueue.put(msgcreater.createmsg('network','lost_peer','to',self.addr))
        print('connection lost----->', self.addr)
        self.sock.close()
    def update(self):
        self.flag = False
if __name__ == '__main__':
    import queue
    msgs = queue.Queue()
    clients = {}
    client = p2pclient(55568,msgqueue=msgs)
    while True:
        msg = msgs.get()
        print(msg)
