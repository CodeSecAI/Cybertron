from jsonify import *
import zipfile
import os
import ast
from KeyStore import *
def BugDB(id,data,code):
    x = JsonBackend(id=id,data=data,code=code)
    return x.to_dict()
def SaveDB(prefix,db):
    x = JsonBackend().write_json_file(f'{prefix}.db',db)
    return x
def AddZDB(prefix):
    x = ZipFS(f'{prefix}.zfs')
    x.initalize()
    num = len(x.list_files())
    x.store_file(f'{prefix}.db', f'{prefix}-{num}.db')
    return
def ReadDB(prefix):
    entries = []
    x = ZipFS(f'{prefix}.zfs')
    for i in x.list_files():
        entries.append(x.read_file(i))
    return entries

def ReadZDB(prefix):
    entries = []
    x = ZipFS(f'{prefix}.zdb')
    for i in x.list_files():
        entries.append(x.read_file(i))
    return entries

def DumpZDB(prefix):
    x = ZipFS(f'{prefix}.zdb')
    entries = []
    for i in x.list_files():
        data = str(i).split(".")[0]
        zip_file = zipfile.ZipFile(f'{prefix}.zdb', 'r') 
        print(zip_file.extract(i))
        for c in ZipFS(i).list_files():
            data = ZipFS(i).read_file(c)
            entries.append(data)
    return entries

def ZipDB(prefix):
    x = ZipFS(f'{prefix}.zdb')
    ks = KeyStore().read(f'{prefix}.index')
    for i in ks:
        z = ast.literal_eval(json.loads(json.dumps(i[1])))
        index = z['index']
        x.store_file(f'{index}.zfs', f'{index}.zfs')
        os.remove(f'{index}.zfs')
        os.remove(f'{index}.db')
    x.store_file(f'{prefix}.index', f'{prefix}.index')
    return ks