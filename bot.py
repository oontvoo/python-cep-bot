# RUN these before running this script
# export PYTHONPATH=/opt/streambase/lib64/python2.6
# export STREAMBASE_HOME=/opt/streambase

import socket, ssl, sys, urllib2, time, string, httplib, os, streambase as sb

# server properties
irc = ssl.wrap_socket(socket.socket())        
ircServer = "<your irc server here>"
ircChannel = "<your irc channel here>"
ircSSLPort = 6667
ircUser = "awesomebot"
ircNick = "awesomebot"
ircCKey = "."
ircPass = "<password | needed for SSL>"


# bot's states
count = 0
drActive = True
SB_HOME = "/home/vynguye/repo/7.4.1_quickfix/branches/southstation/streambase"

# streambase properties
URL="sb://localhost:36179"
DEFAULT_TIMEOUT = 500 #ms 
client = None
schema = None

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

def unEscapeCmd(cmdName, msg):
    return string.split(msg, get_cmd(cmdName))[1].strip()

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
    global drActive
    return drActive

def getDoctorResponse(msg, sender):
    global schema
    global client
    global DEFAULT_TIMEOUT

    # enqueue
    tuple = sb.Tuple(schema)
    tuple.setString("sender", sender)
    tuple.setString("msg", msg)

    print("Enqueing " + str(tuple))
    client.enqueue("InputStream", tuple)

    # dequeue
    result = sb.DequeueResult()
    while result.getStatus() != sb.DequeueResult.GOOD:
        result = client.dequeue(DEFAULT_TIMEOUT)
        tuples = result.getTuples()
        print("len: " + str(len(tuples)))
    res = ""
    for tuple in tuples:
        print("Dequeued tuple: " + str(tuple))
        print("res: " + tuple.getString("response"))
        res = res + tuple.getString("response") + " \n"

    return res;

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
    
    ##############################################
    #                  commands
    #############################################
    
    # kill the bot
    if get_cmd("go away") in msg:
        res = "Bye! [killed by " + sender + ", time of death: " + time.ctime() + "]"
        ircMessage(res)
        sys.exit("Received exit command from " + sender + " | time of death: " + time.ctime())
        
    # eval an expression with CEP
    elif get_cmd("eval") in msg:
        sbCmd = SB_HOME + "/bin/sbd --eval " + "'" + unEscapeCmd("eval", msg) + "'"
        print("COMMAND executed: " + sbCmd)
        stdOut = os.popen(sbCmd)
        res = stdOut.read()
        print("RESPONSE: " + res)
        ircMessage(res, sender)

    ###############################################
    #           regular conversational chat
    ##############################################
    else:
        res = "Hi," + sender + "! This is all I can say for now"
        if isDoctorActive():
            res = getDoctorResponse(msg, sender)

        ircMessage(res, sender)

def setUpDoctor():
    global client
    global URL
    global schema

    client = sb.Client(URL)
    client.subscribe("OutputStream")
    schema = client.getStreamProperties("InputStream").getSchema()
    


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

        setUpDoctor()
        
def Initialize():
    setVariables()

    ircConnect()
    ircRegister()
    ircPassword()
    ircSendNick()
    ircJoin()

Initialize()

print("done init")

#TODO: replace polling with some interrupt mechanism
while True:

    data = irc.recv(1024)
    data = data.strip()
    if not data.isspace():
        print(data)


    # respond to server
    if "PING" in data:
        rawSend("PONG")

    # welcome (back)
    #welcome(data)
    
    # respond to humans
    # only if they're addressing me directly, with one exception
    if "ping" in data:
        ircMessage("pong", getSender(data))

    if addressing_me(data):
        respond(data)

