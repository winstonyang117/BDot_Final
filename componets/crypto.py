from cryptography.fernet import Fernet

def encrypt_data(bytes_in, key):
    f = Fernet(key)
    return f.encrypt(bytes_in)

def decrypt_data(bytes_in, key):
    f = Fernet(key)
    return f.decrypt(bytes_in)

def encrypt_file(fn_in, key, fn_out=None):
    if fn_out == None:
        fn_out = fn_in + ".sec"

    with open(fn_in, 'rb') as file_in:
        buf = file_in.read()

        token = encrypt_data(buf, key)
        with open(fn_out, 'wb') as file_out:
            file_out.write(token)

def decrypt_file(fn_in, key, fn_out=None):
    with open(fn_in, 'rb') as file_in:
        buf = file_in.read()
        data = decrypt_data(buf, key)

        if fn_out:
            with open(fn_out, 'wb') as file_out:
                file_out.write(data)

        return data

config_key = b'W__MSG7tzKO9Tah5-WoExXhylLEUK7UBkAPEvzZBno0='


### tests
# key = Fernet.generate_key()
# key = b'W__MSG7tzKO9Tah5-WoExXhylLEUK7UBkAPEvzZBno0='   
# encrypt_file('../conf/config.sys', key, '../conf/config.sec')
#data = decrypt_file('../conf/config.sec', config_key)
#decrypt_file(b'../conf/config.sec', config_key, b'../conf/config.sec.sys')

"""
lip = encrypt_data(b'127.0.0.1', config_key)
lusr = encrypt_data(b'hmeng', config_key)
lpass = encrypt_data(b'hmeng', config_key)
rip = encrypt_data(b'192.168.1.251', config_key)
rusr = encrypt_data(b'hmeng', config_key)
rpass = encrypt_data(b'hmeng', config_key)

print(lip.decode())
print(lusr.decode())
print(lpass.decode())
print(rip.decode())
print(rusr.decode())
print(rpass.decode())

lip = decrypt_data(lip, config_key)
lusr = decrypt_data(lusr, config_key)
lpass = decrypt_data(lpass, config_key)
rip = decrypt_data(rip, config_key)
rusr = decrypt_data(rusr, config_key)
rpass = decrypt_data(rpass, config_key)

print(lip.decode())
print(lusr.decode())
print(lpass.decode())
print(rip.decode())
print(rusr.decode())
print(rpass.decode())
"""
