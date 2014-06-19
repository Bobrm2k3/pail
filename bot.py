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
__module_version__ = "1.8"
__module_description__ = "a Bucket-like IRC chat bot"

dirName = "C:\\bot"  # <---if bot can't find modules, change this to the location of the project directory
configFile = "bot.conf"

import sys, os
os.chdir(dirName)
sys.path.append(dirName)  # this is a workaround, needs a better solution

import text
from botDbAccess import *
from message import *
from botFunctions import *
import xchat, random, time, ConfigParser


# program start
print ">> bot.py loading <<"

#  CONFIG STUFF
config = ConfigParser.RawConfigParser()
config.read(configFile)

botName = config.get('Section', 'name')
serverName = config.get('Section', 'server')
portNum = config.get('Section', 'port')
passwordFile = config.get('Section', 'passwordFile')
dbFile = config.get('Section', 'database')
sourceFile  = config.get('Section', 'source')


# initialization stuff
random.seed()
db = dbAccess(dbFile)
msg = msgObject()
rejoinList = []
abuseDict = {}
nickChangeTimeout = []



def identifyHook(userdata):
  # get password and identify
  try:
    file = open(passwordFile, 'r')
  except IOError as err:
    print err
  else:
    password = file.readline().replace('\n','')
    file.close()
    xchat.command("msg nickserv identify %s" % password)
  return False
    
    
def chanJoinHook(userdata):
  # ajoin channels
  for chan in db.listChans():
    xchat.command("join %s" % chan)
  return False

  

#timed hook to send any waiting messages to people already in the channels
def StartupProxyMessageCheck(userdata):
  chanList = xchat.get_list("channels")
  for chan in chanList:
    if chan.type == 2:   # a channel, not a query window or server
      chanContext = chan.context
      chanContext.set()
      chanName = chanContext.get_info("channel")
      userList = chanContext.get_list("users")

      for user in userList:
        checkForProxyMessage(user.nick, chanName)
        
  return False  #turn it off
xchat.hook_timer(6000, StartupProxyMessageCheck)  # in 6 seconds


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
  botReset,
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
  youtubeLink, lmgtfy,
  genRandom, 
  greetings, 
  apology, 
  thankBot, fightBack, eatBot, touchBot, robBot, 
  whatIsBot, 
  isBot, 
  howAreYou, howAreThings,
  insultBot, praiseBot, 
  mediaReference, 
  willItBlend, 
  adjAssVerb, 
  sadTruths, 
  someoneWon, 
  someoneHas, 
  aOrB,
  botLoves, 
  dontCallMeBro, 
  thatsWhatSheSaid, 
  blankYourself, 
  youreDumb, 
  openCsServer,
  colorize, 
  rps, 
  yoMama, 
  yolo,
  yelling, 
  #godwinsLaw, 
  weeaboo,
  ponies, 
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
  botReset,
  privMsgCatch] 

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



# callback when bot receives a notice
def ScanNotice(word, word_eol, userdata):
  sender = word[0]
  type = word[1].split()[0]
  
  #if it is a nickserv status request
  if sender == "NickServ" and type == "STATUS":
    type, nick, level = word[1].split()
    statusReturn(nick, level, db)
  xchat.EAT_PLUGIN
xchat.hook_print('Notice', ScanNotice)


# callback when anyone joins a channel bot is in 
def ScanJoinMsg(word, word_eol, userdata):
  joinNick, joinChannel, joinHost = word
  checkForProxyMessage(joinNick, joinChannel)
  xchat.EAT_PLUGIN
xchat.hook_print('Join', ScanJoinMsg)


# when someone changes nick
def ScanNickMsg(word, word_eol, userdata):
  newName = word[1]
  nickChangeTimeout.append(newName)
  xchat.hook_timer(120000, endNickTimeout)  # 2 minutes timeout
  # channel = xchat.get_info("channel")
  # checkForProxyMessage(newName, channel)
  # xchat.command("msg ns status %s" % newName)
  xchat.EAT_PLUGIN
xchat.hook_print('Change Nick', ScanNickMsg)


def handleKickMsg(kicker, kickee, kickChan, kickMsg):
  #if bot got kicked
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


dontGetBannedCount = 0  #fixes an issue where the bot opens too many connections to the server and gets banned
def connectionCheck(userdata):
  global dontGetBannedCount
  if xchat.get_info('server') is None and dontGetBannedCount == 0:
    xchat.hook_timer(60000, initialization)  #wait 60 seconds to try reconnect
    dontGetBannedCount = 10
    return False
  dontGetBannedCount -= 1
  return True



# if bot isn't in a channel it should be in (has been kicked), it tries to join
def chanPresenceCheck(userdata):
  # also check if the name is correct
  if xchat.nickcmp(botName, xchat.get_info("nick")) != 0:
    xchat.command("nick %s" % botName)

  actualChanList = xchat.get_list('channels')
  chanList = db.listChans()
  for chan in chanList:
    if chan not in [x.channel for x in actualChanList]:
      xchat.command("join %s" % chan)
  return True
xchat.hook_timer(120000, chanPresenceCheck)  # every 2 minutes


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


# check for messages that should be delivered now
def checkForProxyMessage(nick, channel):
  newMessages = db.checkMessages(nick.lower(), channel)
  if newMessages != None:
    for newMsg in newMessages:
      xchat.command("msg %s %s" % (channel, newMsg))
      


def initialization(userdata):
  print ">>Initializing"
  
  # join server if not already connected
  if xchat.get_info('server') is None:
    xchat.command("server %s %s" % (serverName, portNum))
    
  # set nick
  xchat.command("nick %s" % botName)
  
  xchat.hook_timer(2000, identifyHook)
  xchat.hook_timer(4000, chanJoinHook)
  
  xchat.hook_timer(30000, connectionCheck)  # every 30 seconds
  
  return False
initialization(0)  #get called on first run
  
  
#1. bot may not injure a human being or, through inaction, allow a human being to come to harm.
#2. bot must obey the orders given to it by human beings, except where such orders would conflict with the First Law.
#3. bot must protect its own existence as long as such protection does not conflict with the First or Second Laws.
  