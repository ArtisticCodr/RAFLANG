from interpreter.interpreter.interpreter import Interpreter
import argparse
import sys
import socket

code = ''
try:
    file = open('Interpreter/input.txt', 'r')
    code = file.read()    
except IOError:
    print("could not read from input")
 
 
try:
    interpreter = Interpreter(isDebug = True)
    interpreter.run(code)
except Exception as e:
    HOST = "localhost"
    PORT = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.sendall(bytes('ERROR: '+ str(e), 'utf-8'))
    sock.close()
