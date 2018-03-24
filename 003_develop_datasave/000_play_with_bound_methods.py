
class MyClass(object):
	def __init__(self):
		pass

ob = MyClass()

def hellofunc(self):
	print("Hello")
	return 1

import types 
ob.hello = types.MethodType(hellofunc, ob)

		