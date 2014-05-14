import socket, ssl, sys, urllib2, time, string, httplib

irc = ssl.wrap_socket(socket.socket())        
ircServer = "<your irc server here>"
ircChannel = "<your irc channel here>"
ircSSLPort = 6667
ircUser = "awesomebot"
ircNick = "awesomebot"
ircCKey = "."
ircPass = "<password | needed for SSL>"
count = 0

def rawSend(data):
    irc.send(data + "\r\n")

def ircConnect():
    irc.connect((ircServer, ircSSLPort))

def ircMessage(msg, sender = None):
    if sender is None:
        rawSend("PRIVMSG " + ircChannel + " :" + msg + "\r\n")
    else:
        ircMessage("@" + sender + ": " + msg)

def ircRegister():
    rawSend("USER " + ircUser + " " + ircUser + " " + ircUser + " :" + ircUser)

def ircSendNick():
    rawSend("NICK " + ircNick + "\r\n")

def ircJoin():
    rawSend("JOIN " + ircChannel + "\r\n")

def ircPassword():
    rawSend("PASS " + ircPass + "\r\n")

def GTFO(reason):
    sonRea = ''.join(reason)
    rawSend("PART " + ircChannel + " " + sonRea + "\r\n")

def get_cmd(keyword):
    return "<>" + keyword

def addressing_me(line):
    return ":" + ircNick + ":" in line or ":@" + ircNick + ":" in line

def getSender(line):
    #Eg., vyng!vyng@irc.tinyspeck.com PRIVMSG #random :@oontvoo: hi
    #TODO: hacky, I know!

    splitTks = string.split(line, "!")
    if len(splitTks) > 0:
        return splitTks[0]
    else:
        return None

# get message (presumably addressing me)
def getMsg(line):
    splitTks = string.split(line, ircNick + ":")
    if len(splitTks) > 1:
        return splitTks[1]
    else:
        return None

def isDoctorActive():
    # TODO set up CEP engine
    return False

def getDoctorResponse(msg, sender):
    # TODO
    return None

def welcome(line):
    if ": active" in line:
        # make sure "active" isn'tr just part of a sentence
        split_str = string.split(line, "!")
        if len(split_str) > 1:
            new_user = split_str[0]
            # dont self-welcome and 
            # don't welcome pple in *other* channels. (slack's specific)
            if (not ircNick == new_user) and  "#" + ircChannel + " +v " + new_user + " : active" in split_str[1]:
                ircMessage("Welcome [back]!", new_user)

def respond(line):
    sender = getSender(line)
    msg = getMsg(line)
    
    # commands
    if get_cmd("go away") in msg:
        res = "Bye! [killed by " + sender + ", time of death: " + time.ctime() + "]"
        ircMessage(res)
        sys.exit("Received exit command from " + sender + " | time of death: " + time.ctime())
    elif get_cmd("LIST") in msg or get_cmd("list") in msg:
        rawSend("LIST " + ircChannel)
    elif get_cmd("download") in msg:
        # TODO:
        c = httplib.HTTPSConnection("https://files.slack.com/files-pri/T029TKF5P-F029UFVBY/simple.sbapp", ircPort)
        c.request("GET", "/")
        response = c.getresponse()
        print response.status, response.reason
        data = response.read()
        print data

    # regular conversational chat
    else:
        res = "Hi," + sender + "! This is all I can say for now"
        if isDoctorActive():
            res = getDoctorResponse(msg, sender)

        ircMessage(res, sender)

def setVariables():
    if len(sys.argv) != 5:
        sys.exit("Usage: python bot.by <hostname> <channle> <username> <password>")
    else:
        global ircServer
        ircServer = sys.argv[1]

        global ircChannel
        ircChannel= sys.argv[2]

        global ircUser
        ircUser = sys.argv[3]

        global ircPass
        ircPass = sys.argv[4]
        
        
def Initialize():
    setVariables()

    ircConnect()
    ircRegister()
    ircPassword()
    ircSendNick()
    ircJoin()

Initialize()

print("done init")
while True:

    data = irc.recv(1024)
    data = data.strip()
    if not data.isspace():
        print(data)


    # respond to server
    if "PING" in data:
        rawSend("PONG")

    # welcome (back)
    # vy.nguyen.0000!vy.nguyen.0000@irc.tinyspeck.com MODE #random +v vy.nguyen.0000 : active
    #welcome(data)
    
    # respond to humans
    # only if they're addressing me directly, with one exception
    if "ping" in data:
        ircMessage("pong", getSender(data))

    if addressing_me(data):
        respond(data)

