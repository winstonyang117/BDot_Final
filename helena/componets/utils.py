import os, sys

sys.path.insert(0, os.path.abspath('..'))
import componets.config as config
import componets.crypto as crypto

def decrypt(infile, outfile):
    crypto.decrypt_file(infile, config.license_key, outfile)

def encrypt(infile, outfile):
    crypto.encrypt_file(infile, config.license_key, outfile)

if __name__ == '__main__':
    arg = sys.argv 
    if len(arg) <3:
        print("Usage: python3 utils.py -D|E in_filename out_filename")
        print("Need at least three parameters. Exiting...")
        exit()
    
    if arg[1]=='-D':
        decrypt(arg[2], arg[3])
    else:
        encrypt(arg[2], arg[3])



