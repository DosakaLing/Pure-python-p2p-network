import socket,threading,time,json
from utils import msgcreater

def recv_timeout(sock,addr,msglist,timeout=5):
    sock.setblocking(0)
    total_data = [];data='';begin = time.time()
    while 1:
        if total_data and time.time()-begin > timeout:
            break
        elif time.time()-begin> timeout*2:
            break
        try:
            data = sock.recv(8192)
            if data:
                data = data.decode('utf8')
                data = json.loads(data)
                if data['type'] == 'heartbeat':
                    msg = msgcreater.createmsg('network','heartbeat_reply','','',True)
                    try:
                        sock.send(msg)
                    except:
                        pass
                elif data['type'] != 'heartbeat':
                    msglist.put(data)
                total_data.append(data)
                begin = time.time()
                #print('---------------------\nreceive from--->',addr,'\ncontent is  --->',data,'\n---------------------')
            else:
                time.sleep(0.1)
        except:
            pass
    msg = msgcreater.createmsg('network','lost_peer','from',addr)
    msglist.put(msg)
    sock.close()
    print('connection lost----->' ,addr)
def startserver(msglist,servers,clients_to):
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    for i in range(55568,55578):
        try:
            sock.bind(('localhost',i))
            print('端口%d可用，绑定成功！' % i)
            servers.put(sock)
            break
        except Exception as e:
            print('Fail to bind.',e)
            pass
    sock.listen(2)
    #print('start on ',i)
    while True:
        netsock,address = sock.accept()
        print('connected from:{}'.format(str(address)))
        peers_to = [key[0]+':'+str(key[1]) for key,value in clients_to.items()]
        msg = msgcreater.createmsg('network','serverlist_peer','',json.dumps(peers_to),True)
        netsock.send(msg)
        msg = msgcreater.createmsg('network','new_peer','from',netsock)
        msglist.put(msg)
        t = threading.Thread(target=recv_timeout,args=(netsock,address,msglist))
        t.start()