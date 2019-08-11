from interpreter.interpreter.interpreter import Interpreter
import argparse
import sys

code = ''
try:
    file = open('D:/input.txt', 'r')
    code = file.read()
except IOError:
    print("could not read from input")
 
interpreter = Interpreter()
interpreter.run(code)

    
