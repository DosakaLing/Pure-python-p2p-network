import threading,time,queue
from network_foundation import testb_server
from network_foundation import testb_client
class clients_handler():
    def __init__(self,clients_from,clients_to,bind_range,msglist,localserverip,localserverport):
        self.clients_from = clients_from
        self.clients_to = clients_to
        self.inirange = bind_range
        self.msglist = msglist
        self.localserverip = localserverip
        self.localserverport = localserverport
        for i in bind_range:
            threading.Thread(target=self.create_client,args=(i,msglist)).start()
    #network-related 消息的回调函数
    def handle_msg(self,msg):
        #handshake_peer | from
        if msg['type'] == 'handshake_peer':
            serverip_and_port = msg['content']
            ip_port = serverip_and_port.split(':')
            serverip = ip_port[0]
            serverport = int(ip_port[1])
            if (serverip,serverport) not in list(self.clients_to.keys()):
                threading.Thread(target=self.create_client,args=((serverip,serverport),self.msglist)).start()
        #new_peer | from&to
        if msg['type'] == 'new_peer':
            if msg['operation'] == 'to':
                sock = msg['content']
                self.clients_to[sock.getpeername()] = [sock.getpeername(),'to',sock]
            elif msg['operation'] == 'from':
                sock = msg['content']
                self.clients_from[sock.getpeername()] = [sock.getpeername(),'from',sock]
        #lost_peer | from&to
        if msg['type'] == 'lost_peer':
            if msg['operation'] == 'to':
                try:
                    del self.clients_to[msg['content']]
                except:
                    pass
            elif msg['operation'] == 'from':
                try:
                    del self.clients_from[msg['content']]
                except:
                    pass
        #serverlist_peer |
        if msg['type'] == 'serverlist_peer':
            print(msg['content'])
            pass
    #客户端创建方法
    def create_client(self,addr, que):
        client = testb_client.p2pclient(addr, que,self.localserverip,self.localserverport,self.clients_to)
#用于打印clients列表的函数
def print_clients(clients_from,clients_to):
    import os
    while True:
        print()
        print()
        print('from----------------------------')
        for i in clients_from.keys():
            print(i)
        print('to------------------------------')
        for i in clients_to.keys():
            print(i)
        print('end-----------------------------')
        time.sleep(2)

#程序设计时用
'''
def init_preconnectionlist():
    import json
    addrs = []
    for i in range(55568,55578):
        addr = ('127.0.0.1:%d' % i)
        addrs.append(addr)
    with open('src/prePort.json','w') as jsonfile:
        json.dump(addrs,jsonfile)
'''
#从预设列表中读取预设服务器
def loading_port_list():
    import json
    addr_list = []
    with open('src/prePort.json') as jsonfile:
        addrs = json.load(jsonfile)
    for addr in addrs:
        host = addr.split(':')[0]
        port = int(addr.split(':')[1])
        addr_list.append((host,port))
    return addr_list
#主函数
def main_func():
    #初始化变量
    servers = queue.Queue()
    msgs = queue.Queue()
    clients_from = {}
    clients_to = {}
    bind_range = loading_port_list()
    #server线程启动
    thread_server = threading.Thread(target=testb_server.startserver,args=(msgs,servers,clients_to))
    thread_server.start()
    #server启动前主线程阻塞于此处
    while True:
        server = servers.get()
        ipaddr,port = server.getsockname()
        bind_range.remove((ipaddr,port))
        print('Get local server: ',(ipaddr,port))
        break
    #server启动结束，启动客户端管理器
    print('Waiting for clients!')
    peers_handler = clients_handler(clients_from,clients_to,bind_range,msgs,ipaddr,port)


    #主循环（消费队列）
    while 1:
        msg = msgs.get()
        if msg['type']!= 'heartbeat_reply':
            pass
            #print(msg)
        if msg['app'] == 'network':
            peers_handler.handle_msg(msg)
            #elif:
        #elif:
if __name__ == '__main__':
    main_func()
    #init_preconnectionlist()