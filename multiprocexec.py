#!/usr/bin/env python

import multiprocessing as mp
import numpy as np
import os, sys

class mpComm(object):
	def __init__(self, pid, N_proc, queue_list,
					mutex, barriex, turnstile, turnstile2, cnt):
		self._pid = pid
		self._N_proc = N_proc
		self._queue_list = queue_list
		self.mutex = mutex
		self.turnstile = turnstile
		self.turnstile2 = turnstile2
		self.cnt = cnt
		
	def Get_size(self):
		return self._N_proc

	def Get_rank(self):
		return self._pid
		
	def Barrier(self):
		self.mutex.acquire()
		self.cnt.value += 1
		if self.cnt.value == self._N_proc:
			self.turnstile2.acquire()
			self.turnstile.release()
		self.mutex.release()
		self.turnstile.acquire()
		self.turnstile.release()
		#criticalpoint
		self.mutex.acquire()
		self.cnt.value -= 1
		if self.cnt.value == 0:
		   self.turnstile.acquire()
		   self.turnstile2.release()
		self.mutex.release()
		self.turnstile2.acquire()
		self.turnstile2.release()
		


	def Sendrecv(self, sendbuf, dest, sendtag, recvbuf, source, recvtag):
		self._queue_list[dest].put(sendbuf)
		temp = self._queue_list[self._pid].get()
		recvbuf[:len(temp)]=temp

	def Bcast(self, buf, root):
		self.Barrier()
		if self._pid==root:
			for ii, q in enumerate(self._queue_list):
				if ii!=root:
					q.put(buf)
		else:
			temp = self._queue_list[self._pid].get()
			buf[:len(temp)]=temp
		self.Barrier()

def todo(sim_module_string, pid, N_proc, queue_list,
					mutex, barriex, turnstile, turnstile2, cnt):	

	comm = mpComm(pid, N_proc, queue_list,
					mutex, barriex, turnstile, turnstile2, cnt)

	BIN = os.path.expanduser("./")
	sys.path.append(BIN)

	sim_module_strings = sim_module_string.split('.')
	if len(sim_module_strings)!=2:
		raise(ValueError('\n\nsim_class must be given in the form: module.class.\nNested referencing not implemented.\n\n'))
	module_name = sim_module_strings[0]
	class_name = sim_module_strings[1]
		
	
	SimModule = __import__(module_name)
	SimClass = getattr(SimModule, class_name)
	
	from ring_of_CPUs import RingOfCPUs
	simulation_content = SimClass()
	myCPUring = RingOfCPUs(simulation_content, comm=comm)
	myCPUring.run()
					
	

	


if __name__=='__main__':
	import sys
	
	print repr(sys.argv)
	
	if len(sys.argv)!=4:
		raise ValueError('\n\nSyntax must be:\n\t python multiprocexec -n N_proc sim_class=module.class\n\n')
	if '-n' not in sys.argv[1] or 'sim_class' not in sys.argv[3]:
		raise ValueError('\n\nSyntax must be:\n python multiprocexec -n N_proc sim_class=module.class\n\n')
	
	N_proc = int(sys.argv[2])

	sim_module_string = sys.argv[3].split('=')[-1]
	
	queue_list = [mp.Queue() for _ in xrange(N_proc)]
	
	mutex = mp.Semaphore(1)
	barrier = mp.Semaphore(0)
	turnstile = mp.Semaphore(0)
	turnstile2 = mp.Semaphore(1)
	cnt = mp.Value('i', 0)

	proc_list = []
	for pid in xrange(N_proc):
		proc_list.append(mp.Process(target=todo, 
			args=(sim_module_string, pid, N_proc, queue_list,
					mutex, barrier, turnstile, turnstile2, cnt)))
	for p in proc_list:
		p.start()
	for p in proc_list:
		p.join()
 
