import json

def createmsg(app,type,operation,content,encoded=False):
    msg = {}
    msg['app'] = app
    msg['type'] = type
    msg['operation'] = operation
    msg['content'] = content
    if encoded:
        msg = json.dumps(msg).encode('utf8')
        return msg
    else:
        return msg