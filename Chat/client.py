import socket
import struct
import sys
import os
import threading
from tkinter import *
import math
from tkinter import ttk

FORMAT = 'utf-8'

#message = input("Enter message: ").encode("utf-8")
multicast_group = ('224.3.29.71', 10000)

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set a timeout so the socket does not block indefinitely when trying
# to receive data.
sock.settimeout(10000)

# Set the time-to-live for messages to 1 so they do not go past the
# local network segment.
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

class GUI:
    def __init__(self):
        self.Window = Tk() 
        self.Window.withdraw()     
        
        self.login = Toplevel() 
        
        self.login.title("Ingreso") 
        self.login.resizable(width = False,  
                             height = False) 
        self.login.configure(width = 400, 
                             height = 300) 
        
        self.pls = Label(self.login,  
                       text = "Por favor ingrese su nombre", 
                       justify = CENTER,  
                       font = "Helvetica 14 bold") 
          
        self.pls.place(relheight = 0.15, 
                       relx = 0.2,  
                       rely = 0.07) 
        
        self.labelName = Label(self.login, 
                               text = "Nombre: ", 
                               font = "Helvetica 12") 
          
        self.labelName.place(relheight = 0.2, 
                             relx = 0.1,  
                             rely = 0.2) 
        
        self.entryName = Entry(self.login,  
                             font = "Helvetica 14") 
          
        self.entryName.place(relwidth = 0.4,  
                             relheight = 0.12, 
                             relx = 0.35, 
                             rely = 0.2) 
          
        self.entryName.focus() 
        
        self.go = Button(self.login, 
                         text = "CONTINUAR",  
                         font = "Helvetica 14 bold",  
                         command = lambda: self.goAhead(self.entryName.get())) 
          
        self.go.place(relx = 0.4, 
                      rely = 0.55) 
        self.Window.mainloop() 

    def sendName(self, name):
        try:
            print("Enviando nombre al grupo")
            sock.sendto("NAME".encode(FORMAT), multicast_group)
            sock.sendto(name.encode(FORMAT), multicast_group)
            print("Nombre enviado")
        except:
            print("Error al enviar nombre")

    def goAhead(self, name):
        self.login.destroy()
        self.layout(name)
        self.sendName(name)

        rcv = threading.Thread(target = self.receiveMessage)
        rcv.start()

    def layout(self, name):
        self.name = name 
        
        self.Window.deiconify() 
        self.Window.title("CHAT") 
        self.Window.resizable(width = False, 
                              height = False) 
        self.Window.configure(width = 470, 
                              height = 650,
                              #height = 550, 
                              bg = "#17202A") 
        self.labelHead = Label(self.Window, 
                             bg = "#17202A",  
                              fg = "#EAECEE", 
                              text = self.name , 
                               font = "Helvetica 13 bold", 
                               pady = 5) 
          
        self.labelHead.place(relwidth = 1) 
        self.line = Label(self.Window, 
                          width = 450, 
                          bg = "#ABB2B9") 
          
        self.line.place(relwidth = 1, 
                        rely = 0.07, 
                        relheight = 0.012) 
          
        self.textCons = Text(self.Window, 
                             width = 20,  
                             height = 2, 
                             bg = "#17202A", 
                             fg = "#EAECEE", 
                             font = "Helvetica 14",  
                             padx = 5, 
                             pady = 5) 
          
        self.textCons.place(relheight = 0.745, 
                            relwidth = 1,  
                            rely = 0.08) 
          
        self.labelBottom = Label(self.Window, 
                                 bg = "#ABB2B9", 
                                 height = 80) 
          
        self.labelBottom.place(relwidth = 1, 
                               rely = 0.825) 
          
        self.entryMsg = Entry(self.labelBottom, 
                              bg = "#2C3E50", 
                              fg = "#EAECEE", 
                              font = "Helvetica 13") 
          
        self.entryMsg.place(relwidth = 0.74, 
                            relheight = 0.06, 
                            rely = 0.025,
                            #rely = 0.008, 
                            relx = 0.011) 
          
        self.entryMsg.focus() 
          
        
        self.buttonMsg = Button(self.labelBottom, 
                                text = "Enviar", 
                                font = "Helvetica 10 bold",  
                                width = 20, 
                                bg = "#ABB2B9", 
                                command = lambda : self.sendButton(self.entryMsg.get())) 
          
        self.buttonMsg.place(relx = 0.77, 
                             rely = 0.003,
                             #rely = 0.008, 
                             relheight = 0.08,
                             #relheight = 0.06,  
                             relwidth = 0.22) 
          
        self.textCons.config(cursor = "arrow") 
          
        
        scrollbar = Scrollbar(self.textCons) 
        
        scrollbar.place(relheight = 1, 
                        relx = 0.974) 
          
        scrollbar.config(command = self.textCons.yview) 
          
        self.textCons.config(state = DISABLED)

        self.comboBox = ttk.Combobox(self.labelBottom, state="readonly", 
                        values=[
                                "Todos"])
        self.comboBox.place(relwidth = 0.74, 
                            #width = 300,
                            relx = 0.011,
                            #relx = 0.11, 
                            rely = 0.003)

    def sendButton(self, msg):
        self.textCons.config(state = DISABLED)
        self.msg = msg
        self.entryMsg.delete(0, END)
        snd = threading.Thread(target = self.sendMessage)
        snd.start()

    def receiveMessage(self):
        while True:
            try:
                data, server = sock.recvfrom(1024)
                print(data)
                
                message = data.decode(FORMAT)
                print('Recibido: "%s" de %s' % (message, server))
                
                if message.startswith('list'):
                    membersList = message.split(',')
                    membersList.remove('list')
                    # delete my name from the list
                    membersList.remove(self.name)
                    membersList.insert(0, 'Todos')
                    self.comboBox['values'] = membersList

                    # set comobox default value
                    self.comboBox.current(0)

                # self.comboBox["values"] = message.split()

                else:

                    self.textCons.config(state = NORMAL) 
                    self.textCons.insert(END, message+"\n\n")

                    self.textCons.config(state = DISABLED) 
                    self.textCons.see(END)

                    #self.comboBox["values"] = message.split()
            except:
                print("Ocurrio un error")
                sock.close()
                print("Conexion cerrada")
                break

    def sendMessage(self):
        self.textCons.config(state = DISABLED)
        # get comobox value
        detination = self.comboBox.get()
        
        while True:
            message = (f"{detination}|$%|{self.name}: {self.msg}")
            sock.sendto(message.encode(FORMAT), multicast_group)
            break

# the following code is commented but is the basic for multicast communication
"""
    def sendMessage(self):
        while True:

            message = input("Enter message: ").encode("utf-8")

            try:
                # Send data to the multicast group
                print (sys.stderr, 'sending "%s"' % message)
                sent = sock.sendto(message, multicast_group)

                # Look for responses from all recipients
                while True:
                    print (sys.stderr, 'waiting to receive')
                    try:
                        data, server = sock.recvfrom(16)
                    except socket.timeout:
                        print (sys.stderr, 'timed out, no more responses')
                        #os.system("PAUSE")
                        break
                    else:
                        print (sys.stderr, 'received "%s" from %s' % (data.decode("utf-8"), server))

            except:
                print("ERROR")               
            #finally:
                #print (sys.stderr, 'closing socket')
                #sock.close()
"""

g = GUI()