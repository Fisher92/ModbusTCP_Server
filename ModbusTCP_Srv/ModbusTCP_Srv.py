import tkinter as Tk
import logging
from socketserver import TCPServer
from collections import defaultdict
import threading
from umodbus import conf
from umodbus.server.tcp import RequestHandler, get_server
from umodbus.utils import log_to_stream
from time import sleep
from multiprocessing import Process

class MBS:
    def __init__(self):
        self.window = Tk.Tk()
        self.window.title("Modbus TCP Server")
        self.window.protocol("WM_DELETE_WINDOW", self._delete_window)
        self.delay = 20 # Update Tkinter Window
        self.regs_store = defaultdict(int) #Store Holding Registers
        self.coil_store = defaultdict(bool) #Store Coils
        self.txt_regs = []
        self.lbl_regs = []
        self.coil_chbx = []
        self.coil_chbx_sts = []
        for i in range(100):
            self.coil_chbx_sts.append(Tk.IntVar())
        self.regofs = 0
        self.coilofs = 0
        Tk.Label(self.window,text = 'Holding Register Offset (Functions 3,4):').grid(row = 1, column =0,columnspan = 3, sticky = 'w')
        Tk.Label(self.window,text = 'Coils Offset (Functions 1,2):').grid(row = 1, column =12,columnspan = 3, sticky = 'w')
        self.register_offset = Tk.Text(self.window,height = 1,width =5)
        self.register_offset.grid(row =1,column=3,padx=1,sticky = 'ew')
        self.register_offset.insert('1.0','0')
        self.coil_offset = Tk.Text(self.window,height = 1,width =5)
        self.coil_offset.grid(row =1,column=15,padx=1,sticky = 'ew')
        self.coil_offset.insert('1.0','0')
        self.base = 10
        self.run = False
        self.btn_run = Tk.Button(self.window,text = 'Start', command = self.ctrl_server)
        self.btn_run.grid(row=13,column=0,sticky='w')
        for i in range(10):
            for j in range(1,11):
                a = Tk.Text(self.window,height = 1,width =7)
                self.txt_regs.append(a)
                a.grid(row = i+3, column = j, padx = 1, pady = 1,sticky = 'ew')
                a.insert('1.0','0')
                a.bind('<FocusOut>', self.rds)
        for i in range(3,13):
            a = Tk.Label(self.window,text = 'Registers:')
            self.lbl_regs.append(a)
            a.grid(row = i,column = 0)

        for i,item in enumerate(self.lbl_regs):
                item.config(text = 'Reg {:0>3d}:{:0>3d}'.format(self.regofs+10*i+1,self.regofs+10*i+10))
        log_to_stream(level=logging.DEBUG)
        cnt = 0
        for i in range(3,13):
            for j in range(12,22):
                a=Tk.Checkbutton(text = 'CC',onvalue = 1, offvalue = 0, variable = self.coil_chbx_sts[cnt])
                self.coil_chbx.append(a)
                a.grid(row=i,column=j)
                cnt +=1
        for i,item in enumerate(self.coil_chbx):
                item.config(text = '{:0>3d}'.format(self.coilofs+i+1))
                
        conf.SIGNED_VALUES = True
        TCPServer.allow_reuse_address = True
        self.app = get_server(TCPServer, ('localhost', 502), RequestHandler)
 
        self.thread = threading.Thread(target = self.__Serve, args=(True,))#self.app.serve_forever)
        self.thread.deamon = True

   
        self.update()
        self.window.mainloop()

    def rds(self,event):
        t= event.widget.get("1.0",Tk.END)
        value=t.replace(" ","")
        if self.base == 10:
            try:
                rval = int(value)
                event.widget.config(foreground="black")
                event.widget.delete('1.0', Tk.END)
                event.widget.insert("1.0",str(int(value)))
                #print(str(value).strip())
            except:
                event.widget.config(foreground="red")

    def ctrl_server(self):
        if self.run == False:
            self.btn_run.config(text = "Stop", state=Tk.DISABLED)
            try:
                self.regofs = int(self.register_offset.get("1.0",Tk.END))
            except:
                self.regofs = 0
            try: 
               self.coilofs= int(self.coil_offset.get("1.0",Tk.END))
            except:
               self.coilofs = 0
            for i,item in enumerate(self.lbl_regs):
                item.config(text = 'Reg {:0>3d}:{:0>3d}'.format(self.regofs+10*i+1,self.regofs+10*i+10))           
            for i,item in enumerate(self.coil_chbx):
                item.config(text = '{:0>3d}'.format(self.coilofs+i+1))    
            self.register_offset.config(state=Tk.DISABLED,background="gray")
            self.coil_offset.config(state=Tk.DISABLED,background="gray")
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
        regofs = int(self.register_offset.get("1.0",Tk.END))
        @self.app.route(slave_ids=[1], function_codes=[3, 4], addresses=list(range(self.regofs, self.regofs+100)))
        def read_data_store(slave_id, function_code, address):
            return self.regs_store[address]
        
        @self.app.route(slave_ids=[1], function_codes=[1, 2], addresses=list(range(self.coilofs, self.coilofs+100)))
        def read_data_store(slave_id, function_code, address):
            return self.coil_store[address]

    def __Serve(self,run):
        while run == True:
            self.app.handle_request()
        pass
 
    def update(self):
        #self.app.process_request()
        
        for i,item in enumerate(self.txt_regs):
            try:
                self.regs_store[i+self.regofs] = int(item.get("1.0",Tk.END))
            except:
                pass

        for i,item in enumerate(self.coil_chbx):
            try:
                self.coil_store[i+self.coilofs] = self.coil_chbx_sts[i].get()
            except:
                pass
        
        self.window.after(self.delay, self.update)
    def _delete_window(self):
        print("closing")
        try:
            self.window.destroy()
        except:
            pass


test = MBS()