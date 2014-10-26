#bot.py is a Bucket-like IRC chat bot
#Copyright 2012, 2013, 2014 Andrew Van Hise

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


__module_name__ = "bot.py"
__module_version__ = "1.9"
__module_description__ = "a Bucket-like IRC chat bot"


import sys, os, inspect

# create an arbitrary object, determine the path of the file it was created in (i.e. this one), remove the file name part
# technically the previous workaround was uglier
currentDirName = os.path.abspath(inspect.getsourcefile(lambda _: None)).replace(__module_name__, "")
sys.path.append(currentDirName)

import text
from botDbAccess import *
from message import *
from botFunctions import *
import xchat, random, time, ConfigParser


# program start
print ">>> bot.py loading"

#  CONFIG STUFF
configFile = currentDirName+"bot.conf"
config = ConfigParser.RawConfigParser()
config.read(configFile)

botName = config.get('Section', 'name')
serverName = config.get('Section', 'server')
portNum = config.get('Section', 'port')
passwordFile = config.get('Section', 'passwordFile')
dbFile = config.get('Section', 'database')

status = {
  "connecting": False,
  "connected": False,
  "connectAttempt": 0,
  "identifying": False,
  "identified": False,
  "unbanChanList": [],
  "cannotJoinChans": [],
  "declareFailure": False
}

# initialization stuff
random.seed()
db = dbAccess(currentDirName+dbFile)
msg = msgObject()
rejoinList = []
abuseDict = {}
nickChangeTimeout = []



def identifyWithServer():
  # get password and identify
  try:
    file = open(currentDirName + passwordFile, 'r')
  except IOError as err:
    print err
    status["declareFailure"] = True
  else:
    password = file.readline().replace('\n','')
    file.close()
    xchat.command("msg nickserv identify %s" % password)
    
    
def joinChannels():
  actualChanList = xchat.get_list('channels')
  chanList = db.listChans()
  
  for chan in chanList:
    if chan not in [x.channel for x in actualChanList]:
      xchat.command("join %s" % chan)




chanMsgFunctions = [
  autoResponseTrigger, 
  loneHighlight, 
  storePerm, recallPerm, 
  giveStuff, interceptStuff,
  banUser, unbanUser,
  addAdmin, delAdmin,
  addChannel, delChannel,
  getAdminList, getBanList, getChanList, getAdminList,
  manualCommand,
  markov,
  badIdentify, 
  dotTxt, downvote, recallTxt,
  postCount,
  goodBandName,
  setTimer, 
  sourceRequest, 
  messageByProxy, 
  autoResponseRegister,
  slapByProxy, attackByProxy, 
  nsCalc, 
  youtubeLink, lmgtfy, legitSite,
  genRandom, 
  greetings, 
  apology, 
  thankBot, fightBack, eatBot, touchBot, robBot, 
  whatIsBot, 
  isBot, 
  howAreYou, howAreThings,
  insultBot, praiseBot, 
  willItBlend, 
  adjAssVerb, 
  sadTruths, 
  someoneWon, 
  someoneHas, 
  aOrB,
  botLoves, 
  thatsWhatSheSaid, 
  blankYourself, 
  youreDumb, 
  openCsServer,
  colorize, 
  yoMama, 
  yolo,
  yelling, 
  weeaboo,
  ponies, 
  forCadie,
  helpFunction,
  genericHighlight, 
  parenMatcher, 
  buttBot
]
    

# callback when a message is posted in a channel bot is in
def ScanChanMsg(word, word_eol, userdata):
  global msg
  channel = xchat.get_info("channel")
  
  #create the message object
  msg.strUpdate(word, channel)
  
  #increment post count
  db.incPostCount(msg.getUserName())
  
  #add message to log
  db.storeLog(msg.getUserName(), msg.rawStr, channel)
  
  #if the event occured in an active channel and user isn't banned or abusive
  if channel.lower() not in db.listChans([True]):
    print '>>bot muted in %s<<' % channel
    return xchat.EAT_NONE
  elif msg.getUserName().lower() in db.listUserlist([BANNED]):
    print '>>user %s is on banlist<<' % msg.getUserName()
    return xchat.EAT_NONE
  elif msg.getUserName() in abuseDict and abuseDict[msg.getUserName()] > 5:
    print '>>user %s is temporarily banned for bot flood<<' % msg.getUserName()
    return xchat.EAT_NONE
  elif msg.getUserName() in nickChangeTimeout:  
    print '>>user %s is on timeout for nick change<<' % msg.getUserName()
    return xchat.EAT_NONE
  else:
    for function in chanMsgFunctions:
      result = function(msg, botName, channel, db)
      # if a function triggered
      if result:
        #update abuseDict
        if msg.getUserName() in abuseDict:
          abuseDict[msg.getUserName()] += 1
        else:
          abuseDict[msg.getUserName()] = 1
        return xchat.EAT_PLUGIN
      
      
xchat.hook_print("Channel Message", ScanChanMsg)
xchat.hook_print("Channel Action", ScanChanMsg)
xchat.hook_print("Channel Action Hilight", ScanChanMsg)
xchat.hook_print("Channel Msg Hilight", ScanChanMsg)
xchat.hook_print("Channel Notice", ScanChanMsg)



privMsgFunctions = [
  autoResponseRegister,
  helpFunction,
  addChannel, delChannel,
  banUser, unbanUser,
  getAdminList, getChanList, getBanList,
  manualCommand,
  addAdmin, delAdmin,
  sourceRequest,
  privMsgCatch
] 

# callback when private message received
def ScanPrivMsg(word, word_eol, userdata): 
  global msg
  channel = xchat.get_info("channel")
  msg.strUpdate(word, channel)

  if msg.getUserName().lower() not in db.listUserlist([BANNED]):
    for function in privMsgFunctions:
      result = function(msg, botName, channel, db)
      if result: return xchat.EAT_PLUGIN
        
  return xchat.EAT_NONE

xchat.hook_print("Private Message", ScanPrivMsg)
xchat.hook_print("Private Message to Dialog", ScanPrivMsg)
xchat.hook_print("Private Action", ScanPrivMsg)
xchat.hook_print("Private Action to Dialog", ScanPrivMsg)



# send any waiting messages to people already in the channels
def chanProxyMessageCheck():
  chanList = xchat.get_list("channels")
  for chan in chanList:
    if chan.type == 2:   # a channel, not a query window or server
      chanContext = chan.context
      chanContext.set()
      chanName = chanContext.get_info("channel")
      userList = chanContext.get_list("users")

      for user in userList:
        checkForProxyMessage(user.nick, chanName)

        
# check for messages that should be delivered now
def checkForProxyMessage(nick, channel):
  newMessages = db.checkMessages(nick.lower(), channel)
  if newMessages != None:
    for newMsg in newMessages:
      xchat.command("msg %s %s" % (channel, newMsg))





# callback when bot receives a notice
def ScanNotice(word, word_eol, userdata):
  sender = word[0]
  text = word_eol[1]
  
  # if it is a nickserv status request
  if sender == "NickServ" and text.split()[0] == "STATUS":
    type = word[1]
    type, nick, level = text.split()
    statusReturn(nick, level, db)
    
  # if server has identified the bot, join channels
  elif sender == "NickServ" and string.count(text, "Password accepted") > 0: 
    status["identified"] = True
    status["identifying"] = False
    statusCheck()
    
  elif sender == "ChanServ" and text == "Permission denied.":
    #assume bot was trying to unban self from a channel, declare channel can't be joined
    status["cannotJoinChans"].append(status["unbanChanList"][0])
    status["unbanChanList"].pop(0)
    if len(status["unbanChanList"]) != 0:
      xchat.command("cs unban %s" % status["unbanChanList"][0])
      
    
  elif sender == "ChanServ" and string.count(text, "You have been unbanned") > 0:
    xchat.command("join %s" % status["unbanChanList"][0])
    status["unbanChanList"].pop(0)
    if len(status["unbanChanList"]) != 0:
      xchat.command("cs unban %s" % status["unbanChanList"][0])
  
  return xchat.EAT_PLUGIN
xchat.hook_print('Notice', ScanNotice)


def ScanBanMsg(word, word_eol, userdata):
  channel = word[0]
  
  #if bot is banned from an assigned channel and not waiting for unbanning response
  if channel in db.listChans() and channel not in status["cannotJoinChans"]:
    #try to unban self
    status["unbanChanList"].append(channel)
    #only unban from one channel at a time so if permission is denied, the channel is known
    if len(status["unbanChanList"]) == 1:
      xchat.command("cs unban %s" % channel)

  return xchat.EAT_PLUGIN
xchat.hook_print('Banned', ScanBanMsg)




# callback when anyone joins a channel bot is in 
def ScanJoinMsg(word, word_eol, userdata):
  joinNick, joinChannel, joinHost = word
  checkForProxyMessage(joinNick, joinChannel)
  return xchat.EAT_PLUGIN
xchat.hook_print('Join', ScanJoinMsg)


def selfJoinChannel(word, word_eol, userdata):
  chanProxyMessageCheck()
  return xchat.EAT_PLUGIN
xchat.hook_print('You Join', selfJoinChannel)


# when someone changes nick
def ScanNickMsg(word, word_eol, userdata):
  newName = word[1]
  nickChangeTimeout.append(newName)
  xchat.hook_timer(10000, endNickTimeout)  # 10 second timeout
  
  channel = xchat.get_info("channel")
  checkForProxyMessage(newName, channel)
  
  # xchat.command("msg ns status %s" % newName)
  return xchat.EAT_PLUGIN
xchat.hook_print('Change Nick', ScanNickMsg)


def handleKickMsg(kicker, kickee, kickChan, kickMsg):
  #if bot got kicked, try to rejoin
  if xchat.nickcmp(kickee, xchat.get_info("nick")) == 0:
    xchat.command("join %s" % kickChan)
    message = random.choice(text.revenge) % kicker
    xchat.command("ctcp %s action %s" % (kickChan, message))
    
  #if chanserv did the kicking
  elif xchat.nickcmp(kicker, "ChanServ") == 0:
    rejoinList.append(kickee)
    if rejoinList.count(kickee) >= 3:
      # ban someone if chanserv has kicked them 3+ times
      xchat.command("mode %s +b %s" % (kickChan, kickee))


def scanKickMsg(word, word_eol, userdata):
  kicker, kickee, kickChan, kickMsg = word
  handleKickMsg(kicker, kickee, kickChan, kickMsg)
  return xchat.EAT_PLUGIN
xchat.hook_print("Kick", scanKickMsg)


def scanOwnKickMsg(word, word_eol, userdata):
  kickee, kickChan, kicker, kickMsg = word
  handleKickMsg(kicker, kickee, kickChan, kickMsg)
  return xchat.EAT_PLUGIN
xchat.hook_print("You Kicked", scanOwnKickMsg)




# changes in bot's connection status
  
def serverConnect(word, word_eol, userdata):
  if status["connecting"]:
    status["connected"] = True
    status["connecting"] = False
    status["connectAttempt"] = 0
    statusCheck()
  return xchat.EAT_PLUGIN
  
#treating the MOTD as being fully connected to the server seems to work, I choose not to fight it
xchat.hook_print("Motd", serverConnect)
xchat.hook_print("MOTD Skipped", serverConnect)
#xchat.hook_print("Connected", serverConnect)


def serverConnectFail(word, word_eol, userdata):
  status["connecting"] = False
  xchat.hook_timer(5000, delayedStatusCheck)  # 5 second delay before reconnect attempt
  return xchat.EAT_PLUGIN
xchat.hook_print("Connection Failed", serverConnectFail)


def serverDisconnect(word, word_eol, userdata):
  if status["connected"]:
    status["connected"] = False
    status["connecting"] = False
    status["identified"] = False 
    status["identifying"] = False
    xchat.hook_timer(5000, delayedStatusCheck)  # 5 second delay before reconnect attempt
  return xchat.EAT_PLUGIN
xchat.hook_print("Ping Timeout", serverDisconnect)
xchat.hook_print("Disconnected", serverDisconnect)





# user limitations

def handleAbuseDict(userdata):
  for nick in abuseDict.keys():
    if abuseDict[nick] > 0:
      abuseDict[nick] -= 2
    else:
      del abuseDict[nick]
  return True
xchat.hook_timer(20000, handleAbuseDict)  # every 20 seconds


# removes the oldest name from the nick change timeout list
def endNickTimeout(userdata):
  nickChangeTimeout.pop(0)
  return False

  

  
def delayedStatusCheck(userdata):
  statusCheck()
  return False


def statusCheck():
  if not status["declareFailure"]:
    if xchat.get_info("server") != None:
      status["connected"] = True
  
  
    if not status["connected"] and not status["connecting"]:
      if status["connectAttempt"] >= 5:
        # reset attempts, but don't try again for 10 minutes
        status["connectAttempt"] = 0
        xchat.hook_timer(600000, delayedStatusCheck)
      else:
        print ">>> Attempting to connect to server"
        xchat.command("server %s %s" % (serverName, portNum))
        status["connecting"] = True
        status["connectAttempt"] += 1
      
    elif not status["identified"] and not status["identifying"]:
      print ">>> Attempting to identify with server"
      xchat.command("nick %s" % botName)
      identifyWithServer()
      status["identifying"] = True
      
    else:
      print ">>> Attempting to join channels"
      joinChannels()

# run on start to initialize bot
statusCheck()
  

#1. bot may not injure a human being or, through inaction, allow a human being to come to harm.
#2. bot must obey the orders given to it by human beings, except where such orders would conflict with the First Law.
#3. bot must protect its own existence as long as such protection does not conflict with the First or Second Laws.
  