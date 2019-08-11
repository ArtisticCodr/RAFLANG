"""
This module file supports basic functions from stdio.h library
"""

from ..utils.utils import definition
from ..interpreter.number import Number
import socket
import sys

@definition(return_type='int', arg_types=None)
def toscreen(*args):
    params = args
        
    message = ''
    for param in params:
        if isinstance(param, Number):
            message += str(param.value)
        else:
            message += str(param)
        
    result = len(message)
    print(message, end='')
    
    
    message = message.replace("\n", "\\n")
    HOST = "localhost"
    PORT = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.sendall(bytes(message, 'utf-8'))
    sock.close()
    
    
    return result

@definition(return_type='int', arg_types=None)
def fromscreen(*args):
    from decimal import Decimal
    
    *params, memory = args

    elements = []
    while len(elements) < len(params):
        #string = input()
        
        
        soc = socket.socket() 
        host = "localhost"
        port = 5001
        soc.bind((host, port))
        soc.listen(5)
        
        conn, addr = soc.accept() 
        msg = conn.recv(1024)
        if '$exit$' in str(msg):
            soc.close()
            sys.exit()
        string = str(msg).split(':')[1]
        string = string[:-1]
        
        
        elements.extend(string.split('`'))
        
    i = 0
    for param in params:
        val = elements[i]
        i += 1
        
        if isinstance(memory[param], Number):
            if memory[param].type == 'int':
                memory[param] = Number('int', int(val))
            elif memory[param].type == 'float':
                memory[param] = Number('float', Decimal(val))
            elif memory[param].type == 'char':
                memory[param] = val[0]
        else:
            memory[param] = str(val)

    return len(elements)


@definition(return_type='char', arg_types=[])
def getchar():
    import sys
    return ord(sys.stdin.read(1))


