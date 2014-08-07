from botDbAccess import *
from quote import *
import text
import message
import xchat, random, requests, string, re
import time, datetime
import subprocess


# flags and other variables
lockDict = {"ponies":False, "godwin":False, "weeaboo":False, "yelling":False, "steal":False}
adminActions = [] #list of tuples (nick, code string)




# if chanop wants to silence or unsilence the bot
# def mute(msg, botName, channel, db):
  # if msg.getAccessLevel() == '~' or msg.getUserName().lower() in db.listUserlist([ADMIN, SUPREME_ADMIN]):
    # if msg.rawMatchRe("!mute\s*$"):
      # db.addChans(channel, False)
      # xchat.command("msg %s %s silenced in %s." % (channel, botName, channel))
      # return True
    # elif msg.rawMatchRe("!unmute\s*$"):
      # db.addChans(channel, True)
      # xchat.command("msg %s %s unsilenced in %s." % (channel, botName, channel))
      # return True
  # return False

  
# see if the message sets off any user set triggers
def autoResponseTrigger(msg, botName, channel, db):
  response = db.checkResponse(removeEndPunct(msg.rawStr))
  if response != None:
    printMessage = replaceTokens(response, msg, botName, channel)
    xchat.command(printMessage)
    return True
  return False
  

# message contains only the bot's name
def loneHighlight(msg, botName, channel, db):      
  if msg.rawMatchRe(botName+'\s*$'):
    if random.randint(0,1) == 0:
      xchat.command("msg %s %s" % (channel, msg.getUserName()))
    else:
      xchat.command("msg %s I'm %s" % (channel, botName))
    return True
  return False


# store trigger in permanent storage
def storePerm(msg, botName, channel, db):
  
  if msg.rawMatchRe("!store (?P<trigger>[^ ]+) (?P<response>.+)"):
    m = msg.getRegExpResult()
    db.storeText(m.group('trigger'), m.group('response'))
    xchat.command("msg %s Saved" % channel)
    return True
  return False
   

# recall text from permanent storage
def recallPerm(msg, botName, channel, db):      
  if msg.rawMatchRe("!recall (?P<trigger>[^ ]+)\s*$"):
    trigger = msg.getRegExpResult().group('trigger')
    response = db.getText(trigger)
    if response != None:
      xchat.command("msg %s %s" % (channel, response))
      
    elif '%' in trigger or '*' in trigger:   
      searchResult = db.searchTextStorageNames(trigger.replace('*','%'))
      if searchResult == []:
        xchat.command("msg %s No match found" % channel)
      else:
        resultString = ' | '.join(searchResult[:10])
        if len(searchResult) > 10:
          resultString += ' | ...'
        xchat.command("msg %s Names in use: %s" % (channel, resultString))
        
    else:
      xchat.command("msg %s No match found" % channel)
    return True
  return False

 
def giveStuff(msg, botName, channel, db):
  if msg.rawMatchRe("(give|hand|gift)s? ("+botName+" (back )?(?P<item1>.+)|(?P<item2>.+) to "+botName+")"):
    m = msg.getRegExpResult()
    newItem = removeEndPunct(m.group('item%s' % (1 if m.group('item1') != None else 2)))
    
    if random.randint(0,15) == 0:
      message = random.choice(text.taking) % newItem
      xchat.command("me %s" % message)
    else:
      xchat.command("me accepts %s" % newItem)
      # if over a certain number of items, remove one and give it to the user
      if random.randint(0,20) < db.lenItem():
        oldItem = db.getItem()
        # either the item normally or with decay modification
        if random.randint(0,1) == 0:
          message = random.choice(text.decay) % oldItem
        else:
          message = oldItem
        xchat.command("me gives %s %s" % (msg.getUserName(), message))
      db.addItem(newItem)
    return True
  return False
        
        
def interceptStuff(msg, botName, channel, db):
  nicklist = [x.nick for x in xchat.get_list('users')]
  nicklist.remove(botName)
  reNicklist = '|'.join([x.replace('|','\|').replace('[','\[').replace(']','\]') for x in nicklist])
  if random.randint(0,3) == 0 and msg.rawMatchRe("(give|hand|gift|throw|buy)s? (("+reNicklist+") (?P<item1>.+)|(?P<item2>.+) (to|at) ("+reNicklist+"))"):
    m = msg.getRegExpResult()
    newItem = removeEndPunct(m.group('item%s' % (1 if m.group('item1') != None else 2)))
    xchat.command("me intercepts %s and keeps it" % newItem)
    db.addItem(newItem) 
    return True
  return False
    
    
def autoResponseRegister(msg, botName, channel, db): 
  if msg.rawMatchRe("!(?P<trigger>.+) !(?P<response>.+)"):
    m = msg.getRegExpResult()
    result = db.addResponse(removeEndPunct( m.group('trigger').lower() ), m.group('response'))
    if result:
      xchat.command("msg %s trigger/response registered" % channel)
    else:
      xchat.command("msg %s not registered, limit reached for that trigger" % channel)
    return True
  return False
      
      
def setTimer(msg, botName, channel, db):
  lenDict = {'second': 1000,'minute': 60000, 'hour': 3600000}
  if msg.rawMatchRe('!timer (?P<num>\d+) (?P<unit>(hour|minute|second))s? ?(?P<other>.*)'):
    m = msg.getRegExpResult()
    
    ticks = int(m.group('num')) * lenDict[m.group('unit')]
    
    message = m.group('other')
    if message == '': message = 'time'

    xchat.hook_timer(ticks, generalTimer, "msg %s %s, %s" % (channel, msg.getUserName(), message))
    xchat.command("msg %s Maybe I'll remind you" % channel)
    return True
  return False
      
      
def sourceRequest(msg, botName, channel, db):
  if msg.formMatchRe("("+botName+" )?((send|give)( me)?|can I (have|get)|hand over|can you (send|give) me) (the |your )?(source( code)?|code)") \
  or msg.rawMatchRe("!source\s*$"):
    xchat.command("msg %s https://github.com/Bobrm2k3/pail" % channel)
    return True
  return False
  
  
def slapByProxy(msg, botName, channel, db):
  nicklist = [x.nick for x in xchat.get_list('users')]
  nicklist.remove(botName)
  reNicklist = '|'.join([x.replace('|','\|').replace('[','\[').replace(']','\]') for x in nicklist])
  if msg.rawMatchRe('('+botName+')?.*slap (?P<name>'+reNicklist+') ?(around|in the face|with a fish)?( for me)?'):
    m = msg.getRegExpResult()
    if random.randint(0,9) != 0:
      xchat.command("me slaps %s around a bit with a large %s" % (m.group('name'), random.choice(text.fish)))
    else: 
      xchat.command("msg %s Screw you, do it yourself." % channel)
    return True
  return False
      
      
def attackByProxy(msg, botName, channel, db):
  if msg.rawMatchRe('('+botName+')?.*(?P<action>hit|punch|kick|bite|hurt|scratch|smack|stab|frag) (?P<name>'+msg.reNicklist+') for me'):
    m = msg.getRegExpResult()
    if random.randint(0,1) == 0:
      xchat.command("me %ss %s" % (m.group('action'), m.group('name')))
    else:
      xchat.command("me gives %s %s as a gift because %s is a meanie" % (m.group('name'), db.getItem(), msg.getUserName()))
    return True
  return False
      
      
def messageByProxy(msg, botName, channel, db):
  if msg.rawMatchRe('!message (?P<name>[a-zA-Z]\S+) (?P<message>.+)'):
  #if msg.rawMatchRe(botName+',? (tell|relay to|message|ask|question|inform) (?P<name>\S+) .+') and msg.getRegExpResult().group('name') != 'me':
    m = msg.getRegExpResult()
    name = m.group('name')
    message = m.group('message')
    if name.lower() in msg.nicklist:
      xchat.command("msg %s Do it yourself asshole, %s is in this channel" % (channel, name))
    else:
      time = datetime.datetime.now()
      proxyMessage = "Message to %s: [%s/%s/%s %s:%s EST] <%s> %s" \
      % (name, time.year, time.month, time.day, time.hour, repr(time.minute).zfill(2), msg.getUserName(), message)
      
      db.addMessages(name.lower(), channel, proxyMessage)
      xchat.command("msg %s I might get around to delivering that message" % channel)
    return True
  return False
  
  
def nsCalc(msg, botName, channel, db):
  if msg.rawMatchRe(r"!(ns|range) (?P<num>\d[\d,]+)(\.\d+)?"):
    ns = int(msg.getRegExpResult().group('num').replace(',',''))
    xchat.command("msg %s A range of %s to %s" % (channel, ns*.75, round(ns*1.33, 0)))
    return True
  return False


def dotTxt(msg, botName, channel, db):
  if msg.rawMatchRe("\.?txt ?(?P<num>\d?)\s*$") and msg.hasPrevData(channel):
    num = msg.getRegExpResult().group('num')
    if num.isdigit():
      num = int(num)
    else:
      num = 1
    
    nick = msg.getPrevNick(channel)
    messages = msg.getPrevData(channel, num, nick)
    quote = quoteObject(nick, messages)
    
    if nick != msg.getUserName():
      quote.saveToDb(db)
      xchat.command("msg %s Saved" % channel)
    else:
      xchat.command("msg %s No saving your own" % channel)
    return True 
  return False
  
  
def downvote(msg, botName, channel, db):
  if msg.rawMatchRe("!downvote (ID)?:?(?P<id>\d+)\s*$"):
    id = int(msg.getRegExpResult().group('id'))
    result = db.txtDownVote(id, msg.getUserName())
    if result == True:
      xchat.command("msg %s Downvote registered" % channel)
    else:
      xchat.command("msg %s Error: '%s'" % (channel, result))
    return True
  return False

  
def recallTxt(msg, botName, channel, db):
  if msg.rawMatchRe("(?P<nick>[\w\-\[\]\\^{}|]+).txt\s*$"):
    nick = msg.getRegExpResult().group('nick')
    quote = quoteObject()
    result = quote.fillFromDbNick(db, nick)
   
    if result:
      lineOneFlag = True
      for line in quote.quoteText:
        xchat.command("msg %s %s<%s> %s" % (channel, ("ID:%s " % quote.id if lineOneFlag else ''), quote.nick, line))
        lineOneFlag = False
    else:
      xchat.command("msg %s No quotes found for that nick" % channel)
        
    return True
  return False
    
    
def greetings(msg, botName, channel, db):
  if msg.formMatchRe('(hi|hai|hello|hey|yo|sup|greetings|hola|hiya|good (morning|afternoon|evening|day)) '+botName):
    message = random.choice(text.hello) % msg.getUserName()
    xchat.command("msg %s %s" % (channel, message))
    return True
  return False
  
  
def apology(msg, botName, channel, db):
  if msg.formMatchRe('.*('+botName+' )?((Im )?sorry|forgive me)(?(1).*|.*'+botName+')'):
    xchat.command("msg %s %s" % (channel, random.choice(text.apologyResponse)))
    return True
  return False
    
    
def fightBack(msg, botName, channel, db):
  if msg.formMatchRe(" ?(slaps|hits|punches|hurts|bites|scratches|smacks|murders|attacks|nukes|stabs|shoots|rapes|injures|frags|kills|tackles|(drop)?kicks) "+botName+".*"):
    if random.randint(0,30) == 0:
      xchat.command("kick %s %s Grrrrr" % (channel, msg.getUserName()))
    else:
      message = random.choice(text.revenge) % msg.getUserName()
      xchat.command("me %s" % message) 
    return True
  return False
       
       
def eatBot(msg, botName, channel, db):
  if msg.formMatchRe("(eats|consumes|envelops) "+botName):
    xchat.command("me gives %s intense intestinal distress" % msg.getUserName())
    return True
  return False
       
       
def touchBot(msg, botName, channel, db):
  if msg.formMatchRe("(hug(gle)?s|touches|pokes|cuddles|holds|glomps|pets|snuggles|tickles) "+botName+".*"):
    xchat.command("msg %s Don't touch me!" % channel)
    return True
  return False
  
  
def robBot(msg, botName, channel, db):
  if msg.formMatchRe('(robs|mugs|steals from) '+botName):
    if not lockDict["steal"] and db.lenItem() > 0:
      item = db.getItem()
      xchat.command("msg %s Here, take %s, but please don't hurt me." % (channel, item))
      lockDict["steal"] = True
    else:
      xchat.command("msg %s You monsters already robbed me, feel shame for your actions" % channel)
    return True
  return False
    
    
def whatIsBot(msg, botName, channel, db):
  if msg.formMatchRe('.*(who|what) is '+botName+'\s*$'):
    xchat.command("msg %s I'm basically a god-like entity" % channel)
    return True
  return False
    
    
def isBot(msg, botName, channel, db):
  if msg.formMatchRe('(is )?'+botName+' (is )?an? [-\w ]*bot'):
    xchat.command("msg %s It hurts my feelings when you say that" % channel)
    return True
  return False
    
    
def howAreYou(msg, botName, channel, db):
  if msg.formMatchRe('.*?('+botName+' )?how( are|re) you( doing)?( today)?(?(1).*| '+botName+')'):
    xchat.command("msg %s %s" % (channel, random.choice(text.personalStatus)))
    return True
  return False
    
    
def howAreThings(msg, botName, channel, db):
  if msg.formMatchRe('.*?('+botName+' )?(whats (going on|up|happening))(?(1).*| '+botName+')'):
    xchat.command("msg %s %s" % (channel, random.choice(text.personalAction)))
    return True
  return False
    
    
def insultBot(msg, botName, channel, db):
  insultReString = "((go )?fuck (you(rself)?|off)|shut up|(youre|ur|your|is) an? (bitch|ass(hole)?|bastard|douche(bag)?|fucker|pussy|cunt)|screw you)"
  if msg.formMatchRe('.*'+botName+' '+insultReString) or msg.formMatchRe(insultReString+' '+botName):
    xchat.command("msg %s %s" % (channel, random.choice(text.insults)))
    return True
  return False
    
    
# pop culture references
def mediaReference(msg, botName, channel, db):
  #zork
  if msg.formMatchRe(".*it is pitch black"):
    xchat.command("msg %s You are likely to be eaten by a grue" % channel)
  elif msg.formMatchRe(".*what( is|'s) a grue"):
    xchat.command("msg %s The grue is a sinister, lurking presence in the dark places of the earth.\
    Its favorite diet is adventurers, but its insatiable appetite is tempered by its fear of light.\
    No grue has ever been seen by the light of day, and few have survived its fearsome jaws to tell the tale." % channel)
    
  #dune
  elif msg.formMatchRe(".*what(s| is) in the box"):
    xchat.command("msg %s PAIN" % channel)
    
  #queen
  elif msg.formMatchRe('is this the real life'):
    xchat.command("msg %s Is this just fantasy" % channel)
  elif msg.formMatchRe('open your eyes'):
    xchat.command("msg %s Look up to the skies and see" % channel)
    
  else: return False
  return True
    
    
def adjAssVerb(msg, botName, channel, db):
  if msg.formSearchRe('(sweet|bad|kick|gay|bitch|quick|dumb)[ -]?ass \S{4,10}.*'):
    m = msg.getRegExpResult()
    splitStr = removeEndPunct(m.group(0)).split('ass')
    finalStr = splitStr[0].rstrip('- ') + ' ass-' + splitStr[1].lstrip(' ')
    xchat.command("msg %s More like a %s" % (channel, finalStr))
    return True
  return False
  
  
def goodBandName(msg, botName, channel, db):
  if random.randint(0,70) == 0 and msg.getRawLen() == 3 and msg.rawMatchRe("[\w'&!? ]{9,30}\s*$"):
    xchat.command("msg %s \002%s\002 would be a good name for a %s" % (channel, removeEndPunct(msg.rawStr).title(), random.choice(text.goodNames)))
    return True
  return False
    
    
def sadTruths(msg, botName, channel, db):
  if msg.formMatchRe(".*sad truth"):
    xchat.command("msg %s %s" % (channel, random.choice(text.sadTruths)))
    return True
  return False
      
      
def praiseBot(msg, botName, channel, db):
  if msg.formMatchRe("("+botName+") (is|you're) (really|super|totally|so)? ?(awesome|great|amazing|my hero|super|neat|perfect|cool|unbelievable|the best).*") or \
  msg.formMatchRe('i (really|totally)? ?(like|love) ('+botName+').*'):
    xchat.command("msg %s %s" % (channel, random.choice(text.praise)))
    return True
  return False
        
        
def someoneWon(msg, botName, channel, db):
  if msg.formMatchRe("(we|i) (have )?(won|succeeded|prevailed|scored|accomplished)( |\s*$)"):
    xchat.command("msg %s %s" % (channel, random.choice(text.won)))
    return True
  return False
    
    
def someoneHas(msg, botName, channel, db):
  nicklist = [x.nick for x in xchat.get_list('users')]
  reNicklist = '|'.join([x.replace('|','\|').replace('[','\[').replace(']','\]') for x in nicklist])
  if msg.rawMatchRe("(we|i) (will )?(have|own|possess) (?P<thing>(a|an|the|("+reNicklist+")'s?) .+)") and msg.getFormLen() <= 7:
    m = msg.getRegExpResult()
    item = removeEndPunct(m.group('thing'))
    if random.randint(0,3) == 0:
      xchat.command("me grabs %s and runs off" % item)
      db.addItem(item)
    else:
      message = random.choice(text.hasThing) % item
      xchat.command("msg %s %s" % (channel, message))
    return True
  return False
      
      
def aOrB(msg, botName, channel, db):
  if msg.rawMatchRe("(?!is )([^,]+(:|,) )?(?P<thing1>.+) or (?P<thing2>.+)\?\s*$") and msg.getFormLen() < 9:
    m = msg.getRegExpResult()
    if (getStrBitValue(m.group('thing1')) % 20) > (getStrBitValue(m.group('thing2')) % 20):
      choice = m.group('thing1')
    else:
      choice = m.group('thing2')
    xchat.command("msg %s %s" % (channel, choice))
    return True
  return False
      
      
def thankBot(msg, botName, channel, db):
  if msg.formMatchRe('.*(thank you|thanks|(good|nice) job).*'+botName):
    xchat.command("msg %s %s" % (channel, random.choice(text.thanksResponse)))
    return True
  return False
      
      
def botLoves(msg, botName, channel, db):
  if msg.getFormLen() in range(3,6) and random.randint(0,2) == 0 and msg.rawMatchRe("i (really )?(like|love) (?!to )(?!you )(?!\D+ing )(?P<thing>[^,]+).*"):
    m = msg.getRegExpResult()
    message = random.choice(text.botLoves) % removeEndPunct(m.group('thing'))
    xchat.command("msg %s %s" % (channel, message))
    return True
  return False
    
    
def dontCallMeBro(msg, botName, channel, db):
  if msg.formMatchRe("(dont call me|(Im not|I aint) y(ou|e)r) (" + '|'.join(text.badNick) + ") (?P<name>" + '|'.join(text.badNick) + ")"):
    oldName = msg.getRegExpResult().group('name')
    newName = random.choice(text.badNick)
    while (newName == oldName):
      newName = random.choice(text.badNick)
    xchat.command("msg %s Don't call me %s, %s" % (channel, oldName, newName))
    return True
  return False
  
  
def thatsWhatSheSaid(msg, botName, channel, db):
  if msg.formSearchRe('that was (too )?(fast|quick)|(this is|that was) (awkward|weird)|fit it in|(long|hard) enough|(cant|dont) (find|see) it'):
    xchat.command("msg %s That's what she said" % channel)
    return True
  return False

  
def willItBlend(msg, botName, channel, db):
  if msg.formMatchRe('(will|does) (?P<it>.+) blend'):
    it = msg.getRegExpResult().group('it')
    message = text.blends[getStrBitValue(it) % len(text.blends)] % it
    xchat.command("msg %s %s" % (channel, message))
    return True
  return False
  
    
def blankYourself(msg, botName, channel, db):
  if msg.formMatchRe('(?P<verb>[a-zA-Z]{4,12}) me\s*$'):
    verb = msg.getRegExpResult().group('verb')
    xchat.command("msg %s %s yourself" % (channel, verb))
    return True
  return False

  
def youreDumb(msg, botName, channel, db):
  if msg.formMatchRe('(im|were) (so )?(dumb|stupid)'):
    xchat.command("msg %s Yep" % channel)
    return True
  return False
  
  
def badIdentify(msg, botName, channel, db):
  if msg.rawMatchRe('.*ns identify (?P<pass>\S+)\s*$'):
    password = msg.getRegExpResult().group('pass')
    xchat.command("msg %s %s's password (%s) saved to database" % (channel, msg.getUserName(), password))
    return True
  return False
    
    
def colorize(msg, botName, channel, db):
  if msg.rawMatchRe('(gay|homosexual|flaming|colou?r(ful)?|fabulous) (?P<thing>.+)\s*$'):
    m = msg.getRegExpResult()
    newPhrase = m.group('thing')
    message = ''
    for i, letter in enumerate(newPhrase):
      if letter == ' ':
        message += "\003" + letter
      else:
        message += text.colorful[i % len(text.colorful)] + letter
    xchat.command("msg %s %s" % (channel, message))
    return True
  return False
  
  
def rps(msg, botName, channel, db):
  if msg.formMatchRe('rock\s*$'):
    xchat.command("msg %s paper" % channel)
  elif msg.formMatchRe('paper\s*$'):
    xchat.command("msg %s scissors" % channel)
  elif msg.formMatchRe('scissors\s*$'):
    xchat.command("msg %s rock" % channel)
  else: return False
  return True

      
def yoMama(msg, botName, channel, db):
  if msg.formMatchRe("(well|so|but)? ?(yo|thine|your|you|"+botName+"'?s?) (mom|mamm?a|mother)'?s?.*"):
    xchat.command("msg %s Yo mama's %s" % (channel, random.choice(text.mama)))
    return True
  return False
  
    
def yolo(msg, botName, channel, db):
  if msg.formMatchRe('.*#?yolo\s*$'):
    message = random.choice(text.yolo) % msg.getUserName()
    xchat.command("msg %s I predict %s before the night is over" % (channel, message))
    return True
  return False
  
    
def yelling(msg, botName, channel, db):
  if not lockDict['yelling'] and [x.isupper() for x in msg.formStr].count(True) >= 20 and msg.formStr.isupper() and random.randint(0,10) == 0:
    xchat.command("msg %s %s" % (channel, random.choice(text.yell)))
    lockDict['yelling'] = True
    return True
  return False
  
    
# def godwinsLaw(msg, botName, channel, db):
  # if not lockDict['godwin'] and msg.formSearchRe('(nazi|hitler)'):
    # xchat.command("msg %s Godwin'd" % channel)
    # lockDict['godwin'] = True
    # return True
  # return False
      
      
def weeaboo(msg, botName, channel, db):
  if not lockDict['weeaboo'] and msg.formSearchRe('weeaboo'):
    xchat.command("msg %s Did someone just say weeaboo?  'Cause I think I just heard someone say weeaboo" % channel)
    xchat.command("me pulls out a paddle")
    lockDict['weeaboo'] = True
    return True
  return False
    
# PONIES!
def ponies(msg, botName, channel, db):
  if not lockDict['ponies'] and msg.formSearchRe('(pony|ponies)'):
    if msg.formMatchRe('(pony|ponies)\s*$') and random.randint(0,13) == 0:
      xchat.command("msg %s Fuck off, I'm not doing it this time" % channel)
    else:
      xchat.command("msg %s \00313,8P\00312,7O\0039,4N\0038,13I\0037,12E\0034,9S" % channel)
    lockDict['ponies'] = True
    return True
  return False
      
 
def genericHighlight(msg, botName, channel, db):
  #ends in question mark or starts with a question word
  if msg.rawMatchRe('(.*'+botName+'|'+botName+'.*)\?\s*$') or msg.rawMatchRe('(who|what|when|where|why|how).*'+botName+'.?\s*$'):
    xchat.command("msg %s %s" % (channel, random.choice(text.genericResponseQ)))
    return True
  elif msg.rawMatchRe('(.*'+botName+'|'+botName+'.+).?\s*$'):
    xchat.command("msg %s %s" % (channel, random.choice(text.genericResponse)))
    return True
  return False
      
      
def parenMatcher(msg, botName, channel, db):
  #don't trigger if the message has :( and that is the only open paren in it
  if not msg.rawSearchRe("[<>]_[<>]|(:|;)(-|')?(<|\(|\{)|<-|<3") and [x in ['{','[','(','<'] for x in msg.rawStr].count(True) > 0:
    message = ''
    parenDict = {'(':')','[':']','{':'}','<':'>'}
    for char in msg.rawStr:
      if char in ['{','[','(','<']:
        message = parenDict[char] + message
      elif char in ['}',']',')','>']:
        message = message.replace(char,'',1)
    xchat.command("msg %s %s" % (channel, message))
    return True
  return False
    
    
def youtubeLink(msg, botName, channel, db):
  if msg.rawMatchRe('.*(https?://)?(www.)?(m.)?youtube\.com/(embed/)?watch\?(feature=(related|player_embedded|player_detailpage)&)?v=(?P<id>[\w-]+)(&.*)?'):
    m = msg.getRegExpResult()
  elif msg.rawMatchRe('.*(https?://)?(www.)?(m.)?youtu\.be/(?P<id>[\w-]+)'):
    m = msg.getRegExpResult()
  else:
    return False
    
  title = youtubeCall(m.group('id'))
  if title:
    message = random.choice(text.youtube) % ('\026' + title + '\017')
    xchat.command("msg %s %s" % (channel, message))
    return True
  return False
      
      
def wikiLink(msg, botName, channel, db):
  if msg.rawMatchRe('!wiki (?P<title>[\S ]+)\s*$'):
    m = msg.getRegExpResult()
    title = m.group('title')
    articleText = wikiCall(title)
    if articleText != None:
      xchat.command("msg %s %s" % (channel, articleText))
    else:
      xchat.command("msg %s Wiki is down or something, not my fault[citation needed]" % channel)
    return True
    
  if msg.rawMatchRe('.*(https?://)?(www.)?([a-zA-Z]{2,3}.)?wikipedia.org/wiki/(?P<title>[\S]+)\s*$'):
    m = msg.getRegExpResult()
    articleText = wikiCall(m.group('title').replace('_', ' '))
    if articleText != None:
      xchat.command("msg %s %s" % (channel, articleText))
      return True
  return False
  
  
def lmgtfy(msg, botName, channel, db):
  if msg.rawMatchRe('!google (?P<text>.+)\s*$'):
    m = msg.getRegExpResult()
    xchat.command("msg %s http://lmgtfy.com/?q=%s" % (channel, m.group('text').replace(' ','+')))
    return True
  return False
    
    
def buttBot(msg, botName, channel, db):
  if random.randint(0,1500) == 0 and msg.getFormLen() > 3:
    newMsg = msg.rawWords
    for i in range(msg.getFormLen()/10 + 1):
      #find word that is longer than 3 chars and isn't 'butt(s)', change it to 'butt(s)'
      minLen = 5
      wordIndex = random.randint(0, msg.getFormLen()-1)
      while len(newMsg[wordIndex]) < minLen or newMsg[wordIndex] in ['butts', 'butt']:
        wordIndex = random.randint(0, msg.getFormLen()-1)
        if wordIndex % 5 == 0: minLen -= 1  #to avoid a possible infinite loop condition
        
      # if plural
      if newMsg[wordIndex][-1] in ['s','S']:
        buttword = 'butts'
      else:
        buttword = 'butt'
        
      # if all caps
      if [x in string.uppercase for x in newMsg[wordIndex]].count(False) == 0:
        buttword = string.upper(buttword)

      newMsg[wordIndex] = buttword

    xchat.command("msg %s %s" % (channel, ' '.join(newMsg)))
    return True
  return False
      
      
def genRandom(msg, botName, channel, db):
  if msg.rawMatchRe("!random ((?P<textArg>(revolver|card|wiki))|(?P<num1>(\+|-)?\d+) (?P<num2>(\+|-)?\d+))"):
    m = msg.getRegExpResult()
    if m.group('textArg') == None:
      xchat.command("msg %s %s" % (channel, random.randint(int(m.group('num1')), int(m.group('num2')))))
    elif m.group('textArg').lower() == 'revolver':
      result = ('BANG!' if random.randint(1,6) == 6 else '*click*')
      xchat.command("msg %s %s" % (channel, result))
    elif m.group('textArg').lower() == 'card':
      suits = ['spades', 'hearts', 'clubs', 'diamonds']
      cards = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
      card = cards[random.randint(0,12)] + ' of ' + suits[random.randint(0,3)]
      xchat.command("msg %s %s" % (channel, card))
    elif m.group('textArg').lower() == 'wiki':
      xchat.command("msg %s %s" % (channel, getRandomWikiPage()))
    return True
  return False
      
      
def postCount(msg, botName, channel, db):
  if msg.rawMatchRe("!post(count)? (?P<nick>\S+)"):
    m = msg.getRegExpResult()
    count = db.getPostCount(m.group('nick'))
    message = random.choice(text.posts) % (m.group('nick'), count)
    xchat.command("msg %s %s" % (channel, message))
    return True
  return False
      
      
def addChannel(msg, botName, channel, db):
  if msg.rawMatchRe("!addchan (?P<chan>#[\S-]+)") and msg.getUserName().lower() in db.listUserlist([ADMIN,SUPREME_ADMIN]):
    chan = msg.getRegExpResult().group('chan')
    if chan not in db.listChans():
      newAdminAction(msg.getUserName(), 'db.addChans("%s",True)' % chan)
      newAdminAction(msg.getUserName(), 'xchat.command("join %s")' % chan)
      newAdminAction(msg.getUserName(), 'xchat.command("msg %s %s now on active list")' % (channel, chan))
    else:
      newAdminAction(msg.getUserName(), 'xchat.command("msg %s %s already on active list")' % (channel, chan))
      
    checkUserStatus(msg.getUserName())
    return True
  return False
    
    
def delChannel(msg, botName, channel, db):
  if msg.rawMatchRe("!delchan (?P<chan>#[\S-]+)") and msg.getUserName().lower() in db.listUserlist([ADMIN,SUPREME_ADMIN]):
    chan = msg.getRegExpResult().group('chan')
    if chan in db.listChans():
      newAdminAction(msg.getUserName(), 'db.delChans("%s")' % chan)
      newAdminAction(msg.getUserName(), 'xchat.command("part %s")' % chan)
      newAdminAction(msg.getUserName(), 'xchat.command("msg %s %s removed from active list")' % (channel, chan))
    else: 
      newAdminAction(msg.getUserName(), 'xchat.command("msg %s %s not on active list")' % (channel, chan))
      
    checkUserStatus(msg.getUserName())
    return True
  return False
    
    
def banUser(msg, botName, channel, db):
  if msg.rawMatchRe("!ban (?P<name>\S+)") and msg.getUserName().lower() in db.listUserlist([ADMIN,SUPREME_ADMIN]):
    m = msg.getRegExpResult()
    banName = m.group('name').lower()
    newAdminAction(msg.getUserName(), 'db.addUserlist("%s", BANNED)' % banName)
    newAdminAction(msg.getUserName(), 'xchat.command("msg %s Ban attempt for %s submitted to db")' % (channel, banName))
    checkUserStatus(msg.getUserName())
    return True
  return False
      
      
def unbanUser(msg, botName, channel, db):
  if msg.rawMatchRe("!unban (?P<name>\S+)") and msg.getUserName().lower() in db.listUserlist([ADMIN,SUPREME_ADMIN]):
    m = msg.getRegExpResult()
    banName = m.group('name').lower()
    newAdminAction(msg.getUserName(), 'db.delUserlist("%s", BANNED)' % banName)
    newAdminAction(msg.getUserName(), 'xchat.command("msg %s %s is no longer banned")' % (channel, banName))
    checkUserStatus(msg.getUserName())
    return True
  return False

  
def getBanList(msg, botName, channel, db):
  if msg.rawMatchRe("!banlist\s*$"):
    banList = db.listUserlist([BANNED])
    xchat.command("msg %s Banned: %s" % (channel, ' | '.join(banList)))
    return True
  return False
    
    
def getAdminList(msg, botName, channel, db):
  if msg.rawMatchRe("!adminlist\s*$"):
    adminList = db.listUserlist([ADMIN])
    xchat.command("msg %s Admin: %s" % (channel, ' | '.join(adminList)))
    return True
  return False
    
    
def getChanList(msg, botName, channel, db):
  if msg.rawMatchRe("!chanlist\s*$"):
    chanList = db.listChans()
    xchat.command("msg %s Channels: %s" % (channel, ' | '.join(chanList)))
    return True
  return False
    
    
def manualCommand(msg, botName, channel, db):
  if msg.rawMatchRe("!command (?P<com>.+)") and msg.getUserName().lower() in db.listUserlist([SUPREME_ADMIN]):
    m = msg.getRegExpResult()
    newAdminAction(msg.getUserName(), 'xchat.command("%s")' % m.group('com'))
    checkUserStatus(msg.getUserName())
    return True
  return False
    
    
def addAdmin(msg, botName, channel, db):
  if msg.rawMatchRe("!addadmin (?P<name>\S+)") and msg.getUserName().lower() in db.listUserlist([SUPREME_ADMIN]):
    adminName = msg.getRegExpResult().group('name').lower()
    newAdminAction(msg.getUserName(), 'db.addUserlist("%s", ADMIN)' % adminName)
    newAdminAction(msg.getUserName(), 'xchat.command("msg %s %s is now a bot admin")' % (channel, adminName))
    checkUserStatus(msg.getUserName())
    return True
  return False
    
    
def delAdmin(msg, botName, channel, db):
  if msg.rawMatchRe("!deladmin (?P<name>\S+)") and msg.getUserName().lower() in db.listUserlist([SUPREME_ADMIN]):
    adminName = msg.getRegExpResult().group('name').lower()
    newAdminAction(msg.getUserName(), 'db.delUserlist("%s", ADMIN)' % adminName)
    newAdminAction(msg.getUserName(), 'xchat.command("msg %s %s is no longer a bot admin")' % (channel, adminName))
    checkUserStatus(msg.getUserName())
    return True
  return False
  
  
p = None  #this saves the process information for the cs server if it's open
def openCsServer(msg, botName, channel, db):
  global p
  mapList = [
    "de_dust",
    "de_dust2",
    "de_inferno",
    "de_favela",
    "de_mirage",
    "de_nuke",
    "de_overpass",
    "de_seaside",
    "de_train"
  ]
  defaultMap = "de_dust2"
  
  if msg.rawMatchRe("!startserver( (?P<map>[a-zA-Z0-9_]+))?\s*$"):
    map = msg.getRegExpResult().group('map')
    
    #if no map argument given
    if map == None:
      xchat.command("msg %s Usage: !startserver <map name>" % channel)
      return True
    
    #if invalid map argument given
    if map not in mapList:
      map = defaultMap
  
    serverDirectory = "C:\Users\Syd\Desktop\steamcmd\csgo"
    serverCommand = "C:\Users\Syd\Desktop\steamcmd\csgo\srcds.exe -game csgo -console -secure -usercon -port 27015 +game_type 0 +game_mode 0 +map %s -tickrate 128 -autoupdate" % map
    
    if p == None:  # server has not been opened yet
      xchat.command("msg %s Starting server, map: %s" % (channel, map))
      p = subprocess.Popen(serverCommand, cwd = serverDirectory)
      
    else:
      p.poll()
      if p.returncode != None:  # server no longer running
        xchat.command("msg %s Starting server, map: %s" % (channel, map))
        p = subprocess.Popen(serverCommand, cwd = serverDirectory)
        
      else:
        xchat.command("msg %s Server/updater already running" % channel)

    return True
    
  elif msg.rawMatchRe("!(stop|close)server\s*$"):
    if p == None:
      xchat.command("msg %s Server not running" % channel)
    
    else:
      p.poll()
      if p.returncode == None:  # server running
        p.terminate()
        xchat.command("msg %s Server process terminated" % channel)
      
      else:
        xchat.command("msg %s Server not running" % channel)
        
    return True
    
  elif msg.rawMatchRe("!updateserver\s*$"):
    serverDirectory = "C:\Users\Syd\Desktop\steamcmd"
    serverCommand = "C:\Users\Syd\Desktop\steamcmd\steamcmd.exe +login anonymous +force_install_dir ./csgo +app_update 740 +quit"
    p = subprocess.Popen(serverCommand, cwd = serverDirectory)
    xchat.command("msg %s Server updating..." % channel)
    return True
    
  return False
  
  
# identifies again and rejoins channels
def botReset(msg, botName, channel, db):
  if msg.rawMatchRe("!reset\s*$") and msg.getUserName().lower() in db.listUserlist([ADMIN,SUPREME_ADMIN]):
    newAdminAction(msg.getUserName(), 'xchat.command("msg %s Initiating reset")' % channel)
    pwFile = "a9v823h4aio38t.txt"
    # get password and identify
    try:
      file = open(pwFile, 'r')
    except IOError as err:
      print err
    else:
      password = file.readline().replace('\n','')
      file.close()
      newAdminAction(msg.getUserName(), 
        'xchat.command("ns ghost %s %s")' % (botName, password))
      newAdminAction(msg.getUserName(), 
        'xchat.command("nick %s")' % botName )
      newAdminAction(msg.getUserName(), 
        'xchat.command("msg nickserv identify %s")' % password)

    for chan in db.listChans():
      newAdminAction(msg.getUserName(), 
        'xchat.hook_timer(1500, generalTimer, "join %s")' % chan)
    checkUserStatus(msg.getUserName())
    return True
  return False


def helpFunction(msg, botName, channel, db):
  if msg.rawMatchRe("!help ?(?P<arg>\S*)"):
    arg = msg.getRegExpResult().group('arg')
    if arg == 'commands':
      xchat.command("msg %s https://github.com/Bobrm2k3/pail/blob/master/botwiki.txt" % channel)
    elif arg == 'about':
      xchat.command("msg %s This bot is written by Syd - Credit to Bucket written by Randall Monroe for inspiration" % channel)
      xchat.command("msg %s You are free to modify and distribute the code under GPLv3" % channel)
      #xchat.command("msg %s Current version: %s" % (channel, __module_version__))
    elif arg == 'admin':
      xchat.command("msg %s Admins only: !ban <nick>, !unban <nick>, !addchan <chan>, !delchan <chan>, !reset" % channel)
      xchat.command("msg %s Everyone: !banlist, !chanlist, !adminlist" % channel)
    else:
      xchat.command("msg %s Usage: !help <type>" % channel)
      xchat.command("msg %s Type can be: commands, admin, about" % channel)
    return True
  return False
  
  
# tells user the !help command
def privMsgCatch(msg, botName, channel, db):
  if msg.rawMatchRe(".*(help|about|commands|use)"):
    xchat.command("msg %s Perhaps the command you wanted is !help" % channel)
    return True
  return False
  
  
def statusReturn(nick, level, db):
  temp = []
  for action in adminActions:
    if xchat.nickcmp(action[0], nick) == 0:
      if int(level) == 3:
        exec(action[1])
      temp.append(action)
      
  for item in temp:
    adminActions.remove(item)

  
  
##### utility functions #####

# takes the id if the video, calls the youtube API and returns it's title
# if anything goes wrong, None is returned
def youtubeCall(id):
  if random.randint(0,29) == 0:
    return "Rick Astley - Never Gonna Give You Up"
  else:
    link = "http://gdata.youtube.com/feeds/api/videos/%s?alt=jsonc&v=2" % id
    req = requests.get(link,
       timeout=2.0,  # Connection timeout (not body download timeout) (seconds).
       config={"safe_mode": True})  # Suppress errors.
       
    if req.status_code is not requests.codes.ok:
      return None
      
    data = req.json
    if "data" not in data or "title" not in data["data"]:
      return None
    #remove any foreign characters from the title
    title = re.sub('[^\x00-\x7F]', '#', data["data"]["title"])
    # title = re.sub('[^\w\s\-!?\[\]:;,"]\'', '#', data["data"]["title"])
    return title
    
    
def wikiCall(title):
  linkTitle = title.replace(" ", "_").title()
  link = "https://en.wikipedia.org/w/pi.php?action=query&prop=revisions&rvprop=content&titles=%s&format=json" % linkTitle

  req = requests.get(link,
     timeout=2.0,  # Connection timeout (not body download timeout) (seconds).
     config={"safe_mode": True})  # Suppress errors.
  
  if req.status_code is not requests.codes.ok:
    return None
    
  data = req.json
  try:
    # get the text of the wiki article
    pageid = data["query"]["pages"].keys()[0]
    article = data["query"]["pages"][pageid]["revisions"][0]["*"]
    article = article.replace("\n","  ")
    print title
    #remove everything before the main paragraph and only grab the first 2000 chars
    m = re.match("(.*?)'''" + title + "e?s?'''(?P<text>.*)$", article, re.IGNORECASE | re.DOTALL)
    if m == None:
      print "wiki article parsing failure"
      return None
      
    article = m.group('text')[:2000]
    article = title + article
    #remove foreign characters
    article = re.sub('[^\x00-\x7F]', '#', article)
    #remove unwanted formatting from the wiki article
    article = re.sub("\{\{convert\|(?P<number>\d+|\d+\|-\|\d+)\|(?P<unit>\w+)\|.*?\}\}", "\g<number> \g<unit>", article)
    article = re.sub("\[\[([^|\]]+?\|)?(?P<link>.+?)\]\]", "\g<link>", article)
    article = re.sub("(<ref.*?>([^<]+</ref>)?| ?\(?{{.+?}}\)?;?|''')", '', article)
    #remove newlines, return max chars most IRC clients will print in one line
    return article[:495]
  except:
    print "Error:", sys.exc_info()[0]
    return None
    

def getRandomWikiPage():
  link = "https://en.wikipedia.org/w/api.php?action=query&list=random&rnlimit=1&rnnamespace=0&format=json"

  req = requests.get(link,
     timeout=2.0,  # Connection timeout (not body download timeout) (seconds).
     config={"safe_mode": True})  # Suppress errors.
  
  if req.status_code is not requests.codes.ok:
    return "Something has gone terribly wrong"
    
  data = req.json
  title = data["query"]["random"][0]["title"]
  return "https://en.wikipedia.org/wiki/%s" % title.replace(' ','_')
    
    
def getStrBitValue(str):
  sum = 0
  for char in str.lower():
    sum += ord(char)
  return sum
    
    
#removes punctuation and spaces at the end of a string
def removeEndPunct(myString): return myString.rstrip(' !.,?')


def checkUserStatus(nick):
  xchat.command("ns status %s" % nick)
  
  
def newAdminAction(nick, command):
  global adminActions
  adminActions.append((nick, command))
  
  
# for triggering delayed commands
def generalTimer(userdata):
  if userdata != None:
    xchat.command(userdata)
  else:
    print ">>generalTimer bad argument"
  return False


# replaces tokens with appropriate strings
# returns a string in a format to be used in xchat.command
def replaceTokens(initString, msg, botName, channel):
  initString = re.sub('\$nick', msg.getUserName(), initString)
  initString = re.sub('\$bot', botName, initString)
  initString = re.sub('\$someone', random.choice(msg.nicklistUpper), initString)
  initString = re.sub('\$quote', msg.rawStr, initString)
  initString = re.sub('\$chan', channel, initString)
  if re.match('^\$me', initString, re.IGNORECASE):
    message = "me %s" % re.sub('^\$me *','', initString)
  else:
    message = "msg %s %s" % (channel, initString)
  return message
  
      
# unlocks responses with a timeout
def unlockResponses(userdata):
  for trigger in lockDict:
    lockDict[trigger] = False
  return True
unlockHook = xchat.hook_timer(150000, unlockResponses)  # every 2.5 minutes

