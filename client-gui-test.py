"""
Trial project - Team NILE
IRC chat client
"""

import socket, select, string, sys, threading
import Tkinter

NAME = 'Anonymous'

"""
Send contents of entry box, prints it then clears it
"""
def outbuttonCallback(*args):
    entry.focus_force()
    newMessage = entry.get()
    textboxPrint('<You> '+newMessage)
    global NAME
    sendMessage('<name>'+NAME+'</name>\n<message>'+newMessage+'</message>')
    clearEntry()

"""
Changes name of client, and sends new name
"""
def namebuttonCallback(*args):
    global NAME
    name.focus_force()
    newName = name.get()
    if newName == "" and NAME != "Anonymous":
        textboxPrint('You changed your name to Anonymous')
        sendMessage('<setname old="'+NAME+'" new="Anonymous"></setname>')
        NAME = 'Anonymous'
        name.insert(Tkinter.END, 'Anonymous')
    elif newName != "" and newName != NAME:
        textboxPrint('You changed your name to '+newName)
        sendMessage('<setname old="'+NAME+'" new="'+newName+'"></setname>')
        NAME = newName
    else:
        pass
    clearFocus()

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
Clear text from entry widget
"""
def clearEntry(*args):
    entry.delete(0, len(entry.get()))

"""
Clear focus from widget
"""
def clearFocus(*args):
    root.focus()

"""
Parse message XML and output on textbox
"""
def onReceive(data):
    pass

"""
Connect to HOST and PORT
"""
def connectServer(*arg):
    try:
        sendSocket.connect((HOST, PORT))
    except:
        textboxPrint('Cannot connect to Host: ' + str(HOST) + ':' + str(PORT) + '\n')
        print 'Cannot connect to Host: ' + str(HOST) + ':' + str(PORT) + '\n'
        sys.exit()
    finally:
        pass
    textboxPrint('Connected to chat server\n')
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
                        #onReceive(data)
                        textboxPrint(data)

if __name__ == "__main__":
    if len(sys.argv)!=2:
        print 'Usage: client-gui.py <hostaddress>'
        sys.exit(2)

    HOST = sys.argv[1]
    PORT = 5000
    sendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sendSocket.settimeout(None)

    #connectServer()

    root = Tkinter.Tk()

    frame = Tkinter.Frame(root)
    frame.pack(padx=2, pady=2)

    nameLabel = Tkinter.Label(frame, text="Name:")
    nameLabel.pack(side=Tkinter.LEFT)

    name = Tkinter.Entry(frame)
    name.bind("<Return>", namebuttonCallback)
    name.bind("<Escape>", clearFocus)
    name.insert(Tkinter.END, 'Anonymous')
    name.pack(padx=3, side=Tkinter.LEFT)

    namebutton = Tkinter.Button(frame, text="Change", command=namebuttonCallback)
    namebutton.pack(padx=2, pady=2, side=Tkinter.LEFT)

    frameTextbox = Tkinter.Frame(frame)
    frameTextbox.pack()

    scrollbar = Tkinter.Scrollbar(frameTextbox, jump=0)
    scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

    textbox = Tkinter.Text(frameTextbox, yscrollcommand=scrollbar.set)
    textbox.configure(state='disabled')
    textbox.pack()

    textLabel = Tkinter.Label(frame, text="Text:")
    textLabel.pack(side=Tkinter.LEFT)

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

    sendSocket.close()

