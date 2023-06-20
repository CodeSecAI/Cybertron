import json
from threading import Lock, Thread
import ast


class KeyStore(object):
    """KeyStore is a thread safe python class that is intended to replace sqlite3 for most use cases."""
    def __init__(self,**kwargs):
            global key
            global value
            global KeyStore
            for key, value in kwargs.items():
                    self.key = key
                    self.value = value
                    KeyStore = {}
                    KeyStore[key] = value
                    for key in KeyStore:
                        setattr(self, key, KeyStore[key])


    def __missing__(self):
         KeyStore[key] = value
         return KeyStore
    

    def __setitem__(self, key, value):
        KeyStore[key] = value
        setattr(self, key, KeyStore[key])
        return KeyStore
    

    def __getitem__(self, key):
         try:
            return KeyStore[key]
         except KeyError:
            return self.__missing__()
         

    def __delitem__(self, key):
            KeyStore[key] = ""
            return KeyStore[key]
    

    def __dict__(self):
        KeyStore[key] = value
        return KeyStore


    def __repr__(self):
         return repr(KeyStore)
    

    def lock(self):
         lock = Lock()
         return lock.acquire
    

    def unlock(self):
        lock = Lock()
        return lock.release 
    

    def set(self,key,value):
        KeyStore[key] = value
        return KeyStore
    

    def write(self,id,database):
         self.lock()
         db = open(database,'a+')
         db.write(f"{id} |#| {KeyStore}\n")
         db.close()
         self.unlock()
         return db
    
    def read(self,database):
        self.lock()
        db = open(database, 'r+').read()
        db = db.split("\n")
        result = []
        for i in db:
             x = i.split(" |#| ")
             result.append(x)
        result.pop(len(result)-1)
        self.unlock()
        return result
    
    def get(self,id,database):
        self.lock()
        db = open(database, 'r+').read()
        db = db.split("\n")
        result = [i for i in db if id in i]
        try:
            result = str(result[0]).split("|#|")[1][1:]
        except IndexError:
             return
        self.unlock()
        KeyStore = ast.literal_eval(json.loads(json.dumps(result)))
        return KeyStore
    
    
    def len(self,database):
        self.lock()
        db = open(database, 'r+').read()
        db = db.split("\n")
        self.unlock()
        return len(db)
    
    def json(self):
         return json.dumps(KeyStore)
    

    def dict(self,blob):
         return json.loads(blob)

    def ThreadedWrite(self,id,database):
        t = Thread(name='write_thread',target=self.write,args=(id,database,)).start()
        return

    def ThreadedRead(self,id,database):
        thread = Thread(name='read_thread',target=self.read,args=(database,))
        thread.start()
        thread.join(timeout=1)
        return KeyStore


    
 
def test():    
    x = KeyStore(hello="world")
    print("Class Test:")
    print(x)
    print("Attribute Test:")
    print(x.hello)
    print("Dict Test:")
    x['hello'] = 'bye'
    x.set('hello', x.hello)
    print(x)
    print("Attribute Test:")
    x.hello = "Goodbye"
    x.set('hello', x.hello)
    print(x)
    print("Write Test:")
    x.write("id-test","id.db")
    print("Len Test:")
    _len = x.len('id.db')
    x.write(f"id-test-{_len}","id.db")
    y = x.get(f"id-test-{_len}","id.db")
    print("JSON Dump Test:")
    _json = x.json()
    print(_json)
    print("JSON Load Test:")
    _dict = x.dict(_json)
    print(_dict['hello'])
    print("Threaded Read and Write Test: ")
    x.hello = "Thread Test"
    x.set('hello', x.hello)
    _len = x.len('id.db')
    x.ThreadedWrite(f"id-test-{_len}","id.db")
    print(x.ThreadedRead(f"id-test-{_len}","id.db"))

if __name__ == '__main__':
     test()
