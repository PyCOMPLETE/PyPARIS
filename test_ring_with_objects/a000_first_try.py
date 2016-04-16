import multiprocessing as mp
import time
import numpy as np

class mpComm(object):
	def __init__(self, N_nodes, pid, N_proc, queue_list,
					at_sync_list, done_sync):
		self._pid = pid
		self._N_proc = N_proc
		self._queue_list = queue_list
		self._at_sync_list = at_sync_list
		self._done_sync = done_sync

	def Get_size(self):
		return self._N_proc

	def Get_rank(self):
		return self._pid

	def Barrier(self):
		myid = self._pid
		self._done_sync.clear()
		self._at_sync_list[myid].set()
		if myid == 0:
			for e in self._at_sync_list:
				e.wait()
				e.clear()
			self._done_sync.set()
		else:
			self._done_sync.wait()

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
					at_sync_list, done_sync):	

	comm = mpComm(N_nodes, pid, N_proc, queue_list,
					at_sync_list, done_sync)

	myid = comm.Get_rank()
	temp_buff = np.array(4*[0.])
	temp_int_buf = np.array(4*[0])
	for i_turn in xrange(10):
		
		comm.Sendrecv(np.array(3*[0.])+myid, 
			(myid+1)%N_nodes, -1, temp_buff, (myid-1)%N_nodes, -1)

		bcastroot = 1
		if myid == bcastroot:
			bcastbuf = np.array([2, 2, 2])
			comm.Bcast(bcastbuf, root=bcastroot)
		else:
			comm.Bcast(temp_int_buf, root=bcastroot)

		print 'Turn %d,  I am %d/%d, rec=%d, bcast=%d'%(i_turn,
			myid, comm.Get_size(), temp_buff[0], temp_int_buf[0]), repr(temp_buff)
			
		time.sleep(np.random.rand())

		assert(int(temp_buff[0])==((myid-1)%N_nodes))


		comm.Barrier()
		
		comm.Barrier()
		

if __name__=='__main__':
	N_proc = 3
	queue_list = [mp.Queue() for _ in xrange(N_proc)]
	at_sync_list = [mp.Event() for _ in xrange(N_proc)]
	done_sync = mp.Event()

	proc_list = []
	for pid in xrange(N_proc):
		proc_list.append(mp.Process(target=todo, 
			args=(pid, N_proc, queue_list,
					at_sync_list, done_sync)))
	for p in proc_list:
		p.start()
	for p in proc_list:
		p.join()
 
