import tkinter as Tk
import logging
from socketserver import TCPServer
from collections import defaultdict
import threading
from umodbus import conf
from umodbus.server.tcp import RequestHandler, get_server
from umodbus.utils import log_to_stream

class MBS:
    def __init__(self):
        self.window = Tk.Tk()
        self.delay = 150
        self.regs = []
        hr_ofs = 3 #Row Offset for Holding Register Textboxes
        Tk.Label(self.window,text = 'Holding Register Offset:').grid(row = 1, column =0,columnspan = 3, sticky = 'w')
        self.register_offset = Tk.Text(self.window,height = 1,width =5)
        self.register_offset.grid(row =1,column=3,sticky = 'ew')
        self.register_offset.insert('1.0','4000')
        for i in range(10):
            for j in range(10):
                a = Tk.Text(self.window,height = 1,width =5)
                self.regs.append(a)
                a.grid(row = i+hr_ofs, column = j, padx = 1, pady = 1,sticky = 'ew')
                
               
                #self.regs.append(a)
        for reg in self.regs:
            reg.insert('1.0','0')

        # Add stream handler to logger 'uModbus'.
        log_to_stream(level=logging.DEBUG)
        self.data_store = defaultdict(int)
        print(self.data_store)
        conf.SIGNED_VALUES = True
        TCPServer.allow_reuse_address = True
        app = get_server(TCPServer, ('localhost', 502), RequestHandler)

        @app.route(slave_ids=[1], function_codes=[3, 4], addresses=list(range(0, 100)))
        def read_data_store(slave_id, function_code, address):
            return self.data_store[address]

        @app.route(slave_ids=[1], function_codes=[6, 16], addresses=list(range(0, 100)))
        def write_data_store(slave_id, function_code, address, value):

            data_store[address] = value
        
        
        thread = threading.Thread(target = app.serve_forever)
        thread.deamon = True
        thread.start()

       
        self.update()
        self.window.mainloop()
               
        
        
        

    def update(self):
        #self.app.process_request()
        for i,item in enumerate(self.regs):
            self.data_store[i] = int(item.get("1.0",Tk.END))
        self.window.after(self.delay, self.update)

test = MBS()