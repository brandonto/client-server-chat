import socket, select, string, sys
import Tkinter
import threading

"""
Send contents of entry box, prints it then clears it
"""
def outbuttonCallback(*args):
    entry.focus_force()
    #print('>>', entry.get())
    textboxPrint('<You> '+entry.get())
    sendMessage(entry.get())
    clearEntry()

"""
Send contents of entry box
"""
def sendMessage(arg):
    try:
        sendSocket.send(arg)
    except:
        textboxPrint('Disconnected from chat server\n')
        sys.exit()

"""
Print contents of entry box
"""
def textboxPrint(arg):
    textbox.configure(state='normal')
    textbox.insert(Tkinter.END, arg+'\n')
    textbox.see(Tkinter.END)
    textbox.configure(state='disabled')

"""
Clear contents in entry box
"""
def clearEntry(*args):
    entry.delete(0, len(entry.get()))

"""
Connect to HOST and PORT
"""
def connectServer(*arg):
    try:
	    sendSocket.connect((HOST, PORT))
    except:
        #textboxPrint('Cannot connect to Host: ' + str(HOST) + ':' + str(PORT) + '\n')
	    print 'Cannot connect to Host: ' + str(HOST) + ':' + str(PORT) + '\n'
	    sys.exit()
    finally:
        pass
    #textboxPrint('Connected to chat server\n')
    print 'Connected to chat server\n'

"""
Thread running network logic alongside GUI loop
"""
class networkTaskThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        connectServer()
        self.SOCKET_LIST = [sendSocket]
    def run(self):
        self.read_sockets, self.write_sockets, self.error_sockets = select.select(self.SOCKET_LIST , [], [])

        while True:
            for listeningSocket in self.read_sockets:
                #Monitor socket for incoming message
                if listeningSocket == sendSocket:
                    data = listeningSocket.recv(8192)
                    if not data:
                        print 'Disconnected from chat server\n'
                        textboxPrint('Disconnected from chat server\n')
                        sys.exit()
                    else:
                        #Fix to weird symbol at beginning
                        textboxPrint(data[1:])

if __name__ == "__main__":

    HOST = "10.0.0.22"
    PORT = 5000
    sendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sendSocket.settimeout(None)

    #connectServer()

    root = Tkinter.Tk()

    frame = Tkinter.Frame(root)
    frame.pack(padx=2, pady=2)

    frameTextbox = Tkinter.Frame(frame)
    frameTextbox.pack()

    scrollbar = Tkinter.Scrollbar(frameTextbox, jump=0)
    scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

    textbox = Tkinter.Text(frameTextbox, yscrollcommand=scrollbar.set)
    textbox.configure(state='disabled')
    textbox.pack()

    label = Tkinter.Label(frame, text="Text:")
    label.pack(side=Tkinter.LEFT)

    entry = Tkinter.Entry(frame)
    entry.bind("<Return>", outbuttonCallback)
    entry.bind("<Escape>", clearEntry)
    entry.focus_set()
    entry.pack(padx=3, side=Tkinter.LEFT)

    outbutton = Tkinter.Button(frame, text="Output", command=outbuttonCallback)
    outbutton.pack(padx=2, pady=2, side=Tkinter.LEFT)

    quitbutton = Tkinter.Button(frame, text="Quit", fg="red", command=frame.quit)
    quitbutton.pack(padx=2, pady=2, side=Tkinter.RIGHT)

    networkTask = networkTaskThread()
    networkTask.daemon = True
    networkTask.start()

    root.mainloop()

