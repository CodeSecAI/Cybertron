import json
from threading import Lock
from jose import jwe
import string
import random
import zipfile
from datetime import datetime
from base64 import b64decode,b64encode
import scrypt

class ZipFSLogger:
    def __init__(self, zip_file_path):
        self.zip_file_path = zip_file_path
        self.log_file = open(f"{zip_file_path}.log", "w")

    def log_access(self, user, action):
        self.log_file.write(f"{datetime.now()} {user} {action}\n")

    def close(self):
        self.log_file.close()


class RBAC:
    def __init__(self, roles):
        self.roles = roles
        self.permissions = dict(users=roles,role=roles)
        for role in roles:
            self.permissions[role] = []

    def has_permission(self, role, permission):
        return role in self.roles and permission in self.permissions[role]

    def get_roles(self):
        return self.roles

    def get_permissions(self):
        return self.permissions

    def add_role(self, role):
        self.roles.append(role)

    def remove_role(self, role):
        self.roles.remove(role)

    def add_permission(self, role, permission):
        if role not in self.roles:
            self.roles.append(role)
        self.permissions[role].append(permission)

    def remove_permission(self, role, permission):
        if role not in self.roles:
            return
        self.permissions[role].pop(permission)

class ZipFS:
    def __init__(self, zip_file_path):
        self.zip_file_path = zip_file_path

    def initalize(self):
        open(self.zip_file_path,'w+').write("")

    def store_file(self, file_path, file_name):
        with zipfile.ZipFile(self.zip_file_path, "a",compresslevel=9) as zip_file:
            zip_file.write(file_path, file_name)

    def read_file(self, file_name):
        with zipfile.ZipFile(self.zip_file_path, "r") as zip_file:
            z = zip_file.read(file_name)
            return json.loads(z.decode('utf-8'))

    def list_files(self):
        with zipfile.ZipFile(self.zip_file_path, "r") as zip_file:
            return zip_file.namelist()

class JsonBackend:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def lock(self):
         lock = Lock()
         return lock.acquire
    

    def unlock(self):
        lock = Lock()
        return lock.release 
    def to_dict(self):
        return dict(self.kwargs)

    def to_json(self):
        return json.dumps(self.kwargs, indent=4, sort_keys=True)

    def read_json_file(self, file_path):
        with open(file_path, "r") as f:
            json_data = json.load(f)
        return json_data
    
    def read_json_blob(self,json_data, path):

        if not isinstance(json_data, dict):
            raise TypeError("json_data must be a dict")

        path = path.split(".")
        obj = json_data
        for key in path[:-1]:
            if key not in obj:
                raise KeyError(f"No key '{key}' in JSON object")
        obj = obj[key]
        return obj[path[-1]]

    def write_json_file(self, file_path, json_data):
        with open(file_path, "w+") as f:
            return json.dump(json_data, f, indent=4, sort_keys=True)
            
    def append_json_blob(self, file_path, json_data):
        with open(file_path, "r+") as f:
            existing_json_data = json.load(f)
            existing_json_data.append(json_data)
            f.seek(0)
            return json.dump(existing_json_data, f, indent=4, sort_keys=True)


    def update_json(self,dict_obj, path, value):
        json_data = dict_obj.to_dict()
        if not isinstance(json_data, dict):
            raise TypeError("json_data must be a dict")

        path = path.split(".")
        obj = json_data
        for key in path[:-1]:
            if key not in obj:
                raise KeyError(f"No key '{key}' in JSON object")
            obj = obj[key]

        obj[path[-1]] = value
        self.merge_data(json_data)
        return json_data

    def append_json(self,obj, new_data):
        json_data = obj.to_dict()
        if not isinstance(json_data, dict):
            raise TypeError("json_data must be a dict")

        if not isinstance(new_data, dict):
            raise TypeError("new_data must be a dict")

        for key, value in new_data.items():
            json_data[key] = value
        self.merge_data(json_data)
        return json_data
    
    def random_key(self,size):
        if size == 16 or size == 32: 
            letters = string.ascii_letters
            return ''.join(random.choice(letters) for i in range(size))
        else:
            raise TypeError("Key size must be 16 or 32")
    
    def encrypt(self,data,key):
        if len(key) == 16:
            jwt = jwe.encrypt(f'{data}', f'{key}', algorithm='dir', encryption='A128GCM')
            return jwt.decode('utf-8')
        if len(key) == 32:
            jwt =  jwe.encrypt(f'{data}', f'{key}', algorithm='dir', encryption='A256GCM')
            return jwt.decode('utf-8')
        else:
            raise TypeError("Incorrect key size")
    
    def decrypt(self,data,key):
        if len(key) == 16 or len(key) == 32:
            jwt = bytes(data,'utf-8')
            jwt = jwe.decrypt(key=key,jwe_str=jwt)
            return json.loads(json.dumps(jwt.decode('utf-8')))

    def merge_data(self,json_data):
        kwargs = json_data
        obj = self.__init__(**kwargs)
        return obj
    
    def len(self,file_path):
        self.lock()
        try:
            db = open(file_path, 'r+').read()
        except FileNotFoundError:
            self.unlock()
            return 0
        db = db.split("\n")
        self.unlock()
        return len(db)

    def reload(self,obj):
        jwt = json.loads(obj.to_json())['data']['enc']
        return jwt

    def get_key(self,obj):
        jwt = json.loads(obj.to_json())['key']['enc']
        return jwt


def HashPassword(password,size):
    return bytes(b64encode(scrypt.hash(password, password))).decode('utf-8')
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
                    prog='VaultTec',
                    description='Secrets Storage Tool',
                    epilog='Tool By ServiceKeys.io')   
    parser.add_argument('--vault')           
    parser.add_argument('--secret')
    parser.add_argument('--password')
    parser.add_argument('--name')
    parse = parser.parse_args()


    rbac = RBAC([
        "admin",
        "test_user",
    ])
    rbac.add_permission("admin", "read")
    rbac.add_permission("admin", "write")
    rbac.add_permission("admin", "delete")
    rbac.add_permission("test_user", "read")
    print(f"Permissions: {rbac.get_permissions()}")
    import scrypt
    from base64 import b64encode
    print(parse)
    print(HashPassword(parse.password,32))

    



