# Title: 	logger-ui
# Description:
#			Logger GUI.		
# Environment:
#			Python 3.5 and wxPython 3.0	
#
from __future__ import print_function
__author__ = "PyDemo"
__copyright__ = "Copyright 2017, PyDemo"
__credits__ = []
__appname__='logger-ui'
__license__ = "GPL"
__title__ = "logger-ui"
__version__ = "2"
__maintainer__ = "PyDemo"
__email__ = "pydemo.git@gmail.com"
__github__=	''
__status__ = "Development" 
import os, sys
import imp, traceback, time
import socket
from multiprocessing import freeze_support 
import argparse
import random
#import wx.lib.sized_controls as sized_ctrls


import wx
import wx.lib.inspection
import wx.lib.mixins.inspection
from wx.aui import AuiManager, AuiPaneInfo, AuiToolBar, \
AUI_TB_DEFAULT_STYLE, AUI_TB_VERTICAL, AUI_TB_OVERFLOW
from wx.py import shell, version

#from asyncio import Lock

from six.moves import _thread
import wx.lib.newevent
(UpdateLogEvent, EVT_UPDATE_REMOTELOG) = wx.lib.newevent.NewEvent()
#print (UpdateLogEvent, EVT_UPDATE_REMOTELOG)

(UpdateBarEvent, EVT_UPDATE_BARGRAPH) = wx.lib.newevent.NewEvent()
print (UpdateBarEvent, EVT_UPDATE_BARGRAPH)

UPDATE_MS=1000
LOG_LIST_DISPLAY_SIZE=20 #number of messages to display in remote_log control
outdir='out'
if not os.path.isdir(outdir):
	os.makedirs(outdir)
class CalcBarThread:
	def __init__(self, win, barNum, val):
		self.win = win
		self.barNum = barNum
		self.val = val

	def Start(self):
		self.keepGoing = self.running = True
		_thread.start_new_thread(self.Run, ())

	def Stop(self):
		self.keepGoing = False

	def IsRunning(self):
		return self.running

	def Run(self):
		while self.keepGoing:
			# We communicate with the UI by sending events to it. There can be
			# no manipulation of UI objects from the worker thread.
			evt = UpdateLogEvent(barNum = self.barNum, value = int(self.val))
			wx.PostEvent(self.win, evt)

			sleeptime = (random.random() * 2) + 0.5
			time.sleep(sleeptime/4)

			sleeptime = sleeptime * 5
			if int(random.random() * 2):
				self.val = self.val + sleeptime
			else:
				self.val = self.val - sleeptime

			if self.val < 0: self.val = 0
			if self.val > 300: self.val = 300
			time.sleep(2)
		self.running = False
		

class NetcatReader:
	def __init__(self, win, ts, fn):
		self.win = win
		self.ts = ts
		self.fn = fn
		self.timeout=60*60 # one hour
		self.chunksize=100*1024
		self.bytes_written=0

	def Start(self):
		self.keepGoing = self.running = True
		
		_thread.start_new_thread(self.Run, ({'host':socket.gethostname(), 'port':12349, 'outfile':self.fn},))

	def Stop(self):
		self.keepGoing = False

	def IsRunning(self):
		return self.running

	def Run0(self):
		while self.keepGoing:
			# We communicate with the UI by sending events to it. There can be
			# no manipulation of UI objects from the worker thread.
			evt = UpdateLogEvent(barNum = self.barNum, value = int(self.val))
			wx.PostEvent(self.win, evt)

			sleeptime = (random.random() * 2) + 0.5
			time.sleep(sleeptime/4)

			sleeptime = sleeptime * 5
			if int(random.random() * 2):
				self.val = self.val + sleeptime
			else:
				self.val = self.val - sleeptime

			if self.val < 0: self.val = 0
			if self.val > 300: self.val = 300
			time.sleep(2)
		self.running = False
	def Run(self,data):
		host, port, fn = data['host'], data['port'], data['outfile']
		#s = socket.socket()         # Create a socket object
		timed_out=True
		fid=0
		#while timed_out:
		
		if 1:
			try:
		
				#print (1,flush=True, end='')
				s= socket.socket(socket.AF_INET, type=socket.SOCK_STREAM, proto=0)
				s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
				s.setblocking(False)
				s.settimeout(self.timeout)
				#timed_out=False
				#print (2)
				log_file_name='%s_%d.log' % (fn, fid)
				f = open(log_file_name,'wb')
				f.seek(0)
				fid +=1
				#f.write('test')
				#f.close()
					
						
				
				#s.settimeout(10)
				#s.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
				#host = socket.gethostname() # Get local machine name
				#port = port                 # Reserve a port for your service.
				#print (port)
				s.bind((host, port))        # Bind to the port
				
				s.listen(5)                 # Now wait for client connection.
				i=0
				
				while self.running:
					
					c, addr = s.accept()     # Establish connection with client.
					c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
					c.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
					c.setblocking(False)
					c.settimeout(self.timeout)
					#c.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
					print ('Got connection from', addr)
					print ("Receiving...")
					#netcat.write('netcat from file writer')
					
					l = c.recv(self.chunksize)
					
					#f.write(l)
					#print (l)
					#f.write(l)
					#f.close()
					#f = open(r'C:\Temp\example_lines1.txt','wb')
					#f.write('test')
					#f.close()
					#pprint(dir(c))
					while (l):
						evt = UpdateLogEvent(barNum = 1, value = (log_file_name,len(l), self.bytes_written))
						wx.PostEvent(self.win, evt)
						self.bytes_written +=len(l)
						f.write(l)
						#await asyncio.sleep(0.1)
						#print "*",
						#if i%10000==0:
						#		netcat.write('Chunk# %d' % i)
						#f = open('/tmp/torecv_%d.png' % i,'wb')
						
						#f.close()
						l = c.recv(self.chunksize)
						#self.bytes_written +=len(l)
						#f.write(l)
						print (len(l), end='')
						i +=1


					#f.close()

					#c.send('Thank you for connecting')
					c.close()
					#s.shutdown(socket.SHUT_WR)
					#s.close()
					print ("Done Receiving %s" %  i)
					#del netcat
					#e(0)
					s.listen(5) 
				s.close()
				f.close()
			except socket.timeout as er1:
				
				err = er1.args[0]
				#pprint(er1.args)
				print ('EXCEPTION-----socket.timeout')
				timed_out=True
				f.close()
				s.close()
				#raise er1			
			except socket.error as er3:
				
				err = er3.args[0]
				#print (er3.args)			
				f.close()
				s.close()
				timed_out=False
				raise er3
			except Exception as ex:
				
				f.close()
				s.close()
				raise	
					
		self.running = False

if 0:
	import asyncio
	import signal
	import functools
	asyncio.PYTHONASYNCIODEBUG=1
if 1:
	try:
		from pubsub import pub
	except ImportError:
		from wx.lib.pubsub import pub
		
if 0:
	try:
		# Python 3.4+
		if sys.platform.startswith('win'):
			import multiprocessing.popen_spawn_win32 as forking
		else:
			import multiprocessing.popen_fork as forking
	except ImportError:
		import multiprocessing.forking as forking
	if sys.platform.startswith('win'):
		# First define a modified version of Popen.
		class _Popen(forking.Popen):
			def __init__(self, *args, **kw):
				if hasattr(sys, 'frozen'):
					# We have to set original _MEIPASS2 value from sys._MEIPASS
					# to get --onefile mode working.
					os.putenv('_MEIPASS2', sys._MEIPASS)
				try:
					super(_Popen, self).__init__(*args, **kw)
				finally:
					if hasattr(sys, 'frozen'):
						# On some platforms (e.g. AIX) 'os.unsetenv()' is not
						# available. In those cases we cannot delete the variable
						# but only set it to the empty string. The bootloader
						# can handle this case.
						if hasattr(os, 'unsetenv'):
							os.unsetenv('_MEIPASS2')
						else:
							os.putenv('_MEIPASS2', '')

		# Second override 'Popen' class with our modified version.
		forking.Popen = _Popen
	import multiprocessing

	class SendeventProcess(multiprocessing.Process):
		def __init__(self, resultQueue):
			self.resultQueue = resultQueue
			multiprocessing.Process.__init__(self)
			self.start()

		def run(self):
			print ('SendeventProcess')
			self.resultQueue.put((1, 2))
			print ('SendeventProcess')

from pprint import pprint
from locale import getdefaultlocale, setlocale, LC_ALL
#setlocale(LC_ALL, '')
e=sys.exit
default_fullscreen_style = wx.FULLSCREEN_NOSTATUSBAR | wx.FULLSCREEN_NOBORDER | wx.FULLSCREEN_NOCAPTION
import gettext
_ = gettext.gettext

from operator import or_
loop= None # coro loop
FlagList = ['FULLSCREEN_NOMENUBAR',
	'FULLSCREEN_NOTOOLBAR',
	'FULLSCREEN_NOSTATUSBAR',
	'FULLSCREEN_NOBORDER',
	'FULLSCREEN_NOCAPTION',
	'FULLSCREEN_ALL']
colours = [
	"BLACK",
	"BLUE",
	"BLUE VIOLET",
	"BROWN",
	"CYAN",
	"DARK GREY",
	"DARK GREEN",
	"GOLD",
	"GREY",
	"GREEN",
	"MAGENTA",
	"NAVY",
	"PINK",
	"RED",
	"SKY BLUE",
	"VIOLET",
	"YELLOW",
	] 
	
class MessageList(wx.ListCtrl):
	def __init__(self, parent,win, ID=wx.ID_ANY, pos=wx.DefaultPosition,
						size=wx.DefaultSize, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.LC_SORT_ASCENDING):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		self.win=win
		self.InsertColumn(0, "Type")
		self.InsertColumn(1, "Time")
		self.InsertColumn(2, "Pid")
		self.InsertColumn(3, "Job")
		self.InsertColumn(4, "Script")
		self.InsertColumn(5, "Method")
		self.InsertColumn(6, "Message")
		#self.InsertColumn(4, "Cycle [ms]")
		self.SetColumnWidth(0, 40)
		self.SetColumnWidth(1, 80)
		self.SetColumnWidth(2, 50)
		self.SetColumnWidth(3, 50)
		self.SetColumnWidth(4, 80)
		self.SetColumnWidth(5, 80)
		self.SetColumnWidth(6, 800)
		#self.SetColumnWidth(4, 75)
		#self.last_chunk=parent.last_chunk
		self.log_errors=[]
		self.log_start=[]
		self.log_done=[]
		self.old_item=-1
		self.Bind(wx.EVT_MOTION, self.onMouseOver)
	# either add messages to the listctrl or update the existing ones if 
	def onMouseOver(self, evt):
		x,y  = evt.GetX(), evt.GetY()
		item, flags = self.HitTest((x, y))
		if item > 0:
			if 0:
				self.SetItemBackgroundColour(item,"#3246A8")
				if self.old_item>0 and item !=self.old_item:
					self.SetItemBackgroundColour(self.old_item,wx.WHITE)
			
				self.old_item=item
			status = self.GetItem(item,0).GetText()
			self.SetToolTipString("STATUS:%s\nTIMESTAMP:%s\nJOB:\t%s\nMESSAGE:\n%s" % (self.GetItem(item,0).GetText(), self.GetItem(item,1).GetText(),self.GetItem(item,2).GetText(),self.GetItem(item,3).GetText()))
	
		#print ('onMouseOver',x,y, item, flags)
	
	def Populate(self, msg_store):
		#self.Freeze()
		item=-1
		if 0:
			while 1:
				item = self.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE)
				if item == -1: break
				if self.GetItemText(item) not in msg_store:
					self.DeleteItem(item)

		for msg_id in msg_store:
			
			item = self.FindItem(-1, msg_id)
			msg = msg_store.get(msg_id)
			#print(msg_id, msg)
			#print(msg.DATA)
			interval = randint(10,1000)
			# insert new messages
			if item == -1:
				item = self.InsertItem(1000, msg_id)
				self.SetItem(item, 1, 'std')
			# fill in other columns
			self.SetItem(item, 2, '%1d'%msg.LEN)
			self.SetItem(item, 3, ' '.join(['%02x'%d for d in msg.DATA[:msg.LEN]]))
			self.SetItem(item, 4, '%d'%interval)
		#self.Thaw()
	def Populate2(self, data):
		#self.Freeze()
		if data:
			last_log_list= data[:10000].split(b'\n')
			item=-1
			if 0:
				while 1:
					item = self.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE)
					if item == -1: break
					if self.GetItemText(item) not in msg_store:
						self.DeleteItem(item)
			
			#self.store.append(msg_store)
			#print ('appended ',len(msg_store))
			col_count=5
			emty_row=['']*col_count
			
			lcount=  self.GetItemCount()
			for i, val in enumerate(last_log_list):
				print(val)
				cols=val.split(b'|')

				if len(cols) ==7:

					item = self.InsertItem(0, cols[0])
					if cols[0].decode('ascii').upper() in 'ERROR':
						#pprint (cols)
						#self.log_errors[cols[4].decode('ascii')]= cols
						self.SetItemTextColour(item, wx.RED)
						#self.win.svg_panel.graph.setColor(cols[4].decode('ascii'),True)
					self.SetItem(item, 1, cols[1])
					# fill in other columns
					self.SetItem(item, 2, cols[2])
					self.SetItem(item, 3, cols[3])
					self.SetItem(item, 4, cols[4])
					self.SetItem(item, 5, cols[5])
					self.SetItem(item, 6, cols[6])
				else:
					print ('cols len %d' % len(cols))
			#print(lcount)
			if 0:
				log_length= len(last_log_list[:LOG_LIST_DISPLAY_SIZE])
				#print ('----------------------------------', log_length)
				if log_length:
					for i in range(LOG_LIST_DISPLAY_SIZE):
						if i>log_length-1:
							cols=['']*col_count
						else:
							cols=last_log_list[i].split(b'|')
						#print (i)
						#msg=last_log_list[:LOG_LIST_DISPLAY_SIZE][i]
						#print (msg)
						if 1:
							#item = self.FindItem(-1, msg_id)
							#msg = msg_store.get(msg_id)
							#print(msg_id, msg)
							#print(msg.DATA)
							#interval = randint(10,1000)
							# insert new messages
							#if item == -1:

							#e(0)
							#cols=msg.split(b'|')
							#print (cols)
							#print ('self.GetItemCount()',self.GetItemCount())
							if len(cols) < col_count:						
								if i in [0]:
									cols=['']*(col_count-len(cols)+1) + cols[1:]
								else:
									cols=cols+['']*(col_count-len(cols))					
							if lcount ==0: #first page
								#pprint(cols)
								item = self.InsertItem(i, cols[0])
								self.SetItem(item, 1, cols[1])
								# fill in other columns
								self.SetItem(item, 2, cols[2])
								self.SetItem(item, 3, cols[3])
								#self.SetItem(item, 4, cols[4])
								#pprint(last_log_list[:LOG_LIST_DISPLAY_SIZE])
								#e(0)
							else:

			
								#print (i,self.GetItemCount(), cols)	
								self.SetItem(i, 0,cols[0])
								#print ('setting o to:',cols[0] )
								self.SetItem(i, 1,cols[1])
								# fill in other columns
								self.SetItem(i, 2,  cols[2])
								self.SetItem(i, 3, cols[3])
								#self.SetItem(i, 4, cols[4])
	
				
	def PopulateErrors(self, data):
		#self.Freeze()
		new_errors=0
		if data:
			#print ('PopulateErrors', len(data), end=' ')
			#print (len(data.split(b'ERROR')))
			for d in data.split(b'ERROR')[1:]:
				#print(d[:d.find(b'\n')])
				self.log_errors.append(d[:d.find(b'\n')])
				new_errors +=1
			col_count=5
			emty_row=['']*col_count
			
			lcount=  self.GetItemCount()
			
			
			
			if new_errors:
				for id,error_log_row in enumerate(self.log_errors[-new_errors:]):
					cols=error_log_row.split(b'|')

					#print ('adding',lcount+id)
					i=0
					item = self.InsertItem(lcount+id, '')
					#f = item.GetItemFont(0)
					#f.SetWeight(wx.BOLD)
					#w.SetItemFont(f)
					self.SetItemTextColour(item, wx.RED)
					self.SetItem(item, 0, 'ERROR')
					# fill in other columns
					self.SetItem(item, 1, cols[1])
					self.SetItem(item, 2, cols[2])
					self.SetItem(item, 3, cols[3])
					self.SetItem(item, 4, cols[4])
					self.SetItem(item, 5, cols[5])
					self.SetItem(item, 6, cols[6])
				#index = self.GetFirstSelected()
				#print ('selected',index)
				#self.EnsureVisible((index))
			
class MessagesTab(wx.Panel):
	def __init__(self, parent, win, group_name):
		msg_size=650    # width of messge windows
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.last_chunk=[]
		self.win=win
		self.group_name=group_name
		self.log_data=win.log_data
		#self.SetDoubleBuffered(False)
		
		self.splitter = wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_3D | wx.SP_BORDER)
		self.p1 = wx.Panel(self.splitter, wx.ID_ANY)
		self.p2 = wx.Panel(self.splitter, wx.ID_ANY)
		
		sentLabel=wx.StaticText(self.p1, wx.ID_ANY, 'Messages Received')
		sentLabel.SetForegroundColour('dark slate blue')
		IncomingLogMsgList = MessageList(self.p1, win, size=wx.Size(msg_size,150))
		self.p1.v_sizer=wx.BoxSizer(wx.VERTICAL)
		self.p1.v_sizer.Add(sentLabel, 0, wx.EXPAND|wx.ALL, 5)
		self.p1.v_sizer.Add(IncomingLogMsgList, 1, wx.EXPAND|wx.ALL, 0)				
		self.p1.SetSizer(self.p1.v_sizer)
		
		
		
		errorLabel=wx.StaticText(self.p2, wx.ID_ANY, 'Errors Received')
		#errorLabel.SetSizerProps(valign="center")
		errorLabel.SetForegroundColour('blue')	
		ErrorMsgList = MessageList(self.p2, win, size=wx.Size(msg_size,150))
		b_refresh_errors = wx.Button(self.p2, -1, "Refresh",size=(60,30))
		
		

		
		self.p2.h_sizer=wx.BoxSizer(wx.HORIZONTAL)
		self.p2.h_sizer.Add(errorLabel, 1, wx.ALIGN_CENTER|wx.EXPAND|wx.ALL, 5)
		self.p2.h_sizer.Add(b_refresh_errors, 0, wx.ALIGN_RIGHT)
		
		self.p2.v_sizer=wx.BoxSizer(wx.VERTICAL)
		line = wx.StaticLine(self.p2)
		self.p2.v_sizer.Add(line, 0, wx.EXPAND|wx.ALL, 0) 
			
		self.p2.v_sizer.Add(self.p2.h_sizer, 0, wx.EXPAND|wx.ALL, 0)
		#sizer.Add(errorLabel, 0, wx.EXPAND|wx.ALL, 2)
		self.p2.v_sizer.Add(ErrorMsgList, 1, wx.EXPAND|wx.ALL, 0)
		self.p2.SetSizer(self.p2.v_sizer)	
		#b = wx.Button(self, wx.ID_ANY, 'Clear messages', name='clear_stale')
		#self.Bind(wx.EVT_BUTTON, self.OnClearMessages, b)
		#sizer.Add(b, proportion=0, flag=wx.ALL, border=4)
		v_sizer=wx.BoxSizer(wx.VERTICAL)
		self.splitter.SplitHorizontally(self.p1, self.p2)
		self.splitter.SetSashPosition(800, True) 
		#self.splitter.SetMinimumPaneSize(500)
		v_sizer.Add(self.splitter, 1, wx.EXPAND, 0)
		self.SetSizer(v_sizer)
		v_sizer.Fit(self)
		self.Layout()
		self.IncomingLogMsgList = IncomingLogMsgList
		self.ErrorMsgList = ErrorMsgList
		self.Bind(EVT_UPDATE_REMOTELOG, self.OnReceive)
		self.lfh={}
		self.log_done={}
		self.log_start={}
		self.log_error={}
		self.log_tree={}
		self.percent={}
		self.first_percent=50
		self.percent_increment= 25
		self.max_percents =200
		
	def OnReceive(self, evt):
	
		self.last_chunk=evt.value
		
		#print('last_chunk ',self.last_chunk[0:])

		
	def UpdateRemoteLogList(self):
		print('UpdateRemoteLogList')
		try :
			chunk=self.log_data.pop(0)
			#print (3444444444333, chunk)
			if chunk:
				#print (time.strftime('%Y%m%d_%a_%H%M%S'))
				#pprint(self.last_chunk)
				(lfn, start_from_len ,data) = chunk

				self.IncomingLogMsgList.Populate2(data)
				self.ErrorMsgList.PopulateErrors(data)
				self.PopulateStart(data)
				self.PopulateDone(data)
				if start_from_len<100000:
					self.PopulateTree(data)
				self.last_chunk=None
				#update graph

				#print (self.win.svg_panel.graph.values)
				
		except IndexError:
			print ('log_data is empty')
		#pprint(self.log_done.keys())
		
		labels=[k.decode('ascii') for k in self.log_start.keys()]
		#self.win.svg_panel.graph.values={}
		gr=self.win.svg_panel.graph
		#increment percents:
		for l in labels:
			if not l in  self.percent.keys():
				self.percent[l]=-self.first_percent
			else:
				self.percent[l] +=self.percent_increment

				
		for label in labels:	
			gr.values[label]= [self.percent[label]%250+25,str(self.percent[label]), wx.BLUE]
			#self.win.svg_panel.graph.SetValue(i, i*100)
		for k in self.log_done.keys():
			#self.percent[k.decode('ascii')]=self.max_percents
			gr.values[k.decode('ascii')] = [self.max_percents, 'Done', wx.GREEN]
		if len(self.log_done)==0 or len(self.log_start)==0:
			gr.values[self.group_name]=[1, '0/0',  wx.RED]
		else:
			gr.values[self.group_name]=[(self.max_percents)/len(self.log_start)*len(self.log_done),' %s/%s' % (len(self.log_done),len(self.log_done)), wx.RED]
		gr.Refresh(True)
		#self.percent +=50
		#pprint(self.percent)		
	def PopulateStart(self, data):
		new_start=0
		if data:
			#print ('PopulateErrors', len(data), end=' ')
			#print (len(data.split(b'ERROR')))
			iter=data.split(b'|START|')
			#pprint(iter)
			#pprint(iter[1:])
			#e(0)
			for i,d in enumerate(iter[1:],1):
				#print(d[:d.find(b'\n')])
				prevd=iter[i-1]
				prev_line=prevd[prevd.rfind(b'\n'):]
				
				row=(prev_line.strip(b'\n')+b'|'+d[:d.find(b'\n')]).split(b'|')
				#pprint(row)
				self.log_start[row[1]]= row
				
				#self.log_start.append(d[:d.find(b'\n')])
				new_start +=1
			#pprint(self.log_start)
			#print(self.log_start)
	def PopulateDone(self, data):
		new_done=0
		if data:
			#print ('PopulateErrors', len(data), end=' ')
			#print (len(data.split(b'ERROR')))
			iter=data.split(b'|DONE|')
			for i,d in enumerate(iter[1:],1):
				#print(d[:d.find(b'\n')])
				prevd=iter[i-1]
				prev_line=prevd[prevd.rfind(b'\n'):]				
				row=(prev_line.strip(b'\n')+b'|'+d[:d.find(b'\n')]).split(b'|')
				self.log_done[row[1]]= row
				new_done +=1		
			#print(self.log_done)
	def PopulateTree(self, data):
		new_register=0
		if data:
			#print ('PopulateErrors', len(data), end=' ')
			iter=data.split(b'|REGISTER|')
			for i,d in enumerate(iter[1:],1):
				prevd=iter[i-1]
				prev_line=prevd[prevd.rfind(b'\n'):]				
				row=(prev_line.strip(b'\n')+b'|'+d[:d.find(b'\n')]).split(b'|')
				#pprint(row)
				self.log_tree[row[1]]= row
				new_register +=1		
			#print(self.log_tree)			
	def OnClearMessages(self, event):
		self.SentMsgList.DeleteAllItems()
		self.ReceivedMsgList.DeleteAllItems()	
	def RunMP(self):
		print('MP')
		self.threads = []
		ts=time.strftime('%Y%m%d_%a_%H%M%S')
		fn=os.path.join(outdir,'netcat_%s_incoming' % ts) #timestamp
		self.threads.append(NetcatReader(self, ts, fn))
		
		for t in self.threads:
			t.Start()

		
			
class log_ctrl(wx.TextCtrl):
	def __init__(self, *args, **kwargs):
		self.file_name = kwargs.pop('file_name', 'log.txt')
		self.main_frame = kwargs.pop('main_frame', None)
		self.add_to_file = kwargs.pop('add_to_file', False)
		if self.main_frame is None:
			self.main_frame = args[0]
		super(log_ctrl, self).__init__(*args, **kwargs)
		self.Bind(EVT_UPDATE_REMOTELOG, self.OnUpdate)
	def __write__(self, content):
		self.WriteText(content)
	def show_control(self, ctrl_name = 'log_ctrl'):
		if self.main_frame is not None:
			if hasattr(self.main_frame,'aui_manager'):
				self.main_frame.show_aui_pane_info(ctrl_name)
		self.SetInsertionPointEnd()
		if self.add_to_file: self.flush()
	def write(self, content):
		self.show_control()
		self.__write__(content)
	def writeline(self, content):
		self.show_control()
		self.__write__(content+'\n')		
	def writelines(self, l):
		self.show_control()
		map(self.__write__, l)
	def flush(self):
		self.SaveFile(self.file_name)
	def print_error(self):
		exc, err, traceback = sys.exc_info()
		self.write(repr(exc) + ' ' + traceback.tb_frame.f_code.co_filename + ' ERROR ON LINE ' + str(traceback.tb_lineno) + '\n' + repr(err) + '\n')
		del exc, err, traceback
	def OnUpdate(self, evt):
		#data=evt
		#self.graph.SetValue(evt.barNum, evt.value)
		#self.graph.Refresh(False)
		#print('Log:',evt.barNum, evt.value)
		#pprint (dir(evt))	
		#evt.Skip()
		#for line in str(evt.value).split(r'\n'):
		self.Freeze()
		wx.BeginBusyCursor()
		self.writeline(str(evt.value).replace(r'\n','\n'))
		#time.sleep(10)
		wx.EndBusyCursor()
		self.Thaw()
	def RunMP(self):
		print('MP')
		self.threads = []
		self.threads.append(NetcatReader(self, 0, 50))
		
		for t in self.threads:
			t.Start()
			
class app_log_ctrl(wx.TextCtrl):
	def __init__(self, *args, **kwargs):
		self.file_name = kwargs.pop('file_name', 'log.txt')
		self.main_frame = kwargs.pop('main_frame', None)
		self.add_to_file = kwargs.pop('add_to_file', False)
		if self.main_frame is None:
			self.main_frame = args[0]
		super(app_log_ctrl, self).__init__(*args, **kwargs)
	def __write__(self, content):
		self.WriteText(content)
	def show_control(self, ctrl_name = 'app_log_ctrl'):
		if self.main_frame is not None:
			if hasattr(self.main_frame,'aui_manager'):
				self.main_frame.show_aui_pane_info(ctrl_name)
		self.SetInsertionPointEnd()
		if self.add_to_file: self.flush()
	def write(self, content):
		self.show_control()
		self.__write__(content)
	def writelines(self, l):
		self.show_control()
		map(self.__write__, l)
	def flush(self):
		self.SaveFile(self.file_name)
	def print_error(self):
		exc, err, traceback = sys.exc_info()
		self.write(repr(exc) + ' ' + traceback.tb_frame.f_code.co_filename + ' ERROR ON LINE ' + str(traceback.tb_lineno) + '\n' + repr(err) + '\n')
		del exc, err, traceback

		
class shell_control(shell.Shell):
	HELP_TEXT = shell.HELP_TEXT
	def __init__(self, parent = None, ID = wx.ID_ANY):
		self.mf = parent
		str1 = _('Console')
		self.intro_text = '%s Python - %s (wxPython - %s)' % (str1, version.VERSION, wx.VERSION_STRING)
		shell.Shell.__init__(self, parent, ID, style = wx.CLIP_CHILDREN, introText = self.intro_text, locals = locals())
		#self.redirectStdin()
		#~ self.redirectStdout()
		#~ self.redirectStderr()
def import_module(filepath):
	class_inst = None
	#expected_class = 'MyClass'

	mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])
	assert os.path.isfile(filepath), 'File %s does not exists.' % filepath
	if file_ext.lower() == '.py':
		py_mod = imp.load_source(mod_name, filepath)

	elif file_ext.lower() == '.pyc':
		py_mod = imp.load_compiled(mod_name, filepath)
	return py_mod
home=os.path.dirname(os.path.abspath(__file__))
app_title='%s %s' % (__title__,__version__)
#main_file=os.path.join('include','main_logger_ui.py')
#logger_ui=import_module(main_file)
#import include.main_logger_ui.py as logger_ui

def rescale_bmp(bmp, scale):
	img = bmp.ConvertToImage()
	img.Rescale(scale[0], scale[1])
	return img.ConvertToBitmap()
def get_xpm(xmp_data):
	xpm="""/* XPM */
static char *burn48[] = {
/* columns rows colors chars-per-pixel */
"%s"
};
""" % (('",\n"').join([ x for x in xmp_data.split('\n')]).strip().strip(','))
		
	return xmp
def TestAll(dc,log):
	global pens,pencache,brushes,brushcache
	pens  = makeRandomPens(10, pencache)
	brushes = makeRandomBrushes(10, brushcache)
	TestLines(dc,log)
	TestRectanglesArray(dc,log)
	TestText(dc,log)
def TestText(dc,log):

	start = time.time()
	font = wx.Font(pointSize = 10, family = wx.DEFAULT,style = wx.NORMAL, weight = wx.NORMAL,faceName = 'Consolas')
	dc.SetFont(font)
	# NOTE: you need to set BackgroundMode for the background colors to be used.
	dc.SetBackgroundMode(wx.SOLID)
	foreground = wx.Colour('BLACK')
	background = wx.Colour('WHITE')
	text=['Populating Migration log. ', 'Extracting data from Oracle.', 'Uploading data to S3.']
	dc.DrawTextList(text, points, foreground, background)

	log.write("DrawTime: %s seconds with DrawTextList\n" % (time.time() - start))	
def TestLines(dc,log):
	start = time.time()

	dc.SetPen(wx.Pen("BLACK", 2))
	dc.SetBrush(wx.Brush("BLACK"))	
	dc.DrawLineList(lines)
	#dc.DrawLineList(lines, wx.Pen("RED", 2))
	#print(len(lines), len(pens))
	#dc.DrawLineList(lines, pens)

	log.write("DrawTime: %s seconds with DrawLineList\n" % (time.time() - start))	
def TestRectangles(dc,log):
	start = time.time()

	dc.SetPen( wx.Pen("BLACK",1) )
	dc.SetBrush( wx.Brush("RED") )

	dc.DrawRectangleList(rectangles)
	dc.DrawRectangleList(rectangles,pens)
	dc.DrawRectangleList(rectangles,pens[0],brushes)
	dc.DrawRectangleList(rectangles,pens,brushes[0])
	dc.DrawRectangleList(rectangles,None,brushes)
##    for i in range(10):
##        #dc.DrawRectangleList(rectangles,pens,brushes)
##        dc.DrawRectangleList(rectangles)

	log.write("DrawTime: %s seconds with DrawRectanglesList\n" % (time.time() - start))
def TestRectanglesArray(dc,log):
	global rectangles,pens,brushes
	try:
		import numpy
		Apoints = numpy.array(rectangles)

		start = time.time()
		dc.SetPen(wx.Pen("BLACK", 2))
		dc.SetBrush(wx.Brush("WHITE"))
		dc.DrawRectangleList(rectangles)
		#print(len(rectangles),len(pens), len(brushes))
		#print(pens)
		#pprint(dir(pens[0]))
		#e(0)
		dc.DrawRectangleList(Apoints)
		#dc.DrawRectangleList(rectangles,pens[:9])
		#dc.DrawRectangleList(rectangles,pens[0],brushes[:9])
		#print (brushes)
		#print ()
		#dc.DrawRectangleList(rectangles,pens[:9],[getBrush('WHITE') for x in range(9)])
		#dc.DrawRectangleList(rectangles,None,brushes)
##        for i in range(10):
##            #dc.DrawRectangleList(rectangles,pens,brushes)
##            dc.DrawRectangleList(rectangles)

		log.write("DrawTime: %s seconds with DrawRectangleList and Numpy Array\n" % (time.time() - start))
	except ImportError:
		log.write("Couldn't import numpy")
		raise	
		
class ListeningGauge(wx.Gauge):
	def __init__(self, *args, **kwargs):
		wx.Gauge.__init__(self, *args, **kwargs)
		pub.subscribe(self.start_listening, "progress_awake")
		pub.subscribe(self.stop_listening, "progress_sleep")

	def _update(self, this, total):
		try:
			self.SetRange(total)
			self.SetValue(this)
		except Exception as e:
			print (e)

	def start_listening(self, listen_to):
		rect = self.Parent.GetFieldRect(1)
		self.SetPosition((rect.x+2, rect.y+2))
		self.SetSize((rect.width-4, rect.height-4))
		self.Show()
		pub.subscribe(self._update, listen_to)

	def stop_listening(self, listen_to):
		pub.unsubscribe(self._update, listen_to)
		self.Hide()		
class SvgPanel(wx.Panel):
	use_alpha=True
	alpha_for_buffer=wx.ALPHA_OPAQUE
	def __init__(self, parent, drawFun, log, size=wx.Size(200,150)):
		wx.Panel.__init__(self, parent, -1)
		self.SetBackgroundColour(wx.WHITE)

		self.log = log
		#w = nb.GetClientSize().width
		#h = nb.GetClientSize().height
		self.SetSize(400,400)
		w, h = self.GetSize()
		if w < 600: w = 600
		if h < 400: h = 400
		self.w, self.h=(w,h)
		Init(self.w, self.h, 200)
		self.drawFun = drawFun
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.paint_counter=0


	def OnPaint(self, evt):
		global lines, rectangles, num, points
		#self.Freeze()
		#wx.BeginBusyCursor()
		dc = wx.PaintDC(self)
		#dc.Clear()
		points=makePoints(num)
		lines = makeLines(num, self.w, self.h)
		#pprint(lines)
		rectangles= makeRectangles(num, self.w, self.h)
		self.drawFun(dc,self.log)
		#print(0)
		self.paint_counter +=1
		print('paint_counter= ',self.paint_counter)
		#wx.EndBusyCursor()
		#self.Thaw()
	def _Paint(self):
		if 0:
			#self.Freeze()
			#wx.BeginBusyCursor()
			self.scale_x = 3.0 #self.svg_data['scale_x']
			self.scale_y = 3.0 #self.svg_data['scale_y']
			width, height = 300, 400
			#self.SetVirtualSize((width, height))
			if self.use_alpha:
				try:
					self.buffer = wx.Bitmap.FromRGBA(width, height, alpha = self.alpha_for_buffer)
				except:
					print_error()
					self.buffer = wx.Bitmap(width, height)
			else:
				self.buffer = wx.Bitmap(width, height)
			dc = wx.BufferedDC(None, self.buffer, wx.BUFFER_VIRTUAL_AREA)
			#dc.Clear()
			dc.SetDeviceOrigin(0, 0)
			#self.draw_to_dc(dc)
			self.drawFun(dc,self.log)
			#wx.EndBusyCursor()
			
			#self.Thaw()
		#self.Refresh()
h_len=75	
v_step=120
h_start=40

num=3
width = 210
height=70
v_start=height/2+30
def makeRandomLines(num, w, h):
	pnts = []

	for i in range(1,num):
		x1 = random.randint(0, w)
		y1 = random.randint(0, h)
		x2 = random.randint(0, w)
		y2 = random.randint(0, h)
		pnts.append( (x1,y1, x2,y2) )

	return pnts

def makePoints(num):
	pnts = []
	for i in range(num):
		x = h_start+h_len +10
		y = i*v_step+v_start -10
		pnts.append( (x,y) )

	return pnts
	
def makeLines(num, w, h):
	pnts = []

	vline=(h_start,v_start/2,h_start,num*v_step)
	pnts.append(vline)
	for i in range(num):
		x1 = h_start
		y1 = i*v_step+v_start
		x2 = h_start+h_len
		y2 = i*v_step+v_start
		pnts.append( (x1,y1, x2,y2) )

	return pnts
def makeRectangles(num, w, h):
	global v_start
	rects = []

	for i in range(num):
		w = width
		h = height
		x = h_start+h_len
		y = i*v_step-height/2 +v_start
		rects.append( (x, y, w, h) )
	return rects
def makeRandomPens(num, cache):
	pens = []

	for i in range(num):
		c = random.choice(colours)
		t = random.randint(1, 4)

		if not (c, t) in cache.keys():
			cache[(c, t)] = wx.Pen(c, t)

		pens.append( cache[(c, t)] )

	return pens		
def makeRandomBrushes(num, cache):
	brushes = []

	for i in range(num):
		c = random.choice(colours)

		if not c in cache.keys():
			cache[c] = wx.Brush(c)

		brushes.append( cache[c] )

	return brushes
def getBrush(c):
	global brushcache
	if not c in brushcache.keys():
		return wx.Brush(c)
	else:
		return brushcache[c]
pencache = {}
brushcache = {}
points = None
lines = None
rectangles = None
polygons = None
text = None
pens = None
brushes = None
colors1 = None
colors2 = None


def Init(w, h, n):
	global pencache
	global brushcache
	global points
	global lines
	global rectangles
	global polygons
	global text
	global pens
	global brushes
	global colors1
	global colors2

	# make some lists of random shapes
	if 0:
		points = makeRandomPoints(n, w, h)

		try:
			import Numeric
			Apoints = Numeric.array(points)
		except:
			pass

	#lines = makeRandomLines(n, w, h)
	#rectangles = makeRandomRectangles(n, w, h)
	#polygons = makeRandomPolygons(n, w, h)
	#text = makeRandomText(n)

	# make some random pens and brushes
	#pens  = makeRandomPens(n, pencache)
	#brushes = makeRandomBrushes(n, brushcache)
	# make some random color lists
	#colors1 = makeRandomColors(n)
	#colors2 = makeRandomColors(n)
	
def runTest(frame, nb, log):
	w = nb.GetClientSize().width
	h = nb.GetClientSize().height
	if w < 600: w = 600
	if h < 400: h = 400
	Init(w, h, 200)
	win = TestNB(nb, -1, log)
	return win

class NetcatChunkReader:
	def __init__(self, win, log_data, ts, fn):
		self.win = win
		self.ts = ts
		self.fn = fn
		self.timeout=0.1 # one hour
		self.chunksize=100*1024
		self.bytes_written=0
		self.c=self.s=None
		self.log_data=log_data
		self.total_bytes_read=0
		self.l=None
	def Start(self):
		self.keepGoing = self.running = True
		
		_thread.start_new_thread(self.Run, ({'host':socket.gethostname(), 'port':12349, 'outfile':self.fn},))

	def Stop(self):
		self.keepGoing = False

	def IsRunning(self):
		return self.running
	def Stop(self):
		self.s.close()
		self.f.close()
	def Start(self,*args,**kargs):
		host=	kargs.pop('host', socket.gethostname())
		port=	kargs.pop('port', 12349)
		#s = socket.socket()         # Create a socket object
		timed_out=True
		self.fid=0
		try:
			#if not self.s
			#print (1,flush=True, end='')
			self.s= socket.socket(socket.AF_INET, type=socket.SOCK_STREAM, proto=0)
			self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			self.s.setblocking(False)
			self.s.settimeout(self.timeout)
			#timed_out=False
			#print (2)
			self.log_file_name='%s_%d.log' % (self.fn, self.fid)
			self.f = open(self.log_file_name,'wb')
			self.f.seek(0)
			self.fid +=1
			#f.write('test')
			#f.close()
				
					
			
			#s.settimeout(10)
			#s.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
			#host = socket.gethostname() # Get local machine name
			#port = port                 # Reserve a port for your service.
			#print (port)
			self.s.bind((host, port))        # Bind to the port
			
			self.s.listen(5)                 # Now wait for client connection.
			self.i=0
		except socket.timeout as er1:
			
			err = er1.args[0]
			#pprint(er1.args)
			print ('EXCEPTION-----socket.timeout')
			timed_out=True
			self.Stop()
			#raise er1			
		except socket.error as er3:
			
			err = er3.args[0]
			#print (er3.args)			
			self.Stop()
			timed_out=False
			raise er3
		except Exception as ex:
			
			self.Stop()
			raise						
		self.running = False	
	def readChunk(self):
		try:
			if not self.c:			
				self.c, self.addr = self.s.accept()     # Establish connection with client.
				self.c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				self.c.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
				self.c.setblocking(False)
				self.c.settimeout(self.timeout)
				#c.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
				print ('Got connection from', self.addr)
				print ("Receiving...")								
				self.l = self.c.recv(self.chunksize)
				self.total_bytes_read +=len(self.l)
				print(22222222222222222222222222222,self.l)
				self.log_data.append((self.fn,self.total_bytes_read, self.l))
			if self.l:
				#evt = UpdateLogEvent(barNum = 1, value = (self.log_file_name,len(self.l), self.bytes_written))
				#wx.PostEvent(self.win, evt)
				self.bytes_written +=len(self.l)
				#self.f.write(self.l)
				self.l = self.c.recv(self.chunksize)
				self.total_bytes_read +=len(self.l)
				print(11111,self.l)
				self.log_data.append((self.fn,self.total_bytes_read, self.l))
				#print (self.i, len(self.l))
				self.i +=1
				#self.l
			if not self.l: 
				self.c.close()
				self.c=None
				print ("Done Receiving %s" %  self.i)
				self.s.listen(5) 

		except socket.timeout as er1:
			
			err = er1.args[0]
			#pprint(er1.args)
			print ('EXCEPTION-----socket.timeout')
			timed_out=True
			#self.Stop()
			#raise er1			
		except socket.error as er3:
			
			err = er3.args[0]
			#print (er3.args)			
			self.Stop()
			timed_out=False
			raise er3
		except Exception as ex:
			
			self.Stop()
			raise
from collections import OrderedDict			
class GraphWindow(wx.Window):
	def __init__(self, parent, labels, group_name):
		wx.Window.__init__(self, parent, -1)

		self.values = OrderedDict()
		for label in labels:
			self.values[label]=[1,'0%', wx.BLUE]
		self.group_name=group_name
		self.colors={}
	def SetLabels(self, labels):
		self.values[labels[0]]=[1, '0/0', wx.RED]
		for label in labels[1:]:			
			self.values[label]=1
		
		font = wx.Font(pointSize = 10, family = wx.DEFAULT,style = wx.NORMAL, weight = wx.NORMAL,faceName = 'Consolas') 
		#wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
		self.SetFont(font)

		self.all_colors = [ wx.RED, wx.GREEN, wx.BLUE, wx.CYAN,
						"Yellow", "Navy" ]
		
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_PAINT, self.OnPaint)			
			
	def SetValue(self, key, value):
		if key in self.values.keys():
			#assert index < len(self.values)
			#cur = self.values[index]
			self.values[key] = value
		else:
			print ('Key % s is missing' % key)

	def setColor(self,key,hasErrors):
		if hasErrors:
			self.colors[key]=wx.RED
		else:
			self.colors[key]=wx.GREEN
			
	def SetFont(self, font):
		wx.Window.SetFont(self, font)
		wmax = hmax = 0
		for label, val in self.values.items():
			w,h = self.GetTextExtent(label)
			if w > wmax: wmax = w
			if h > hmax: hmax = h
		self.linePos = wmax + 10
		self.barHeight = hmax


	def GetBestHeight(self):
		return 2 * (self.barHeight + 1) * len(self.values)


	def Draw(self, dc, size):
		print('draw')
		dc.SetFont(self.GetFont())
		dc.SetTextForeground(wx.BLUE)
		dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
		dc.Clear()
		dc.SetPen(wx.Pen(wx.BLACK, 3, wx.PENSTYLE_SOLID))
		#dc.DrawLine(self.linePos, 0, self.linePos, size.height-10)

		bh = ypos = self.barHeight
		#pprint(self.values)
		x=0
		if 1:
			label=self.group_name
			val, msg, color = self.values[self.group_name]
			#label, val = self.values[x]
			dc.DrawText(label, 5, ypos)

			if val:
				#color = self.colors[ x % len(self.colors) ]
				dc.SetPen(wx.Pen(color))
				dc.SetBrush(wx.Brush( color))
				dc.DrawRectangle(self.linePos+3, ypos, val, bh)
				dc.DrawText(msg, self.linePos+6+val, ypos)
			ypos = ypos + 2*bh
			#if ypos > size[1]-10:
			#	break
			x +=1

		for label, val in self.values.items():
			#label, val = self.values[x]
			#val= self.values[label]
			if label  not in [self.group_name]:
				dc.DrawText(label, 45, ypos)
				(pos,msg,color) = val
				#self.colors
				if pos:
					#color = self.colors[ x % len(self.colors) ]
					dc.SetPen(wx.Pen(color))
					dc.SetBrush(wx.Brush( color))
					dc.DrawRectangle(self.linePos+3, ypos+17, pos, bh)

				ypos = ypos + 2*bh
				if ypos > size[1]-10:
					break
				x +=1			

	def OnPaint(self, evt):
		#print ('OnPaint')
		#if self.values:
		if 1:
			dc = wx.BufferedPaintDC(self)
			self.Draw(dc, self.GetSize())


	def OnEraseBackground(self, evt):
		pass
class CalcBarThread:
	def __init__(self, win, barNum, val):
		self.win = win
		self.barNum = barNum
		self.val = val

	def Start(self):
		self.keepGoing = self.running = True
		_thread.start_new_thread(self.Run, ())

	def Stop(self):
		self.keepGoing = False

	def IsRunning(self):
		return self.running

	def Run(self):
		while self.keepGoing:
			# We communicate with the UI by sending events to it. There can be
			# no manipulation of UI objects from the worker thread.
			evt = UpdateBarEvent(barNum = self.barNum, value = int(self.val))
			wx.PostEvent(self.win, evt)

			sleeptime = (random.random() * 2) + 0.5
			time.sleep(sleeptime/4)

			sleeptime = sleeptime * 5
			if int(random.random() * 2):
				self.val = self.val + sleeptime
			else:
				self.val = self.val - sleeptime

			if self.val < 0: self.val = 0
			if self.val > 300: self.val = 300

		self.running = False
		
class LogGraphPanel(wx.Panel):
	def __init__(self, parent,group_name):
		wx.Panel.__init__(self, parent, -1)
		#self.log = log

		#self.CenterOnParent()

		panel = wx.Panel(self, -1)
		panel.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
		#wx.StaticText(panel, -1,"Data backup", (5,5))
		panel.Fit()
		self.group_name=group_name
		self.graph = GraphWindow(self, [],self.group_name)
		
		

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(panel, 0, wx.EXPAND)
		sizer.Add(self.graph, 1, wx.EXPAND)

		self.SetSizer(sizer)
		self.SetAutoLayout(True)
		sizer.Fit(self)

		self.Bind(EVT_UPDATE_BARGRAPH, self.OnUpdate)
		
		self.Start(3)
		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
		

	def Start(self, num_of_threads):
		labels=[self.group_name]	
		self.graph.SetLabels(labels)
		self.graph.SetMinSize((450, self.graph.GetBestHeight()))
		if 0:
			self.threads = []
			for i in range(num_of_threads):
				self.threads.append(CalcBarThread(self, i, 200))
			for t in self.threads:
				t.Start()	
	def OnUpdate(self, evt):
		self.graph.SetValue(evt.barNum, evt.value)
		self.graph.Refresh(False)


	def OnCloseWindow(self, evt):
		busy = wx.BusyInfo("One moment please, waiting for threads to die...")
		wx.Yield()

		for t in self.threads:
			t.Stop()

		running = 1

		while running:
			running = 0

			for t in self.threads:
				running = running + t.IsRunning()

			time.sleep(0.1)

		self.Destroy()

		
class main_frame(wx.Frame):
	def __init__(self, *args, **kwargs):
		self.app = kwargs.pop('app', None)
		#self.open_file_name = kwargs.pop('open_file_name', '')
		wx.Frame.__init__(self, *args, **kwargs)
		self.default_title = self.GetTitle()
		#~ self.SetIcon(wx.IconFromBitmap(wx.BitmapFromXPMData(xpm_main_icon.split('\n'))))
		#self.SetIcon(wx.IconFromBitmap(svg_to_bitmap(logo, (32, 32), use_cairo = False)))
		self.log_data=[]
		#Logging Text Control
		ts=time.strftime('%Y%m%d_%a_%H%M%S')
		fn=os.path.join(outdir,'netcat_%s_incoming' % ts) 
		self.nc=NetcatChunkReader(self,self.log_data,ts,fn)
		self.nc.Start({'host':socket.gethostname(), 'port':12349})
		if 1:
			self.app_log_ctrl = app_log_ctrl(self, style = wx.TE_MULTILINE)
			

		if 1:
			self.log = wx.LogTextCtrl(self.app_log_ctrl)
			self.log.SetLogLevel(wx.LOG_Error)
			wx.Log.SetActiveTarget(self.log)
		#print (23)
		if 1:
			self.print_data = wx.PrintData()
			self.page_setup_dialog_data = wx.PageSetupDialogData()

			id_about = wx.ID_ABOUT
			id_refresh = wx.NewId()
			id_run_coro = wx.NewId()
			
			id_exit = wx.ID_EXIT
			id_help = wx.ID_HELP
			id_clear_shell = wx.NewId()
			id_show_toolbar = wx.NewId()
			id_show_shell = wx.NewId()
			id_show_log_ctrl = wx.NewId()
			id_show_full_screen = wx.NewId()
			id_save_default_perspective = wx.NewId()
			id_convert_to_raster_and_save = wx.NewId()

			img_size = (24, 24)
			bmp_open = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, img_size)
			bmp_saveas = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_OTHER, img_size)
			bmp_print = wx.ArtProvider.GetBitmap(wx.ART_PRINT, wx.ART_OTHER, img_size)
			bmp_preview = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, img_size)
			bmp_page_setup = wx.ArtProvider.GetBitmap(wx.ART_HELP_PAGE, wx.ART_OTHER, img_size)
			bmp_quit = wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_OTHER, img_size)
			bmp_about = wx.ArtProvider.GetBitmap(wx.ART_HELP_SETTINGS, wx.ART_OTHER, img_size)
			bmp_help = wx.ArtProvider.GetBitmap(wx.ART_HELP_BOOK, wx.ART_OTHER, img_size)
			bmp_zoom_100 = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_OTHER, img_size)
			bmp_clear_shell = wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_OTHER, img_size) #wx.Bitmap([xpm_clear1.split(r'\n')],type=wx.BITMAP_TYPE_XPM)
			#wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, img_size) 
			bmp_show_log_ctrl =wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, img_size)  #wx.Bitmap(log_xpm,type=wx.BITMAP_TYPE_XPM)
			bmp_show_toolbar = wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK, wx.ART_OTHER, img_size)

			bmp_show_shell = wx.Bitmap('xpm/shell.xpm',type=wx.BITMAP_TYPE_XPM)
			bmp_save_default_perspective = wx.ArtProvider.GetBitmap(wx.ART_HELP_SIDE_PANEL, wx.ART_OTHER, img_size)
			#bmp=wx.Bitmap(xpm_shell,type=wx.BITMAP_TYPE_XPM) # xpm_fullscreen
			#bmp_show_full_screen = bmp #rescale_bmp(bmp, img_size)
			bmp_refresh = wx.Bitmap('xpm/squares.xpm',type=wx.BITMAP_TYPE_XPM)
			bmp_coro = wx.Bitmap('xpm/burn48.xpm',type=wx.BITMAP_TYPE_XPM)
			bmp_show_full_screen = wx.Bitmap('xpm/xpm_fullscreen.xpm',type=wx.BITMAP_TYPE_XPM) #wx.ArtProvider.GetBitmap(wx.ART_REPORT_VIEW, wx.ART_OTHER, img_size)
			bmp_convert_to_raster_and_save = wx.ArtProvider.GetBitmap(wx.ART_NEW_DIR, wx.ART_OTHER, img_size)

			self.menubar = wx.MenuBar()
			self.SetMenuBar(self.menubar)
			if 0:
				tmp_menu = wx.Menu()
				menu_item = wx.MenuItem(tmp_menu, wx.ID_OPEN, _('Open'), _('Open'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_open)
				tmp_menu.Append(menu_item)
				menu_item = wx.MenuItem(tmp_menu, wx.ID_SAVEAS, _('Save As...'), _('Save As...'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_saveas)
				tmp_menu.Append(menu_item)
				menu_item = wx.MenuItem(tmp_menu, id_convert_to_raster_and_save, _('Save bitmap'), _('Save to file as raster graphics.'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_convert_to_raster_and_save)
				tmp_menu.Append(menu_item)
				menu_item = wx.MenuItem(tmp_menu, wx.ID_PRINT, _('Print'), _('Print'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_print)
				tmp_menu.Append(menu_item)
				menu_item = wx.MenuItem(tmp_menu, wx.ID_PREVIEW, _('Preview'), _('Preview'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_preview)
				tmp_menu.Append(menu_item)
				menu_item = wx.MenuItem(tmp_menu, wx.ID_PAGE_SETUP, _('Page Setup'), _('Page Setup'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_page_setup)
				tmp_menu.Append(menu_item)
				menu_item = wx.MenuItem(tmp_menu, id_clear_shell, _('&clear'), _('clear shell'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_clear_shell)
				tmp_menu.Append(menu_item)
				menu_item = wx.MenuItem(tmp_menu, id_exit, _('&Quit'), _('Exit from this application'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_quit)
				tmp_menu.Append(menu_item)
				self.menubar.Append(tmp_menu, _('File'))

				tmp_menu = wx.Menu()
				menu_item = wx.MenuItem(tmp_menu, wx.ID_ZOOM_100, _('Zoom 100'), _('Zoom to original size'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_zoom_100)
				tmp_menu.Append(menu_item)
				self.menubar.Append(tmp_menu, _('Zoom'))

				tmp_menu = wx.Menu()
				menu_item = wx.MenuItem(tmp_menu, id_show_toolbar, _('Show &toolbar'), _('Show main toolbar'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_show_toolbar)
				tmp_menu.Append(menu_item)
				menu_item = wx.MenuItem(tmp_menu, id_show_shell, _('Show &shell'), _('Show shell'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_show_shell)
				tmp_menu.Append(menu_item)
				menu_item = wx.MenuItem(tmp_menu, id_show_log_ctrl, _('Show &log'), _('Show log'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_show_log_ctrl)
				tmp_menu.Append(menu_item)
				menu_item = wx.MenuItem(tmp_menu, id_show_full_screen, _('Show full screen'), _('Show frame into full screen mode'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_show_full_screen)
				tmp_menu.Append(menu_item)
				menu_item = wx.MenuItem(tmp_menu, id_save_default_perspective, _('Save default perspective'), _('Save default perspective'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_save_default_perspective)
				tmp_menu.Append(menu_item)
				self.menubar.Append(tmp_menu, _('Show'))
				
				tmp_menu = wx.Menu()
				menu_item = wx.MenuItem(tmp_menu, id_about, _('&About'), _('About authors'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_about)
				tmp_menu.Append(menu_item)
				menu_item = wx.MenuItem(tmp_menu, id_help, _('&Help'), _('Help for this application'), wx.ITEM_NORMAL)
				menu_item.SetBitmap(bmp_help)
				tmp_menu.Append(menu_item)
				self.menubar.Append(tmp_menu, _('Help'))
			
			if 0:
				self.main_toolbar = AuiToolBar(self, style = AUI_TB_DEFAULT_STYLE|AUI_TB_VERTICAL|AUI_TB_OVERFLOW)
				self.main_toolbar.AddTool(wx.ID_OPEN, _('Open'), bmp_open, wx.NullBitmap, wx.ITEM_NORMAL, _('Open'), _('Open'), None)
				self.main_toolbar.AddTool(wx.ID_SAVEAS, _('Save As...'), bmp_saveas, wx.NullBitmap, wx.ITEM_NORMAL, _('Save As...'), _('Save As...'), None)
				self.main_toolbar.AddTool(id_convert_to_raster_and_save, _('Save bitmap'), bmp_convert_to_raster_and_save, wx.NullBitmap, wx.ITEM_NORMAL, _('Save bitmap'), _('Save to file as raster graphics.'), None)
				#self.main_toolbar.AddTool(wx.ID_PRINT, _('Print'), bmp_print, wx.NullBitmap, wx.ITEM_NORMAL, _('Print'), _('Print'), None)
				#self.main_toolbar.AddTool(wx.ID_PREVIEW, _('Preview'), bmp_preview, wx.NullBitmap, wx.ITEM_NORMAL, _('Preview'), _('Preview'), None)
				#self.main_toolbar.AddTool(wx.ID_PAGE_SETUP, _('Page Setup'), bmp_page_setup, wx.NullBitmap, wx.ITEM_NORMAL, _('Page Setup'), _('Page Setup'), None)
				self.main_toolbar.AddTool(wx.ID_ZOOM_100, _('Zoom 100'), bmp_zoom_100, wx.NullBitmap, wx.ITEM_NORMAL, _('Zoom 100 percents'), _('Zoom to original size'), None)
				self.main_toolbar.AddTool(id_show_full_screen, _('Show full screen'), bmp_show_full_screen, wx.NullBitmap, wx.ITEM_NORMAL, _('Show full screen'), _('Show frame into full screen mode'), None)
				#self.main_toolbar.AddTool(id_about, _('Authors'), bmp_about, wx.NullBitmap, wx.ITEM_NORMAL, _('Version application, author'), _('Version application, author'), None)
				
				self.main_toolbar.AddTool(wx.ID_CLOSE, _('Exit'), bmp_quit, wx.NullBitmap, wx.ITEM_NORMAL, _('Exit from application'), _('Exit from application'), None)
				#self.main_toolbar.AddTool(40, "Exit", bmp_quit, wx.NullBitmap, wx.ITEM_NORMAL, "Exit", "Exit", None)
				#self.Bind(wx.EVT_TOOL, self.OnToolClick, id=40)
				
				self.main_toolbar.AddTool(id_refresh, _('Refresh'), bmp_refresh, wx.NullBitmap, wx.ITEM_NORMAL, _('Refresh canvas'), _('Refresh canvas'), None)
				self.main_toolbar.AddTool(id_run_coro, _('MP'), bmp_coro, wx.NullBitmap, wx.ITEM_NORMAL, _('Run MP'), _('Run MP'), None)
				self.main_toolbar.Realize()
			self.group_name='Backup progress'
			self.shell = shell_control(self)
			#self.svg_panel = SvgPanel(self,TestAll, self.app_log_ctrl ) #svg_panel(self)
			self.svg_panel= LogGraphPanel(self, self.group_name)

			self.pane_captions = {
								'main_toolbar':('main_toolbar', _('main toolbar')),
								'svg_panel':('svg_panel', _('svg panel')),
								'app_log_ctrl':('log', _('log')),
								'shell':('shell', _('shell'))
								}
			
			self.aui_manager = AuiManager()
			self.aui_manager.SetManagedWindow(self)
		if 0:
			self.remote_log = log_ctrl(self, style = wx.TE_MULTILINE, size=wx.Size(500,500))
		if 1:
			self.remote_log = wx.Panel(self)
			nb = wx.Notebook(self.remote_log)
			self.messages_tab = MessagesTab(nb, self, self.group_name)
			# self.messages_tab = MessagesTab(panel)
			# add tab pages to notebook
			nb.AddPage(self.messages_tab, 'Backup log')
			self._nb = nb

			sizer = wx.BoxSizer()
			sizer.Add(nb, 1, wx.EXPAND)
			# sizer.Add(self.messages_tab, 1, wx.EXPAND)
			minSize=self.ClientToWindowSize(sizer.GetMinSize())     # get this as Info tab's min size is too small
			self.remote_log.SetSizerAndFit(sizer)
			self.SetInitialSize(minSize)
		
		if 1:
			#self.aui_manager.AddPane(self.main_toolbar, AuiPaneInfo().ToolbarPane().Name('main_toolbar').Left().Layer(0).Position(0))
			self.aui_manager.AddPane(self.remote_log, AuiPaneInfo().Name('remote_log').CaptionVisible(False).CloseButton(False).Left().Layer(1).Position(0).MinSize(wx.Size(1100, 1000)).BestSize(wx.Size(450, 1000)))
			self.aui_manager.AddPane(self.svg_panel, AuiPaneInfo().Name('svg_panel').CenterPane().Layer(1).Position(0).BestSize(wx.Size(500, 1000)))
			
			self.aui_manager.AddPane(self.app_log_ctrl, AuiPaneInfo().Name('app_log_ctrl').CenterPane().Layer(1).Position(1).BestSize(wx.Size(600,600)))
			self.aui_manager.AddPane(self.shell, AuiPaneInfo().Name('shell').Bottom().Layer(1).MaximizeButton(True).Hide())

			#if self.app.settings.ReadBool('GUI/load_default_perspective_on_start', True):
			#	self.aui_manager.LoadPerspective(self.app.settings.Read('GUI/perspective', ''))
			#if self.log_ctrl.GetValue() != '':
			#	self.aui_manager.GetPane('log_ctrl').Show()
			#print(self.svg_panel.paint_counter)
			self.aui_manager.GetPane('main_toolbar').dock_proportion = 10
			self.aui_manager.GetPane('remote_log').dock_proportion = 150
			
			self.aui_manager.GetPane('svg_panel').dock_proportion = 25
			self.aui_manager.GetPane('app_log_ctrl').dock_proportion = 15
			self.aui_manager.Update()
			#print(self.svg_panel.paint_counter)

			#self.method_set_translation_pane_captions()

			#self.sb = self.CreateStatusBar(2)
			status = self.statusbar = self.CreateStatusBar() # A StatusBar in the bottom of the window
			status.SetFieldsCount(3)
			status.SetStatusWidths([-2,200,-1])

			self.progress_bar = ListeningGauge(self.statusbar, style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
			rect = self.statusbar.GetFieldRect(1)
			self.progress_bar.SetPosition((rect.x+2, rect.y+2))
			self.progress_bar.SetSize((rect.width-4, rect.height-4))
			self.progress_bar.Hide()
		
		if 1:

			self.Bind(wx.EVT_CLOSE, self.OnClose)
			
			self.Bind(wx.EVT_MENU, self.event_exit, id=wx.ID_CLOSE)
			#self.Bind(id_show_shell, self.event_show_shell)
			#wx.EVT_MENU(self, id_show_shell, self.event_show_shell)
			self.Bind(wx.EVT_MENU, self.event_show_shell, id=id_show_shell)
			self.Bind(wx.EVT_MENU, self.event_show_app_log_ctrl, id=id_show_log_ctrl)
			
			self.Bind(wx.EVT_MENU, self.OnRefresh, id=id_refresh)
			self.Bind(wx.EVT_MENU, self.OnRunMP, id=id_run_coro)
		if 1:
			if self.app.settings.ReadBool('GUI/load_default_state_on_start', True):
				self.method_load_default_state()

			self.default_open_path = self.app.settings.Read('GUI/default_open_path', os.getcwd())

		self.InitialiseTimers()
	def InitialiseTimers(self):
		# tab updates and test comparison timer
		self.displayTimer=wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.OnUpdateRemoteLogList, self.displayTimer)
		self.displayTimer.Start(UPDATE_MS)
		self.readTimer=wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.OnReadData, self.readTimer)
		self.readTimer.Start(UPDATE_MS)
		
		# self.Bind(wx.EVT_IDLE, self.OnRefresh)
	def OnUpdateRemoteLogList(self, event):
		self.messages_tab.UpdateRemoteLogList()
	def OnReadData(self, event):
		print('OnReadData	')
		self.nc.readChunk()
		print (len(self.log_data))
	def OnUpdate(self, evt):
		#data=evt
		#self.graph.SetValue(evt.barNum, evt.value)
		#self.graph.Refresh(False)
		#print(evt.barNum, evt.value)
		#pprint (dir(evt))
		
		pass
		#evt.Skip()
		
	def OnRunMP(self, evt):
		print('MP')
		self.messages_tab.RunMP()
		#self.remote_log.RunMP()
		
		if 0:
			self.threads = []
			self.threads.append(CalcBarThread(self, 0, 50))
			
			for t in self.threads:
				t.Start()

		#self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
		
		if 0:
			from multiprocessing import Process, Lock
			Process(target=test_MP, args=(10,)).start()
		
		if 0:
			from multiprocessing import Pool, TimeoutError	
			pool = Pool(processes=1)
			res = pool.apply_async(test_MP, (10,))
		if 0:
			try:
				print (res.get(timeout=1))
			except TimeoutError:
				print ("We lacked patience and got a multiprocessing.TimeoutError")
			print (res)
		if 0:
			pool_size=1

			queries=[]

			
			queries.append(['test'])
				
			
			m= multiprocessing.Manager()

			inputs = list([[i,t] for i,t in enumerate(queries)])

			pool = m.Pool(processes=pool_size,
										initializer=start_process,
										)
			#pprint(dir(pool))
			#e(0)		
			pool_outputs = pool.map_async(test_MP, inputs)
			pool.close() # no more tasks
			#pool.join()  # wrap up current tasks

			#print ('Pool    :', pool_outputs)
			#e(0)
			print ('#'*60)
			print ('#'*60)
			pprint(pool_outputs)
			print ('#'*60)
			print ('#'*60)
		
		
	def OnRefresh(self, event):
		self.Freeze()
		wx.BeginBusyCursor()
		self.svg_panel.Refresh()
		wx.EndBusyCursor()
		self.Thaw()
	def OnToolRClick(self, event):
		print("tool %s right-clicked\n" % event.GetId())

	def OnCombo(self, event):
		print("combobox item selected: %s\n" % event.GetString())
	def OnToolEnter1(self, event):
		print('OnToolEnter: %s, %s\n' % (event.GetId(), event.GetInt()))

		if self.timer is None:
			self.timer = wx.Timer(self)

		if self.timer.IsRunning():
			self.timer.Stop()

		self.timer.Start(2000)
		event.Skip()

	def OnClearSB1(self, event):  # called for the timer event handler
		self.SetStatusText("")
		self.timer.Stop()
		self.timer = None		
	def OnToolClick1(self, event):
		print("tool %s clicked\n" % event.GetId())
		#self.main_toolbar.Destroy()		
		self.aui_manager.UnInit()
		self.Destroy()
		event.Skip()
	def _Exit(self):
		if self.app.settings.ReadBool('GUI/save_default_state_on_exit', True):
			self.method_save_default_state()
		if self.app.settings.ReadBool('GUI/save_default_perspective_on_exit', True):
			self.method_save_default_perspective()
		#self.main_toolbar.Destroy()		
		self.aui_manager.UnInit()
		
		self.Destroy()	
	def OnClose(self, event):
		#self.ticker.Stop()
		self._Exit()
		event.Skip()
	def event_exit(self, event):
		#self.main_toolbar.Destroy()		
		self.aui_manager.UnInit()
		self.Destroy()	
		#event.Skip()		
	def event_show_shell(self, event):
		
		self.show_hide_aui_pane_info('shell')
		event.Skip()	
	def event_show_app_log_ctrl(self, event):
		self.show_hide_aui_pane_info('app_log_ctrl')		
	def show_hide_aui_pane_info(self, name):
		if self.aui_manager.GetPane(name).IsShown():
			self.aui_manager.GetPane(name).Hide()
		else:
			self.aui_manager.GetPane(name).Show()
		self.aui_manager.Update()
	def show_aui_pane_info(self, name):
		if not self.aui_manager.GetPane(name).IsShown():
			self.aui_manager.GetPane(name).Show()
			self.aui_manager.Update()		
	def event_show_full_screen(self, event):
		self.ShowFullScreen(not self.IsFullScreen(),functools.reduce(or_,[getattr(wx,val) for val in FlagList],0)) #  self.app.settings.ReadInt('GUI/fullscreen_style', default_fullscreen_style))	
	def method_save_default_perspective(self):
		self.method_set_default_pane_captions()
		current_perspective = self.aui_manager.SavePerspective()
		self.method_set_translation_pane_captions()
		if self.app.settings.Read('GUI/perspective', '') != current_perspective:
			self.app.settings.Write('GUI/perspective', current_perspective)
			self.app.settings.Flush()
	def method_set_default_pane_captions(self):
		for name, caption in self.pane_captions.items():
			self.aui_manager.GetPane(name).Caption(caption[0])

	def method_set_translation_pane_captions(self):
		for name, caption in self.pane_captions.items():
			self.aui_manager.GetPane(name).Caption(caption[1])			
	def method_save_default_state(self):
		flag_flush = False
		position = self.GetPosition()
		if position != eval(self.app.settings.Read('GUI/position', '()')):
			self.app.settings.Write('GUI/position', repr(position))
			flag_flush = True
		size = self.GetSize()
		if size != eval(self.app.settings.Read('GUI/size', '()')):
			self.app.settings.Write('GUI/size', repr(size))
			flag_flush = True
		font = self.GetFont().GetNativeFontInfo().ToString()
		if font != self.app.settings.Read('GUI/font', ''):
			self.app.settings.Write('GUI/font', font)
			flag_flush = True
		is_maximized = self.IsMaximized()
		if is_maximized != self.app.settings.ReadBool('GUI/maximized', False):
			self.app.settings.WriteBool('GUI/maximized', is_maximized)
			flag_flush = True
		is_iconized = self.IsIconized()
		if is_iconized != self.app.settings.ReadBool('GUI/iconized', False):
			self.app.settings.WriteBool('GUI/iconized', is_iconized)
			flag_flush = True
		is_fullscreen = self.IsFullScreen()
		if is_fullscreen != self.app.settings.ReadBool('GUI/fullscreen', False):
			self.app.settings.WriteBool('GUI/fullscreen', is_fullscreen)
			flag_flush = True
		if flag_flush:
			self.app.settings.Flush()
	def method_load_default_state(self):
		#frame_font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
		#frame_font.SetNativeFontInfoFromString(self.app.settings.Read('GUI/font', ''))
		#self.SetFont(frame_font)
		self.SetSize(eval(self.app.settings.Read('GUI/size', '(100,100)')))
		self.SetPosition(eval(self.app.settings.Read('GUI/position', '(100,100)')))
		centre_on_screen = eval(self.app.settings.Read('GUI/centre_on_screen', repr((False, wx.BOTH))))
		if centre_on_screen[0]:
			self.CentreOnScreen(centre_on_screen[1])
		self.Maximize(self.app.settings.ReadBool('GUI/maximized', False))
		self.Iconize(self.app.settings.ReadBool('GUI/iconized', False))
		self.ShowFullScreen(self.app.settings.ReadBool('GUI/fullscreen', False), self.app.settings.ReadInt('GUI/fullscreen_style', default_fullscreen_style))

def start_process():
	print('Starting ' + multiprocessing.current_process().name)		
def test_MP(data):
	print ('testMP')
	i=0
	if 1:
		pub.sendMessage('progress_awake', listen_to = 'short_update')
		if 1:
			#wx.BeginBusyCursor()
			for x in range(6):
				pub.sendMessage('short_update', this = x+1, total = 6)
				time.sleep(0.5)
			#wx.EndBusyCursor()
			pub.sendMessage('progress_sleep', listen_to = 'short_update')
			
	while True:
		print (i)
		time.sleep(1)
		i +=1
	return 99
	
def open_settings(filename):
	conf = wx.FileConfig(localFilename = filename)
	def create_entry(entry_name, entry_value):
		if not conf.HasEntry(entry_name):
			if isinstance(entry_value, (str, bytes)):
				conf.Write(entry_name, entry_value)
			elif isinstance(entry_value, int):
				conf.WriteInt(entry_name, entry_value)
			elif isinstance(entry_value, bool):
				conf.WriteBool(entry_name, entry_value)
			else:
				conf.Write(entry_name, repr(entry_value))
			return True
		else:
			return False
	flag_flush = False
	if create_entry('Language/Catalog', getdefaultlocale()[0]):
		flag_flush = True
	if create_entry('GUI/load_default_perspective_on_start', True):
		flag_flush = True
	if create_entry('GUI/save_default_perspective_on_exit', True):
		flag_flush = True
	if create_entry('GUI/perspective', ''):
		flag_flush = True
	if create_entry('GUI/load_default_state_on_start', True):
		flag_flush = True
	if create_entry('GUI/save_default_state_on_exit', True):
		flag_flush = True
	if create_entry('GUI/fullscreen_style', default_fullscreen_style):
		flag_flush = True
	if create_entry('GUI/centre_on_screen', repr((False, wx.BOTH))):
		flag_flush = True
	if create_entry('GUI/default_open_path', '.'):
		flag_flush = True
	if flag_flush:
		conf.Flush()
	return conf	
class MyApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
	app_version = __version__
	app_path = os.getcwd()
	app_name = os.path.basename(sys.argv[0].split('.')[0])
	help_file = app_name + '.htb'
	settings_name = os.path.join(app_path,'cfg', app_name + '.cfg')
	app_config_loc=os.path.join(home,'config','app_config.py')
	def OnInit(self):

		#ac=import_module(app_config_loc)

		self.Init()
		if 1:
			self.settings = open_settings(self.settings_name)
			name_user = wx.GetUserId()
			name_instance = self.app_name + '::'
			self.instance_checker = wx.SingleInstanceChecker(name_instance + name_user)
			if self.instance_checker.IsAnotherRunning():
				wx.MessageBox(_('Software is already running.'), _('Warning'))
				return False
		self.frame = main_frame(None, app = self,  title = 'Name/version', size=(600,1200))
		
		self.SetTopWindow(self.frame)
		self.frame.Show()
		return True
def start_coro():
	coros=[]
	coros.append(netcat_read_messages(host=socket.gethostname(), port=12349))
	coros.append(start_ui())


def netcat_read_messages(**kargs):
	host, port = kargs['host'], kargs['port']
	#s = socket.socket()         # Create a socket object
	timed_out=True
	
	while timed_out:
		try:
	
			print (1,flush=True, end='')
			s= socket.socket(socket.AF_INET, type=socket.SOCK_STREAM, proto=0)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			s.setblocking(False)
			s.settimeout(0.1)
			#timed_out=False
			print (2)
			f = open(r'C:\Temp\example_lines23.txt','w')
			f.write('test')
			f.close()
				
					
			
			#s.settimeout(10)
			#s.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
			#host = socket.gethostname() # Get local machine name
			#port = port                 # Reserve a port for your service.
			print (port)
			s.bind((host, port))        # Bind to the port
			
			s.listen(5)                 # Now wait for client connection.
			i=0
			while True:
				
				c, addr = s.accept()     # Establish connection with client.
				c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				c.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
				c.setblocking(False)
				c.settimeout(0.1)
				#c.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
				print ('Got connection from', addr)
				print ("Receiving...")
				#netcat.write('netcat from file writer')
				
				l = c.recv(100*1024)
				print (l)
				#f.write(l)
				#f.close()
				f = open(r'C:\Temp\example_lines1.txt','wb')
				f.write('test')
				f.close()
				while (l):
					#await asyncio.sleep(0.1)
					#print "*",
					#if i%10000==0:
					#		netcat.write('Chunk# %d' % i)
					#f = open('/tmp/torecv_%d.png' % i,'wb')
					f.write(l)
					#f.close()
					l = c.recv(100*1024)
					print (l,flush=True, end='')
					i +=1
					if 0 and i>20:
						f.close()
						e(0)
				

				#f.close()

				#c.send('Thank you for connecting')
				c.close()
				#s.shutdown(socket.SHUT_WR)
				#s.close()
				print ("Done Receiving %s" %  i)
				#del netcat
				#e(0)
			s.close()
		except socket.timeout as er1:
			
			err = er1.args[0]
			#pprint(er1.args)
			print ('EXCEPTION-----socket.timeout')
			timed_out=True
			f.close()
			s.close()
			#raise er1			
		except socket.error as er3:
			
			err = er3.args[0]
			print (er3.args)			
			f.close()
			s.close()
			timed_out=False
			raise er3
		except err:
			
			f.close()
			s.close()
			raise	
			
def start_gui(data):
	app = MyApp(redirect=False) #=True,filename="applogfile.txt")
	app.frame.Layout()
	try:
		app.MainLoop()
	except Exception as e:
		print('#'*80)
		traceback.print_exc();
		print('#'*80)
		raise
		
if __name__ == '__main__':
	try:
		_count = int(open("counter").read())
	except IOError:
		_count = 0
	#for signame in ('SIGINT', 'SIGTERM'):
	#	loop.add_signal_handler(getattr(signal, signame), functools.partial(ask_exit, signame))		
	freeze_support()	
	
	parser = argparse.ArgumentParser(description=app_title)
	parser.add_argument('-s','--session',default='',type=str,  help='Session file to open')
	args = parser.parse_args()
	default_session=None
	if hasattr(args, 'session') and args.session:
		default_session=args.session
		
	start_gui(1)
		

	if 0:	
		pool_size=1

		queries=[]

		
		queries.append(['test'])
			
		
		m= multiprocessing.Manager()

		inputs = list([[i,t] for i,t in enumerate(queries)])

		pool = m.Pool(processes=pool_size,
									initializer=start_process,
									)
		#pprint(dir(pool))
		e(0)		
		pool_outputs = pool.map(test_MP, inputs)
		#pool.close() # no more tasks
		#pool.join()  # wrap up current tasks

		#print ('Pool    :', pool_outputs)
		#e(0)
		print ('#'*60)
		print ('#'*60)
		pprint(pool_outputs)
		print ('#'*60)
		print ('#'*60)
		
