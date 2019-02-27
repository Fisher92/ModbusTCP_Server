import tkinter as Tk
import logging
from socketserver import TCPServer
from collections import defaultdict
import threading
from umodbus import conf
from umodbus.server.tcp import RequestHandler, get_server
from umodbus.utils import log_to_stream
from time import sleep

class MBS:
    def __init__(self):
        self.window = Tk.Tk()
        self.delay = 20 # Update Tkinter Window
        self.regs_store = defaultdict(int) #Store Holding Registers
        self.coil_store = defaultdict(bool) #Store Coils
        self.txt_regs = []
        #hr_ofs = 3 #Row Offset for Holding Register Textboxes
        Tk.Label(self.window,text = 'Holding Register Offset:').grid(row = 1, column =0,columnspan = 3, sticky = 'w')
        self.register_offset = Tk.Text(self.window,height = 1,width =5)
        self.register_offset.grid(row =1,column=3,sticky = 'ew')
        self.register_offset.insert('1.0','0')
        self.base = 10
        self.run = False
        self.btn_run = Tk.Button(self.window,text = 'Start', command = self.ctrl_server)
        self.btn_run.grid(row=13,column=0,sticky='w')
        self.test = 0
        cnt = 0
        for i in range(10):
            for j in range(10):
                a = Tk.Text(self.window,height = 1,width =7)
                self.txt_regs.append(a)
                a.grid(row = i+3, column = j, padx = 1, pady = 1,sticky = 'ew')
                a.insert('1.0','0')
                a.bind('<FocusOut>', self.rds)
                cnt+=1
       #for reg in self.txt_regs:
       #    reg.insert('1.0','0')
       #for reg in self.txt_regs:
       #    reg.bind('<Key>', self.rds)
       ## Add stream handler to logger 'uModbus'.
        log_to_stream(level=logging.DEBUG)
        
        #print(self.data_store)
        conf.SIGNED_VALUES = True
        TCPServer.allow_reuse_address = True
        self.app = get_server(TCPServer, ('localhost', 502), RequestHandler)
 
        self.thread = threading.Thread(target = self.__Serve, args=(True,))#self.app.serve_forever)
        self.thread.deamon = True
        
   
        self.update()
        self.window.mainloop()

    def rds(self,event):
        #t=event.widget
        value = event.widget.get("1.0",Tk.END)
        if self.base == 10:
            try:
                rval = int(value)
                event.widget.config(foreground="black")
            except:
                event.widget.config(foreground="red")

    def ctrl_server(self):
        if self.run == False:
            self.btn_run.config(text = "Stop", state=Tk.DISABLED)
            
            self.__MB_route()
            self.app.server_activate()
            self.run = True
            if self.thread.isAlive() ==False:
                self.thread.start()
        else:
            self.btn_run.config(text = "Start")
            self.run = False
            
            #self.thread._stop()

    def __MB_route(self):
        @self.app.route(slave_ids=[1], function_codes=[3, 4], addresses=list(range(0, 100)))
        def read_data_store(slave_id, function_code, address):
            return self.regs_store[address]
        
        @self.app.route(slave_ids=[1], function_codes=[1, 2], addresses=list(range(0, 100)))
        def read_data_store(slave_id, function_code, address):
            return self.regs_store[address]
    def __Serve(self,run):
        while run == True:
            self.app.handle_request()
        pass
 
    def update(self):
        #self.app.process_request()
        for i,item in enumerate(self.txt_regs):
            try:
                self.regs_store[i] = int(item.get("1.0",Tk.END))
            except:
                pass

        self.window.after(self.delay, self.update)


test = MBS()