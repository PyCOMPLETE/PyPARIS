import sys, os
BIN = os.path.expanduser("../../")
sys.path.append(BIN)
BIN = os.path.expanduser("../")
sys.path.append(BIN)

import multiprocessing as mp
import numpy as np

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

def todo(pid, N_proc, queue_list,
					mutex, barriex, turnstile, turnstile2, cnt):	

	comm = mpComm(pid, N_proc, queue_list,
					mutex, barriex, turnstile, turnstile2, cnt)

	from ring_of_CPUs import RingOfCPUs
	#~ from Simulation import Simulation
	from Simulation_with_eclouds import Simulation
	simulation_content = Simulation()

	myCPUring = RingOfCPUs(simulation_content, N_pieces_per_transfer=5, comm=comm)

	myCPUring.run()


if __name__=='__main__':
	N_proc = 2

	queue_list = [mp.Queue() for _ in xrange(N_proc)]
	
	mutex = mp.Semaphore(1)
	barrier = mp.Semaphore(0)
	turnstile = mp.Semaphore(0)
	turnstile2 = mp.Semaphore(1)
	cnt = mp.Value('i', 0)

	proc_list = []
	for pid in xrange(N_proc):
		proc_list.append(mp.Process(target=todo, 
			args=(pid, N_proc, queue_list,
					mutex, barrier, turnstile, turnstile2, cnt)))
	for p in proc_list:
		p.start()
	for p in proc_list:
		p.join()
 
