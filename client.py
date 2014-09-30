"""
Trial project - Team NILE
IRC chat client
"""

import socket, select, string, sys, threading, datetime, Tkinter
import xml.etree.ElementTree as ET

"""
XML string format of messages:

<data>
    <setname old="" new=""></setname>
    <message sender="" payload=""></message>
</data>

"""

NAME = 'Anonymous'

"""
Send contents of entry box, prints it then clears it
"""
def outbuttonCallback(*args):
    entry.focus_force()
    newMessage = entry.get()
    textboxPrint('<You> '+newMessage)
    global NAME
    sendMessage('<data><message sender="'+formatXmlString(NAME)+'" payload="'+formatXmlString(newMessage)+'"></message></data>')
    clearEntry()

"""
Changes name of client, and sends new name
"""
def namebuttonCallback(*args):
    global NAME
    name.focus_force()
    newName = name.get()
    if len(newName) > 20:
        textboxPrint(name.get()+' is too long, names must be less than 20 characters')
        name.delete(0, len(name.get()))
        name.insert(Tkinter.END, NAME)
    elif newName == "" and NAME != "Anonymous":
        textboxPrint('You have changed your name to Anonymous', urgent=True)
        sendMessage('<data><setname old="'+formatXmlString(NAME)+'" new="Anonymous"></setname></data>')
        NAME = 'Anonymous'
        name.insert(Tkinter.END, 'Anonymous')
    elif newName != "" and newName != NAME:
        textboxPrint('You have changed your name to '+newName, urgent=True)
        sendMessage('<data><setname old="'+formatXmlString(NAME)+'" new="'+formatXmlString(newName)+'"></setname></data>')
        NAME = newName
    else:
        name.delete(0, len(name.get()))
        NAME = 'Anonymous'
        pass
    clearFocus()

"""
Send contents of entry box
"""
def sendMessage(arg):
    try:
        sendSocket.send(arg)
    except:
        textboxPrint('Disconnected from chat server', urgent=True)
        sys.exit()

"""
Print contents of entry box
"""
def textboxPrint(message, urgent=False):
    textbox.configure(state='normal')
    startHighlight = Tkinter.END
    textbox.insert(Tkinter.END, formatCurrentTime()+' '+message+'\n')
    if urgent:
        textbox.tag_add("urgent", startHighlight, Tkinter.END)
        textbox.tag_config("urgent", foreground="red")
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
Formats a string to be compatible with XML
"""
def formatXmlString(string):
    return string.replace('&', '&amp;').replace('<','&lt;').replace('>', '&gt;').replace('"','&quot;').replace("'",'&#39;')

def formatCurrentTime():
    return '['+str(datetime.datetime.now()).split('.')[0].split(' ')[1]+']'

"""
Parse message XML string and output on textbox
"""
def onReceive(data):
    treeRoot = ET.fromstring(data)
    elementList = treeRoot.findall("./")
    for element in elementList:
        if element.tag == "setname":
            textboxPrint(element.attrib['old']+' has changed their name to '+element.attrib['new'], urgent=True)
        elif element.tag == "message":
            sender = element.attrib['sender']
            if sender == "": #From the server
                textboxPrint(element.attrib['payload'], urgent=True)
            else:
                textboxPrint('<'+element.attrib['sender']+'> '+element.attrib['payload'])
        else:
            pass

"""
Connect to HOST and PORT
"""
def connectServer(*arg):
    try:
        sendSocket.connect((HOST, PORT))
    except:
        textboxPrint('Cannot connect to Host: ' + str(HOST) + ':' + str(PORT) + '\n', urgent=True)
        print 'Cannot connect to Host: ' + str(HOST) + ':' + str(PORT)
        sys.exit()
    finally:
        pass
    textboxPrint('Connected to chat server', urgent=True)
    print 'Connected to chat server'

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
                        print 'Disconnected from chat server'
                        textboxPrint('Disconnected from chat server', urgent=True)
                        sys.exit()
                    else:
                        onReceive(data)
                        #textboxPrint(data)

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

