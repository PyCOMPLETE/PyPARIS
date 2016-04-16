import sys, os
BIN = os.path.expanduser("../../")
sys.path.append(BIN)
BIN = os.path.expanduser("../")
sys.path.append(BIN)

import multiprocessing as mp
import numpy as np

class mpComm(object):
	def __init__(self, N_nodes, pid, N_proc, queue_list,
					at_sync_list, done_sync, cnt):
		self._pid = pid
		self._N_proc = N_proc
		self._queue_list = queue_list
		self._at_sync_list = at_sync_list
		self._done_sync = done_sync
		self._cnt = cnt

	def Get_size(self):
		return self._N_proc

	def Get_rank(self):
		return self._pid
		
	def Barrier(self):
		with self._cnt.get_lock():
			self._cnt.value+=1
			print self._cnt.value
		while self._cnt.value<self._N_proc:
			pass
		


	#~ def Barrier(self):
		#~ myid = self._pid
		#~ self._at_sync_list[myid].set()
		#~ if myid == 0:
			#~ print 'Start sync'
			#~ for ii, e in enumerate(self._at_sync_list):
				#~ print 'Waiting for:', ii
				#~ with self._cnt:
					#~ e.wait()
					#~ e.clear()
				#~ print 'Done with:', ii
			#~ self._done_sync.set()
			#~ print 'Done sync'
		#~ else:
			#~ with self._cnt:
				#~ self._done_sync.wait()
				#~ self._done_sync.clear()

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

def todo(pid, N_nodes, queue_list,
					at_sync_list, done_sync, cnt):	

	comm = mpComm(N_nodes, pid, N_proc, queue_list,
					at_sync_list, done_sync, cnt)

	from ring_of_CPUs import RingOfCPUs
	from Simulation import Simulation
	simulation_content = Simulation()

	myCPUring = RingOfCPUs(simulation_content, N_pieces_per_transfer=5, comm=comm)

	myCPUring.run()


if __name__=='__main__':
	N_proc = 4
	queue_list = [mp.Queue() for _ in xrange(N_proc)]
	at_sync_list = [mp.Event() for _ in xrange(N_proc)]
	done_sync = mp.Event()
	cnt = mp.Value('i', 0)

	proc_list = []
	for pid in xrange(N_proc):
		proc_list.append(mp.Process(target=todo, 
			args=(pid, N_proc, queue_list,
					at_sync_list, done_sync, cnt)))
	for p in proc_list:
		p.start()
	for p in proc_list:
		p.join()
 
