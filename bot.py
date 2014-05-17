# RUN these before running this script
# export PYTHONPATH=/opt/streambase/lib64/python2.6
# export STREAMBASE_HOME=/opt/streambase

import socket, ssl, sys, urllib2, time, string, httplib, os, subprocess, streambase as sb

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
drActive = False
SB_HOME = "/opt/streambase"
help_text = None

# streambase properties
URL="sb://localhost:43458"
DEFAULT_TIMEOUT = 500 #ms 
client = None
schema = None

def rawSend(data):
    irc.send(data + "\r\n")

def ircConnect():
    irc.connect((ircServer, ircSSLPort))

def ircMessage(msg, sender = None):
    if isinstance(msg, basestring):
        if sender is None:
            rawSend("PRIVMSG " + ircChannel + " :" + msg + "\r\n")
        else:
            ircMessage("@" + sender + ": " + msg)
    else:
        for st in msg:            
            ircMessage(st, sender)

def ircPrivateMsg(msg, sender):
    # PRIVMSG awesomebot :awesomebot:
    rawSend("PRIVMSG " + sender + " :" + sender + ": " + msg + "\r\n")

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

def isPrivateMsg(line):
    # PRIVMSG awesomebot
    # awesomebot :awesomebot:
    return  "PRIVMSG " + ircNick + " " in line

def areAllowedArgs(args):
    # TODO: probably don't want them to run "checkout" commands!!!!
    return True

def getOutput(cmd, timeout=5):
    # execute the command
    p = subprocess.Popen(cmd,
                         stderr=subprocess.STDOUT,  # merge stdout and stderr
                         stdout=subprocess.PIPE,
                         shell=True)
    # poll for terminated status till timeout is reached
    t_beginning = time.time()
    seconds_passed = 0
    while True:
        if p.poll() is not None:
            out, err = p.communicate()
            print(out)
            res = string.split(out.strip(), "\n")
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
            res = "NO repsonse! [TIMEDOUT = " + str(timeout) + " secs]"
            break
        time.sleep(0.1)
    return res

def respond(line):
    sender = getSender(line)
    msg = getMsg(line)
    isPrivate = isPrivateMsg(line)

    ##############################################
    #                  commands
    #############################################
    
    # kill the bot
    if get_cmd("go away") in msg:
        res = "Bye! [killed by " + sender + ", time of death: " + time.ctime() + "]"
        ircMessage(res)
        sys.exit("Received exit command from " + sender + " | time of death: " + time.ctime())
        
    # prints help
    elif get_cmd("help") in msg:
        global help_text
        if help_text is None:
            help_text = open("help_plaintext.txt", "r").read().strip().split('\n')
        res = help_text

    # eval an expression with CEP
    elif get_cmd("eval") in msg:
        sbCmd = SB_HOME + "/bin/sbd --eval " + "'" + unEscapeCmd("eval", msg) + "'"
        print("COMMAND executed: " + sbCmd)
        stdOut = os.popen(sbCmd)
        res = stdOut.read()
        print("RESPONSE: " + res)

    # test args
    elif get_cmd("test_args") in msg:
        args = string.split(msg, get_cmd("test_args"))[1]
        res = getOutput("java Simple " + args)

    # sbx command
    elif get_cmd("sbx") in msg:
        args = string.split(msg, get_cmd("sbx"))[1]
        print("args: " + args)
        if (areAllowedArgs(args)):
            res =["Executing  \"sbx " + args + "\"",
                  getOutput("sbx " + args)]
        else:
            res = args + " is NOT allowed!"
    ###############################################
    #           regular conversational chat
    ##############################################
    else:
        res = "Hi," + sender + "! The doctor is busy, so this is all I know how to say!"
        if isDoctorActive():
            res = getDoctorResponse(msg, sender)
        

    ###### SEND the response #####
    if isPrivate:
        print("Got private msg")
        ircPrivateMsg(res, sender)
    else:
        ircMessage(res, sender)

def setUpDoctor():
    global client
    global URL
    global schema
    global drActive

    try:
        client = sb.Client(URL)
        client.subscribe("OutputStream")
        schema = client.getStreamProperties("InputStream").getSchema()
        drActive = True
    except:
        pass

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

