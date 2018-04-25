import socket 
import sys, time, os
import datetime as dt
import __builtin__ as builtins
from pyinotify import WatchManager, Notifier, ProcessEvent, EventsCodes
from pyinotify import IN_CLOSE_WRITE, IN_CLOSE_NOWRITE,IN_MODIFY, IN_CREATE, IN_DELETE
from optparse import OptionParser
e=sys.exit
DEFAULT_CHUNK_BYTES=100*1024
ERROR_CONNECTION_REFUSED = 1
ERROR_REMOTE_CONNECTION_RESET = 2
d = {'pid':os.getpid(), 'rows':0}

builtins.pid = os.getpid()
builtins.script_name=os.path.splitext(__file__)[0]
import  lib.init_job as init
ts, JOB_NAME, IMP_DATE, HOME, log, ts_dir = init.init()
d=init.d
def tail( f, lines=20 ):
	total_lines_wanted = lines

	BLOCK_SIZE = 1024
	f.seek(0, 2)
	block_end_byte = f.tell()
	lines_to_go = total_lines_wanted
	block_number = -1
	blocks = [] # blocks of size BLOCK_SIZE, in reverse order starting
				# from the end of the file
	while lines_to_go > 0 and block_end_byte > 0:
		if (block_end_byte - BLOCK_SIZE > 0):
			# read the last block we haven't yet read
			f.seek(block_number*BLOCK_SIZE, 2)
			blocks.append(f.read(BLOCK_SIZE))
		else:
			# file too small, start from begining
			f.seek(0,0)
			# only read what was not read
			blocks.append(f.read(block_end_byte))
		lines_found = blocks[-1].count('\n')
		lines_to_go -= lines_found
		block_end_byte -= BLOCK_SIZE
		block_number -= 1
	all_read_text = ''.join(reversed(blocks))
	return '\n'.join(all_read_text.splitlines()[-total_lines_wanted:])

def get_sender_name(path):
	return os.path.basename(path)
		
def Monitor(path):
	
	class PClose(ProcessEvent):
		path=path
		#fh=open(path,'rb')
		s=s
		host=host
		port=port
		fh=None

					
		#def __init__(self, *args):
		#	#self.fh.seek(0)
		#	ProcessEvent.__init__(self,*args)
		def sendData(self,data):
			try:
				self.s.send(data)
			except socket.error, err:
				exc, err, traceback = sys.exc_info()
				log.warn ('Remote connection %s:%d reset.' % (self.host,self.port), extra=d)
				#let's reset and try again
				self.s=None
				self.s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM, proto=0) 
				self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
				#s.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
				try:
					self.s.connect((self.host, self.port))
					self.s.send(data)
				except socket.error, err:
					exc, err, traceback = sys.exc_info()
					log.error ('Remote connection %s:%d reset 2.' % (self.host,self.port), extra=d)
					e(ERROR_REMOTE_CONNECTION_RESET)
				
				
				
		def sendDone(self, path):
			sender_name= get_sender_name(path)
			self.sendData('%d|DONE|%s|Finished|%d\n' % (1,sender_name,1))
			print (sender_name)
		def process_IN_CLOSE_NOWRITE(self, event):
			#print "File was closed without writing: " + event.pathname
			log.info("File was closed without writing: " + event.pathname, extra=d)
			
					
			
		def process_IN_CREATE(self, event):
			print "Creating:", event.pathname
			self.fh=open(event.pathname,'rb')
			self.fh.seek(0)
			sender_name= get_sender_name(event.pathname)
			try:
				self.s.send('%d|REGISTER|%s|register|%d\n' % (1,sender_name,0))	
				self.s.send('345|START|%s|started|%d\n' % (sender_name,2))
			except socket.error, err:
				exc, err, traceback = sys.exc_info()
				log.warn ('Remote connection %s:%d reset.' % (self.host,self.port), extra=d)
				#let's reset and try again
				self.s=None
				self.s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM, proto=0) 
				self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
				#s.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
				try:
					self.s.connect((self.host, self.port))
					self.s.send('%d|REGISTER|%s|register|%d\n' % (1,sender_name,0))	
					self.s.send('345|START|%s|started|%d\n' % (sender_name,2))
				except socket.error, err:
					exc, err, traceback = sys.exc_info()
					log.error ('Remote connection %s:%d reset 2.' % (self.host,self.port), extra=d)
					e(ERROR_REMOTE_CONNECTION_RESET)	
		def process_IN_DELETE(self, event):
			print "Removing:", event.pathname
			if self.fh:
				self.fh.close()
				
		def process_IN_CLOSE_WRITE(self, event):
			global j,fsize,iteration_id,delta_bytes	,delta_estimated,ts_dir	
			log.info( "File was closed with writing: " + event.pathname, extra=d)
			print 'process_IN_CLOSE_WRITE',  event.pathname
			#self.fh.seek(0)
			
			log.warn('DONE.', extra=d)
			#open(done_file,'w').write('DONE.')
			print 'log is at:',ts_dir
			#e(0)
			self.sendDone(event.pathname)
		def process_IN_MODIFY(self, event):
			
			global j,delta_estimated,loaded_so_far,iteration_id,delta_bytes,restart_log,ctl_fn,fsize
			#print str(j)+" --> File was modified: " + event.pathname, os.stat(event.pathname).st_size, min_estimate_size
			j +=1
			print 'process_IN_MODIFY %d' %j,  event.pathname
			if 1: 
				fsize=os.stat(event.pathname).st_size
				print event.pathname
				data= self.fh.read(4*1024)
				print (fsize), len(data)
				self.sendData(data)
		
		def process_default(self, event):
			# Implicitely IN_CREATE and IN_DELETE are watched too. You can
			# ignore them and provide an empty process_default or you can
			# process them, either with process_default or their dedicated
			# method (process_IN_CREATE, process_IN_DELETE) which would
			# override process_default.
			print 'default: ', event.maskname				
	s=None

	wm = WatchManager()
	#pprint(dir(wm))
	notifier = Notifier(wm, PClose())
	wm.add_watch(path, IN_CLOSE_WRITE|IN_CLOSE_NOWRITE|IN_MODIFY|IN_CREATE|IN_DELETE)
	#wm.watch_transient_file(path, IN_CLOSE_WRITE|IN_CLOSE_NOWRITE|IN_MODIFY|IN_CREATE|IN_DELETE, PClose)
	j=0
	if 1:
		try:
			while 1:
				notifier.process_events()
				print j
				j +=1
				if notifier.check_events():
					#pprint(dir(notifier))
					notifier.read_events()
					#print v
					
				#e(0)
		except KeyboardInterrupt:
			notifier.stop()
			return
def print_error():
	exc, err, traceback = sys.exc_info()
	print ('Connection to ')
	print (exc, traceback.tb_frame.f_code.co_filename, 'ERROR ON LINE', traceback.tb_lineno, '\n', err)
	del exc, err, traceback	
	
if __name__ == '__main__':
	#%(levelname)s|%(asctime)s|%(pid)d|%(name)s|%(script)s|%(method)s|%(message)s
	FMT= init.FORMAT.replace('%(', '{').replace(')s', '}').replace(')d', '}')
	#print(FMT)
	#{levelname}|{asctime}|{pid}|{name}|{script}|{method}|{message}
	msg={'levelname':'','asctime':ts,'pid':os.getpid(),'name':JOB_NAME,'script':script_name,'method':'main','message':'test'}
	print (FMT.format(**msg))
	#print(init.FORMAT)
	#e(0)

	
	parser = OptionParser()
	#parser.add_option("-i", "--input_file", dest="input_file", type=str, default='/Bic/scripts/oats/py27/bin/log/testjob/2017-02-08-101243/testjob_2017-02-08-101243.log')
	parser.add_option("-i", "--input_dir", dest="input_dir", type=str, default='/Bic/scripts/oats/py27/bin/log/testjob/2017-02-11-103032/')
	parser.add_option("-c", "--chunk_size_bytes", dest="chunk_size_bytes", type=str, default=DEFAULT_CHUNK_BYTES)
	(opt, args) = parser.parse_args()
	s=None
		
	n1=dt.datetime.now()
	#s = socket.socket()
	s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM, proto=0) 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	#s.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)

	host = 'WHKWDCTGABUZUN1' 	
	port = 12349
	try:	# Reserve a port for your service.
		s.connect((host, port))
	except socket.error, err:
		exc, err, traceback = sys.exc_info()
		log.error ('Connection to %s:%d is refused.' % (host,port), extra=d)
		e(ERROR_CONNECTION_REFUSED)

	
	print 'Sending..',
	counter=0
	j=0
	


	
	#assert os.path.isfile(opt.input_dir)
	path = opt.input_dir
	
	#msg={'levelname':'','asctime':ts,'pid':os.getpid(),'name':JOB_NAME,'script':script_name,'method':'main','message':'test'}
	#msg.update({'levelname':'REGISTER'})
	#print (FMT.format(**msg))
	#s.send(FMT.format(**msg))
	#e(0)
	#msg.update({'levelname':'START'})
	#s.send(FMT.format(**msg))

	
	log.warn('Waiting for data from log file.', extra=d)
	#fh=open(path,'rb')
	#fh.seek(0)
	Monitor(path)		
	
	
	print "Done Sending"
	#s.shutdown(socket.SHUT_WR)
	s.close
	n2=dt.datetime.now()
	diff=(n2-n1)
	print diff.seconds
	e(0)
