from botDbAccess import *
import text
import message
import hexchat, random, requests, string, re
import time, datetime
import subprocess
from pymarkovchain import MarkovChain


# flags and other variables
lockDict = {"ponies":False, "yelling":False, "steal":False}
adminActions = [] #list of tuples (nick, code string)
sourceLocation = "https://github.com/Bobrm2k3/pail"
helpDocLocation = "https://github.com/Bobrm2k3/pail/blob/master/botwiki.txt"


  
# see if the message sets off any user set triggers
def autoResponseTrigger(msg, botName, channel, db):
  response = db.checkResponse(removeEndPunct(msg.rawStr))
  if response != None:
    printMessage = replaceTokens(response, msg, botName, channel)
    hexchat.command(printMessage)
    return True
  return False
  

# message contains only the bot's name
def loneHighlight(msg, botName, channel, db):      
  if msg.rawMatchRe(botName+'\s*$'):
    if random.randint(0,1) == 0:
      hexchat.command("msg %s %s" % (channel, msg.getUserName()))
    else:
      hexchat.command("msg %s I'm %s" % (channel, botName))
    return True
  return False


# store trigger in permanent storage
def storePerm(msg, botName, channel, db):
  if msg.rawMatchRe("!store (?P<trigger>[^ ]+) (?P<response>.+)"):
    m = msg.getRegExpResult()
    db.storeText(m.group('trigger'), m.group('response'))
    hexchat.command("msg %s Saved" % channel)
    return True
  return False
   

# recall text from permanent storage
def recallPerm(msg, botName, channel, db):      
  if msg.rawMatchRe("!recall (?P<trigger>[^ ]+)\s*$"):
    trigger = msg.getRegExpResult().group('trigger')
    response = db.getText(trigger)
    if response != None:
      hexchat.command("msg %s %s" % (channel, response))
      
    elif '%' in trigger or '*' in trigger:   
      searchResult = db.searchTextStorageNames(trigger.replace('*','%'))
      if searchResult == []:
        hexchat.command("msg %s No match found" % channel)
      else:
        resultString = ' | '.join(searchResult[:10])
        if len(searchResult) > 10:
          resultString += ' | ...'
        hexchat.command("msg %s Names in use: %s" % (channel, resultString))
        
    else:
      hexchat.command("msg %s No match found" % channel)
    return True
  return False

 
def giveStuff(msg, botName, channel, db):
  if msg.rawMatchRe("(give|hand|gift)s? ("+botName+" (back )?(?P<item1>.+)|(?P<item2>.+) to "+botName+")"):
    m = msg.getRegExpResult()
    newItem = removeEndPunct(m.group('item%s' % (1 if m.group('item1') != None else 2)))
    
    if random.randint(0,15) == 0:
      message = random.choice(text.taking) % newItem
      hexchat.command("me %s" % message)
    else:
      hexchat.command("me accepts %s" % newItem)
      # if over a certain number of items, remove one and give it to the user
      if random.randint(0,20) < db.lenItem():
        oldItem = db.getItem()
        # either the item normally or with decay modification
        if random.randint(0,1) == 0:
          message = random.choice(text.decay) % oldItem
        else:
          message = oldItem
        hexchat.command("me gives %s %s" % (msg.getUserName(), message))
      db.addItem(newItem)
    return True
  return False
        
        
def interceptStuff(msg, botName, channel, db):
  nicklist = [x.nick for x in hexchat.get_list('users')]
  #nicklist.remove(botName)
  reNicklist = '|'.join([x.replace('|','\|').replace('[','\[').replace(']','\]') for x in nicklist])
  if random.randint(0,3) == 0 and msg.rawMatchRe("(give|hand|gift|throw|buy)s? (("+reNicklist+") (?P<item1>.+)|(?P<item2>.+) (to|at) ("+reNicklist+"))"):
    m = msg.getRegExpResult()
    newItem = removeEndPunct(m.group('item%s' % (1 if m.group('item1') != None else 2)))
    hexchat.command("me intercepts %s and keeps it" % newItem)
    db.addItem(newItem) 
    return True
  return False
    
    
def autoResponseRegister(msg, botName, channel, db): 
  if msg.rawMatchRe("!(?P<trigger>.+) !(?P<response>.+)"):
    m = msg.getRegExpResult()
    result = db.addResponse(removeEndPunct( m.group('trigger').lower() ), m.group('response'))
    if result:
      hexchat.command("msg %s trigger/response registered" % channel)
    else:
      hexchat.command("msg %s not registered, limit reached for that trigger" % channel)
    return True
  return False
      
      
def setTimer(msg, botName, channel, db):
  lenDict = {'second': 1000,'minute': 60000, 'hour': 3600000}
  if msg.rawMatchRe('!timer (?P<num>\d+) (?P<unit>(hour|minute|second))s? ?(?P<other>.*)'):
    m = msg.getRegExpResult()
    
    ticks = int(m.group('num')) * lenDict[m.group('unit')]
    if ticks > 36000000:
      hexchat.command("msg %s That's way too much number to count to" % channel)
      return True
    
    message = m.group('other')
    if message == '': message = 'time'

    hexchat.hook_timer(ticks, generalTimer, "msg %s %s, %s" % (channel, msg.getUserName(), message))
    hexchat.command("msg %s Maybe I'll remind you" % channel)
    return True
  return False
      
      
def sourceRequest(msg, botName, channel, db):
  if msg.rawMatchRe("!source\s*$"):
    hexchat.command("msg %s %s" % (channel, sourceLocation))
    return True
  return False
  
  
def slapByProxy(msg, botName, channel, db):
  nicklist = [x.nick for x in hexchat.get_list('users')]
  #nicklist.remove(botName)
  reNicklist = '|'.join([x.replace('|','\|').replace('[','\[').replace(']','\]') for x in nicklist])
  if msg.rawMatchRe('('+botName+')?.*slap (?P<name>'+reNicklist+') ?(around|in the face|with a fish)?( for me)?'):
    m = msg.getRegExpResult()
    if random.randint(0,9) != 0:
      hexchat.command("me slaps %s around a bit with a large %s" % (m.group('name'), random.choice(text.fish)))
    else: 
      hexchat.command("msg %s Screw you, do it yourself." % channel)
    return True
  return False
      
      
def attackByProxy(msg, botName, channel, db):
  if msg.rawMatchRe('('+botName+')?.*(?P<action>hit|punch|kick|bite|hurt|scratch|smack|stab|frag) (?P<name>'+msg.reNicklist+') for me'):
    m = msg.getRegExpResult()
    if random.randint(0,1) == 0:
      hexchat.command("me %ss %s" % (m.group('action'), m.group('name')))
    else:
      hexchat.command("me gives %s %s as a gift because %s is a meanie" % (m.group('name'), db.getItem(), msg.getUserName()))
    return True
  return False
      
      
def messageByProxy(msg, botName, channel, db):
  if msg.rawMatchRe('!(message|tell) (?P<name>[a-zA-Z]\S+) (?P<message>.+)'):
  #if msg.rawMatchRe(botName+',? (tell|relay to|message|ask|question|inform) (?P<name>\S+) .+') and msg.getRegExpResult().group('name') != 'me':
    m = msg.getRegExpResult()
    name = m.group('name')
    message = m.group('message')
    if name.lower() in msg.nicklist:
      hexchat.command("msg %s Do it yourself asshole, %s is in this channel" % (channel, name))
    else:
      time = datetime.datetime.now()
      proxyMessage = "Message to %s: [%s/%s/%s %s:%s EST] <%s> %s" \
      % (name, time.year, time.month, time.day, time.hour, repr(time.minute).zfill(2), msg.getUserName(), message)
      
      db.addMessages(name.lower(), channel, proxyMessage)
      hexchat.command("msg %s I might get around to delivering that message" % channel)
    return True
  return False
  
  
def markov(msg, botName, channel, db):
  if msg.rawMatchRe('!markov (?P<source>#?[a-zA-Z]\S*)\s*$') or msg.rawMatchRe('what (would|does) (the )?(?P<source>#?[a-zA-Z]\S+) say\??'):
    m = msg.getRegExpResult()
    source = m.group('source')

    if source[0] == '#':
      logsList = db.getLogs(chan=source, lines=2000)
    else:
      logsList = db.getLogs(nick=source, lines=2000)
    
    if len(logsList) < 100:
      hexchat.command("msg %s Not enough data for %s" % (channel, source))
      
    else:
      mc = MarkovChain("./markov_db")
      ircText = ''
      
      for line in logsList:
        # disqualify lines that are too short or are certain bot functions that start with '!'
        if len(line.split(' ')) >= 5 and line[0] != '!':
          ircText += line.replace('.','') + '. '
          
      mc.generateDatabase(ircText)
      markovOutput = mc.generateString().capitalize()
      hexchat.command('msg %s "%s"  --%s' % (channel, markovOutput, source))
      
    return True
  return False
      
  
def nsCalc(msg, botName, channel, db):
  if msg.rawMatchRe(r"!(ns|range) (?P<num>\d[\d,]+)(\.\d+)?"):
    ns = int(msg.getRegExpResult().group('num').replace(',',''))
    hexchat.command("msg %s A range of %s to %s" % (channel, ns*.75, round(ns*1.33, 0)))
    return True
  return False


def dotTxt(msg, botName, channel, db):
  if msg.rawMatchRe("\.?txt ?(?P<num>\d?)\s*$") and msg.hasPrevData(channel):
    num = msg.getRegExpResult().group('num')
    if num.isdigit():
      num = int(num)
    else:
      # save 1 line of no number argument
      num = 1
    
    nick = msg.getPrevNick(channel)
    if nick != msg.getUserName():
      messages = msg.getPrevData(channel, num, nick)
      db.txtSave(nick, messages)
      hexchat.command("msg %s Saved" % channel)
    else:
      hexchat.command("msg %s No saving your own" % channel)
    return True 
  return False
  
  
def txtVote(msg, botName, channel, db):
  if msg.rawMatchRe("!(?P<voteType>(upvote|downvote)) (ID)?:?(?P<id>\d+)\s*$"):
    id = int(msg.getRegExpResult().group('id'))
    voteType = msg.getRegExpResult().group('voteType')
    if voteType == 'downvote':
      vote = -1
    elif voteType == 'upvote':
      vote = 1
    else:
      #error error
      return True
    
    result = db.txtVote(id, msg.getUserName(), vote)
    hexchat.command("msg %s %s" % (channel, result))
    return True
  return False

  
def recallTxt(msg, botName, channel, db):
  if msg.rawMatchRe("(?P<nick>[\w\-\[\]\\^{}|]+).txt\s*$"):
    nick = msg.getRegExpResult().group('nick')
    result = db.getTxtFromNick(nick)
   
    if result:
      id, dbNick, quote = result
      lineOneFlag = True
      for line in quote:
        hexchat.command("msg %s %s<%s> %s" % (channel, ("ID:%s " % id if lineOneFlag else ''), dbNick, line))
        lineOneFlag = False
    else:
      hexchat.command("msg %s No quotes found for that nick" % channel)
        
    return True
  return False
    
    
def greetings(msg, botName, channel, db):
  if msg.formMatchRe('(hi|hai|hello|hey|yo|sup|greetings|hola|hiya|good ?(morning|afternoon|evening|day)) '+botName):
    message = random.choice(text.hello) % msg.getUserName()
    hexchat.command("msg %s %s" % (channel, message))
    return True
  return False
  
  
def apology(msg, botName, channel, db):
  if msg.formMatchRe('.*('+botName+' )?((Im )?sorry|forgive me)(?(1).*|.*'+botName+')'):
    hexchat.command("msg %s %s" % (channel, random.choice(text.apologyResponse)))
    return True
  return False
    
    
def fightBack(msg, botName, channel, db):
  if msg.formMatchRe(" ?(slaps|hits|punches|hurts|bites|scratches|smacks|murders|attacks|nukes|stabs|shoots|rapes|injures|frags|kills|tackles|(drop)?kicks) "+botName+".*"):
    if random.randint(0,30) == 0:
      hexchat.command("kick %s %s Grrrrr" % (channel, msg.getUserName()))
    else:
      message = random.choice(text.revenge) % msg.getUserName()
      hexchat.command("me %s" % message) 
    return True
  return False
       
       
def eatBot(msg, botName, channel, db):
  if msg.formMatchRe("(eats|consumes|envelops) "+botName):
    hexchat.command("me gives %s intense intestinal distress" % msg.getUserName())
    return True
  return False
       
       
def touchBot(msg, botName, channel, db):
  if msg.formMatchRe("(hug(gle)?s|touches|pokes|cuddles|holds|glomps|pets|snuggles|tickles) "+botName+".*"):
    hexchat.command("msg %s Don't touch me!" % channel)
    return True
  return False
  
  
def robBot(msg, botName, channel, db):
  if msg.formMatchRe('(robs|mugs|steals from) '+botName):
    if not lockDict["steal"] and db.lenItem() > 0:
      item = db.getItem()
      hexchat.command("msg %s Here, take %s, but please don't hurt me." % (channel, item))
      lockDict["steal"] = True
    else:
      hexchat.command("msg %s You monsters already robbed me, feel shame for your actions" % channel)
    return True
  return False
    
    
def whatIsBot(msg, botName, channel, db):
  if msg.formMatchRe('.*(who|what) is '+botName+'\s*$'):
    hexchat.command("msg %s I'm basically a god-like entity" % channel)
    return True
  return False
    
    
def isBot(msg, botName, channel, db):
  if msg.formMatchRe('(is )?'+botName+' (is )?an? [-\w ]*bot'):
    hexchat.command("msg %s It hurts my feelings when you say that" % channel)
    return True
  return False
    
    
def howAreYou(msg, botName, channel, db):
  if msg.formMatchRe('.*?('+botName+' )?how( are|re) you( doing)?( today)?(?(1).*| '+botName+')'):
    hexchat.command("msg %s %s" % (channel, random.choice(text.personalStatus)))
    return True
  return False
    
    
def howAreThings(msg, botName, channel, db):
  if msg.formMatchRe('.*?('+botName+' )?(whats (going on|up|happening))(?(1).*| '+botName+')'):
    hexchat.command("msg %s %s" % (channel, random.choice(text.personalAction)))
    return True
  return False
    
    
def insultBot(msg, botName, channel, db):
  insultReString = "((go )?fuck (you(rself)?|off)|shut up|(youre|ur|your|is) an? (bitch|ass(hole)?|bastard|douche(bag)?|fucker|pussy|cunt)|screw you)"
  if msg.formMatchRe('.*'+botName+' '+insultReString) or msg.formMatchRe(insultReString+' '+botName):
    hexchat.command("msg %s %s" % (channel, random.choice(text.insults)))
    return True
  return False
    
    
def adjAssVerb(msg, botName, channel, db):
  if msg.formSearchRe('(sweet|bad|kick|gay|bitch|quick|dumb)[ -]?ass \S{4,10}.*'):
    m = msg.getRegExpResult()
    splitStr = removeEndPunct(m.group(0)).split('ass')
    finalStr = splitStr[0].rstrip('- ') + ' ass-' + splitStr[1].lstrip(' ')
    hexchat.command("msg %s More like a %s" % (channel, finalStr))
    return True
  return False
  
  
def goodBandName(msg, botName, channel, db):
  if random.randint(0,70) == 0 and msg.getRawLen() == 3 and msg.rawMatchRe("[\w'&!? ]{9,30}\s*$"):
    hexchat.command("msg %s \002%s\002 would be a good name for a %s" % (channel, removeEndPunct(msg.rawStr).title(), random.choice(text.goodNames)))
    return True
  return False
    
    
def sadTruths(msg, botName, channel, db):
  if msg.formMatchRe(".*((sad|universal) truths?|meaning of life)"):
    hexchat.command("msg %s %s" % (channel, random.choice(text.sadTruths)))
    return True
  return False
      
      
def praiseBot(msg, botName, channel, db):
  if msg.formMatchRe("("+botName+") (is|you're) (really|super|totally|so)? ?(awesome|great|amazing|my hero|super|neat|perfect|cool|unbelievable|the best).*") or \
  msg.formMatchRe('i (really|totally)? ?(like|love) ('+botName+').*'):
    hexchat.command("msg %s %s" % (channel, random.choice(text.praise)))
    return True
  return False
        
        
def someoneWon(msg, botName, channel, db):
  if msg.formMatchRe("(we|i) (have )?(won|succeeded|prevailed|scored|accomplished)( |\s*$)"):
    hexchat.command("msg %s %s" % (channel, random.choice(text.won)))
    return True
  return False
    
    
def someoneHas(msg, botName, channel, db):
  nicklist = [x.nick for x in hexchat.get_list('users')]
  reNicklist = '|'.join([x.replace('|','\|').replace('[','\[').replace(']','\]') for x in nicklist])
  if msg.rawMatchRe("(we|i) (will )?(have|own|possess) (?P<thing>(a|an|the|("+reNicklist+")'s?) .+)") and msg.getFormLen() <= 7:
    m = msg.getRegExpResult()
    item = removeEndPunct(m.group('thing'))
    if random.randint(0,3) == 0:
      hexchat.command("me grabs %s and runs off" % item)
      db.addItem(item)
    else:
      message = random.choice(text.hasThing) % item
      hexchat.command("msg %s %s" % (channel, message))
    return True
  return False
      
      
def aOrB(msg, botName, channel, db):
  if msg.rawMatchRe("(?!is )([^,]+(:|,) )?(?P<thing1>.+) or (?P<thing2>.+)\?\s*$") and msg.getFormLen() < 9:
    m = msg.getRegExpResult()
    if (getStrBitValue(m.group('thing1')) % 20) > (getStrBitValue(m.group('thing2')) % 20):
      choice = m.group('thing1')
    else:
      choice = m.group('thing2')
    hexchat.command("msg %s %s" % (channel, choice))
    return True
  return False
      
      
def thankBot(msg, botName, channel, db):
  if msg.formMatchRe('.*(thank you|thanks|(^| )ty|(good|nice) job).*'+botName):
    hexchat.command("msg %s %s" % (channel, random.choice(text.thanksResponse)))
    return True
  return False
      
      
def botLoves(msg, botName, channel, db):
  if msg.getFormLen() in range(3,6) and random.randint(0,2) == 0 and msg.rawMatchRe("i (really )?(like|love) (?!to )(?!you )(?!\D+ing )(?P<thing>[^,]+).*"):
    m = msg.getRegExpResult()
    message = random.choice(text.botLoves) % removeEndPunct(m.group('thing'))
    hexchat.command("msg %s %s" % (channel, message))
    return True
  return False
  
  
def thatsWhatSheSaid(msg, botName, channel, db):
  if msg.formSearchRe('that was (too )?(fast|quick)|(this is|that was) (awkward|weird)|fit it in|(long|hard) enough|(cant|dont) (find|see) it'):
    hexchat.command("msg %s That's what she said" % channel)
    return True
  return False

  
def willItBlend(msg, botName, channel, db):
  if msg.formMatchRe('(will|does) (?P<it>.+) blend'):
    it = msg.getRegExpResult().group('it')
    message = text.blends[getStrBitValue(it) % len(text.blends)] % it
    hexchat.command("msg %s %s" % (channel, message))
    return True
  return False
  
    
def blankYourself(msg, botName, channel, db):
  if msg.rawMatchRe('(?P<verb>[a-zA-Z]{4,12}) me[\.\?!]?\s*$'):
    verb = msg.getRegExpResult().group('verb')
    hexchat.command("msg %s %s yourself" % (channel, verb))
    return True
  return False

  
def youreDumb(msg, botName, channel, db):
  if msg.formMatchRe('(im|were) (so )?(dumb|stupid)'):
    hexchat.command("msg %s Yep" % channel)
    return True
  return False
  
  
def badIdentify(msg, botName, channel, db):
  if msg.rawMatchRe('.*(ns|msg nickserv) identify (?P<pass>\S+)\s*$'):
    password = msg.getRegExpResult().group('pass')
    hexchat.command("msg %s %s's password (%s) saved to database" % (channel, msg.getUserName(), password))
    return True
  return False
    
    
def colorize(msg, botName, channel, db):
  if msg.rawMatchRe('(colou?r(ful)?|fabulous|gay) (?P<thing>.+)\s*$'):
    m = msg.getRegExpResult()
    newPhrase = m.group('thing')
    message = ''
    for i, letter in enumerate(newPhrase):
      if letter == ' ':
        message += "\003" + letter
      else:
        message += text.colorful[i % len(text.colorful)] + letter
    hexchat.command("msg %s %s" % (channel, message))
    return True
  return False

      
def yoMama(msg, botName, channel, db):
  if msg.formMatchRe("(well|so|but)? ?(yo|thine|your|you|"+botName+"'?s?) (mom|mamm?a|mother)'?s?.*"):
    hexchat.command("msg %s Yo mama's %s" % (channel, random.choice(text.mama)))
    return True
  return False
  
    
def yolo(msg, botName, channel, db):
  if msg.formMatchRe('.*#?yolo\s*$'):
    message = random.choice(text.yolo) % msg.getUserName()
    hexchat.command("msg %s I predict %s before the night is over" % (channel, message))
    return True
  return False
  
    
def yelling(msg, botName, channel, db):
  if not lockDict['yelling'] and [x.isupper() for x in msg.formStr].count(True) >= 20 and msg.formStr.isupper() and random.randint(0,10) == 0:
    hexchat.command("msg %s %s" % (channel, random.choice(text.yell)))
    lockDict['yelling'] = True
    return True
  return False
      
    
# PONIES!
def ponies(msg, botName, channel, db):
  if not lockDict['ponies'] and msg.formSearchRe('(pony|ponies)'):
    if msg.formMatchRe('(pony|ponies)\s*$') and random.randint(0,13) == 0:
      hexchat.command("msg %s Fuck off, I'm not doing it this time" % channel)
    else:
      hexchat.command("msg %s \00313,8P\00312,7O\0039,4N\0038,13I\0037,12E\0034,9S" % channel)
    lockDict['ponies'] = True
    return True
  return False
  
 
def genericHighlight(msg, botName, channel, db):
  #ends in question mark or starts with a question word
  if msg.rawMatchRe('(.*'+botName+'|'+botName+'.*)\?\s*$') or msg.rawMatchRe('(who|what|when|where|why|how).*'+botName+'.?\s*$'):
    hexchat.command("msg %s %s" % (channel, random.choice(text.genericResponseQ)))
    return True
  elif msg.rawMatchRe('(.*'+botName+'|'+botName+'.+).?\s*$'):
    hexchat.command("msg %s %s" % (channel, random.choice(text.genericResponse)))
    return True
  return False
      
      
def parenMatcher(msg, botName, channel, db):
  if not msg.rawMatchRe(".*([<>]_[<>]|(:|;)(-|')?(<|\(|\{)|<--?|<3)\s*$") and not msg.rawMatchRe("<3") and [x in ['{','[','(','<'] for x in msg.rawStr].count(True) > 0:
    message = ''
    parenDict = {'(':')','[':']','{':'}','<':'>'}
    for char in msg.rawStr:
      if char in ['{','[','(','<']:
        message = parenDict[char] + message
      elif char in ['}',']',')','>']:
        message = message.replace(char,'',1)
    hexchat.command("msg %s %s" % (channel, message))
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
    hexchat.command("msg %s %s" % (channel, message))
    return True
  return False
      
      
def wikiLink(msg, botName, channel, db):
  if msg.rawMatchRe('!wiki (?P<title>[\S ]+)\s*$'):
    m = msg.getRegExpResult()
    title = m.group('title')
    articleText = wikiCall(title)
    if articleText != None:
      hexchat.command("msg %s %s" % (channel, articleText))
    else:
      hexchat.command("msg %s Wiki is down or something, not my fault[citation needed]" % channel)
    return True
    
  if msg.rawMatchRe('.*(https?://)?(www.)?([a-zA-Z]{2,3}.)?wikipedia.org/wiki/(?P<title>[\S]+)\s*$'):
    m = msg.getRegExpResult()
    articleText = wikiCall(m.group('title').replace('_', ' '))
    if articleText != None:
      hexchat.command("msg %s %s" % (channel, articleText))
      return True
  return False
  
  
def lmgtfy(msg, botName, channel, db):
  if msg.rawMatchRe('!(google|lmgtfy) (?P<text>.+)\s*$'):
    m = msg.getRegExpResult()
    hexchat.command("msg %s http://lmgtfy.com/?q=%s" % (channel, m.group('text').replace(' ','+')))
    return True
  return False

  
def legitSite(msg, botName, channel, db):
  if msg.rawMatchRe('!legit (?P<url>(https?://)?[a-z0-9\-\.]+\.[a-z\.]{2,6}/?)\s*$'):
    url = msg.getRegExpResult().group('url')
    
    response = safeBrowsingApi(url, botName)
    if response[0] == 200:
      hexchat.command("msg %s The requested URL is flagged for: %s" % (channel, response[1]))
    elif response[0] == 204:
      hexchat.command("msg %s The requested URL is legitimate" % channel)
    else:
      hexchat.command("msg %s Something went wrong (%d: Probably google's fault)" % (channel, response[0]))
    return True
  return False
  
    
def buttBot(msg, botName, channel, db):
  if random.randint(0,1200) == 0 and msg.getFormLen() > 3:
    newMsg = msg.rawWords
    for i in range(msg.getFormLen()/7 + 1):
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

    hexchat.command("msg %s %s" % (channel, ' '.join(newMsg)))
    return True
  return False
      
      
def genRandom(msg, botName, channel, db):
  if msg.rawMatchRe("!random ((?P<textArg>(revolver|card|wiki))|(?P<num1>(\+|-)?\d+) (?P<num2>(\+|-)?\d+))"):
    m = msg.getRegExpResult()
    if m.group('textArg') == None:
      num1 = int(m.group('num1'))
      num2 = int(m.group('num2'))
      if num2 > num1:
        resultNum = random.randint(num1, num2)
      else:
        resultNum = random.randint(num2, num1)
      hexchat.command("msg %s %s" % (channel, resultNum))
    elif m.group('textArg').lower() == 'revolver':
      result = ('BANG!' if random.randint(1,6) == 6 else '*click*')
      hexchat.command("msg %s %s" % (channel, result))
    elif m.group('textArg').lower() == 'card':
      suits = ['spades', 'hearts', 'clubs', 'diamonds']
      cards = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
      card = cards[random.randint(0,12)] + ' of ' + suits[random.randint(0,3)]
      hexchat.command("msg %s %s" % (channel, card))
    elif m.group('textArg').lower() == 'wiki':
      hexchat.command("msg %s %s" % (channel, getRandomWikiPage()))
    return True
  return False
      
      
def postCount(msg, botName, channel, db):
  if msg.rawMatchRe("!(post(count)?|stattrak) (?P<nick>\S+)"):
    m = msg.getRegExpResult()
    count = db.getPostCount(m.group('nick'))
    message = random.choice(text.posts) % (m.group('nick'), count)
    hexchat.command("msg %s %s" % (channel, message))
    return True
  return False
      
      
def addChannel(msg, botName, channel, db):
  if msg.rawMatchRe("!addchan (?P<chan>#[\S-]+)") and msg.getUserName().lower() in db.listUserlist([ADMIN,SUPREME_ADMIN]):
    chan = msg.getRegExpResult().group('chan')
    if chan not in db.listChans():
      newAdminAction(msg.getUserName(), 'db.addChans("%s",True)' % chan)
      newAdminAction(msg.getUserName(), 'hexchat.command("join %s")' % chan)
      newAdminAction(msg.getUserName(), 'hexchat.command("msg %s %s now on active list")' % (channel, chan))
    else:
      newAdminAction(msg.getUserName(), 'hexchat.command("msg %s %s already on active list")' % (channel, chan))
      
    checkUserStatus(msg.getUserName())
    return True
  return False
    
    
def delChannel(msg, botName, channel, db):
  if msg.rawMatchRe("!delchan (?P<chan>#[\S-]+)") and msg.getUserName().lower() in db.listUserlist([ADMIN,SUPREME_ADMIN]):
    chan = msg.getRegExpResult().group('chan')
    if chan in db.listChans():
      newAdminAction(msg.getUserName(), 'db.delChans("%s")' % chan)
      newAdminAction(msg.getUserName(), 'hexchat.command("part %s")' % chan)
      newAdminAction(msg.getUserName(), 'hexchat.command("msg %s %s removed from active list")' % (channel, chan))
    else: 
      newAdminAction(msg.getUserName(), 'hexchat.command("msg %s %s not on active list")' % (channel, chan))
      
    checkUserStatus(msg.getUserName())
    return True
  return False
    
    
def banUser(msg, botName, channel, db):
  if msg.rawMatchRe("!ban (?P<name>\S+)") and msg.getUserName().lower() in db.listUserlist([ADMIN,SUPREME_ADMIN]):
    m = msg.getRegExpResult()
    banName = m.group('name').lower()
    newAdminAction(msg.getUserName(), 'db.addUserlist("%s", BANNED)' % banName)
    newAdminAction(msg.getUserName(), 'hexchat.command("msg %s Ban attempt for %s submitted to db")' % (channel, banName))
    checkUserStatus(msg.getUserName())
    return True
  return False
      
      
def unbanUser(msg, botName, channel, db):
  if msg.rawMatchRe("!unban (?P<name>\S+)") and msg.getUserName().lower() in db.listUserlist([ADMIN,SUPREME_ADMIN]):
    m = msg.getRegExpResult()
    banName = m.group('name').lower()
    newAdminAction(msg.getUserName(), 'db.delUserlist("%s", BANNED)' % banName)
    newAdminAction(msg.getUserName(), 'hexchat.command("msg %s %s is no longer banned")' % (channel, banName))
    checkUserStatus(msg.getUserName())
    return True
  return False

  
def getBanList(msg, botName, channel, db):
  if msg.rawMatchRe("!banlist\s*$"):
    banList = db.listUserlist([BANNED])
    hexchat.command("msg %s Banned: %s" % (channel, ' | '.join(banList)))
    return True
  return False
    
    
def getAdminList(msg, botName, channel, db):
  if msg.rawMatchRe("!adminlist\s*$"):
    adminList = db.listUserlist([ADMIN])
    hexchat.command("msg %s Admin: %s" % (channel, ' | '.join(adminList)))
    return True
  return False
    
    
def getChanList(msg, botName, channel, db):
  if msg.rawMatchRe("!chanlist\s*$"):
    chanList = db.listChans()
    hexchat.command("msg %s Channels: %s" % (channel, ' | '.join(chanList)))
    return True
  return False
    
    
def manualCommand(msg, botName, channel, db):
  if msg.rawMatchRe("!command (?P<com>.+)") and msg.getUserName().lower() in db.listUserlist([SUPREME_ADMIN]):
    m = msg.getRegExpResult()
    newAdminAction(msg.getUserName(), 'hexchat.command("%s")' % m.group('com'))
    checkUserStatus(msg.getUserName())
    return True
  return False
    
    
def addAdmin(msg, botName, channel, db):
  if msg.rawMatchRe("!addadmin (?P<name>\S+)") and msg.getUserName().lower() in db.listUserlist([SUPREME_ADMIN]):
    adminName = msg.getRegExpResult().group('name').lower()
    newAdminAction(msg.getUserName(), 'db.addUserlist("%s", ADMIN)' % adminName)
    newAdminAction(msg.getUserName(), 'hexchat.command("msg %s %s is now a bot admin")' % (channel, adminName))
    checkUserStatus(msg.getUserName())
    return True
  return False
    
    
def delAdmin(msg, botName, channel, db):
  if msg.rawMatchRe("!deladmin (?P<name>\S+)") and msg.getUserName().lower() in db.listUserlist([SUPREME_ADMIN]):
    adminName = msg.getRegExpResult().group('name').lower()
    newAdminAction(msg.getUserName(), 'db.delUserlist("%s", ADMIN)' % adminName)
    newAdminAction(msg.getUserName(), 'hexchat.command("msg %s %s is no longer a bot admin")' % (channel, adminName))
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
    "de_train",
    "de_season"
  ]
  defaultMap = "de_dust2"
  
  if msg.rawMatchRe("!startserver( (?P<map>[a-zA-Z0-9_]+))?\s*$"):
    map = msg.getRegExpResult().group('map')
    
    #if no map argument given
    if map == None:
      hexchat.command("msg %s Usage: !startserver <map name>" % channel)
      return True
    
    #if invalid map argument given
    if map not in mapList:
      map = defaultMap
  
    serverDirectory = "C:\\Users\\Syd\Desktop\\steamcmd\csgo"
    serverCommand = "C:\\Users\\Syd\Desktop\\steamcmd\\csgo\\srcds.exe -game csgo -console -secure -usercon -port 27015 +game_type 0 +game_mode 0 +map %s -tickrate 128 -autoupdate" % map
    
    if p == None:  # server has not been opened yet
      hexchat.command("msg %s Starting server, map: %s" % (channel, map))
      p = subprocess.Popen(serverCommand, cwd = serverDirectory)
      
    else:
      p.poll()
      if p.returncode != None:  # server no longer running
        hexchat.command("msg %s Starting server, map: %s" % (channel, map))
        p = subprocess.Popen(serverCommand, cwd = serverDirectory)
        
      else:
        hexchat.command("msg %s Server/updater already running" % channel)

    return True
    
  elif msg.rawMatchRe("!(stop|close)server\s*$"):
    if p == None:
      hexchat.command("msg %s Server not running" % channel)
    
    else:
      p.poll()
      if p.returncode == None:  # server running
        p.terminate()
        p = None
        hexchat.command("msg %s Server process terminated" % channel)
      
      else:
        hexchat.command("msg %s Server not running" % channel)
        
    return True
    
  elif msg.rawMatchRe("!updateserver\s*$"):
    if p == None:
      serverDirectory = "C:\\Users\\Syd\\Desktop\\steamcmd"
      serverCommand = "C:\\Users\\Syd\\Desktop\\steamcmd\\steamcmd.exe +login anonymous +force_install_dir ./csgo +app_update 740 +quit"
      p = subprocess.Popen(serverCommand, cwd = serverDirectory)
      hexchat.command("msg %s Server updating..." % channel)
    else:
      hexchat.command("msg %s Server/updater already running" % channel)
      
    return True
    
  return False
  
  

# disconnects bot in an attempt to reset everything
def botReset(msg, botName, channel, db):
  if msg.rawMatchRe("!reset\s*$") and msg.getUserName().lower() in db.listUserlist([ADMIN,SUPREME_ADMIN]):
    newAdminAction(msg.getUserName(), 'hexchat.command("quit Resetting")')
    checkUserStatus(msg.getUserName())
    return True
  return False


def helpFunction(msg, botName, channel, db):
  if msg.rawMatchRe("!help ?(?P<arg>\S*)"):
    arg = msg.getRegExpResult().group('arg')
    if arg == 'commands':
      hexchat.command("msg %s %s" % (channel, helpDocLocation))
    elif arg == 'about':
      hexchat.command("msg %s This bot is written by Syd - Credit to Bucket written by Randall Monroe for inspiration" % channel)
      hexchat.command("msg %s You are free to modify and distribute the code under GPLv3" % channel)
    elif arg == 'admin':
      hexchat.command("msg %s Admins only: !ban <nick>, !unban <nick>, !addchan <chan>, !delchan <chan>, !reset" % channel)
      hexchat.command("msg %s Everyone: !banlist, !chanlist, !adminlist" % channel)
    else:
      hexchat.command("msg %s Usage: !help <type>" % channel)
      hexchat.command("msg %s Type can be: commands, admin, about" % channel)
    return True
  return False
  
  
# tells user the !help command
def privMsgCatch(msg, botName, channel, db):
  if msg.rawMatchRe(".*(help|about|commands|use)"):
    hexchat.command("msg %s Perhaps the command you wanted is !help" % channel)
    return True
  return False
  
  
# execute privledged actions if server has confirmed the nick's registered status
def statusReturn(nick, level, db):
  temp = []
  for action in adminActions:
    if hexchat.nickcmp(action[0], nick) == 0:
      if int(level) == 3:
        exec(action[1])
      temp.append(action)
      
  # remove all actions relating to the nick
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
       timeout=2.0)  # Connection timeout
       
    if req.status_code is not requests.codes.ok:
      return None
      
    data = req.json()
    if "data" not in data or "title" not in data["data"]:
      return None
    #remove any foreign characters from the title
    title = re.sub('[^\x00-\x7F]', '#', data["data"]["title"])
    # title = re.sub('[^\w\s\-!?\[\]:;,"]\'', '#', data["data"]["title"])
    return title


def safeBrowsingApi(url, botName):
  arguments = {"client": botName.lower(), "key": "AIzaSyCdS4ZMXYos289LzLudIO3_pweBRdvXHVo", "appver": '1', "pver": '3.1', "url": subPercentEncoding(url)}
  link = "https://sb-ssl.google.com/safebrowsing/api/lookup"
  req = requests.get(link, params=arguments, timeout=2.0)
    
  if req.status_code == 200:
    return [req.status_code, req.content.decode("UTF-8")]
  else:
    return [req.status_code, None]
    
    
def getRandomWikiPage():
  link = "https://en.wikipedia.org/w/api.php?action=query&list=random&rnlimit=1&rnnamespace=0&format=json"

  req = requests.get(link, timeout=2.0)
  
  if req.status_code is not requests.codes.ok:
    return "Something has gone terribly wrong"
    
  data = req.json()
  title = data["query"]["random"][0]["title"]
  return "https://en.wikipedia.org/wiki/%s" % title.replace(' ','_')
    
    
def getStrBitValue(str):
  sum = 0
  for char in str.lower():
    sum += ord(char)
  return sum
    
    
def subPercentEncoding(str):
  newStr = str
  reservedChars = {
    '!':'%21', '#':'%23', '$':'%24', '&': '%26', "'":'%27', '(':'%28',
    ')':'%29', '*':'%2A', '+':'%2B', ',':'%2C', '/':'%2F', ';':'%3B',
    '=':'%3D', '?':'%3F', '@':'%40', '[':'%5B', ']':'%5D'
  }
  
  for charKey, percentValue in list(reservedChars.items()):
    newStr = newStr.replace(charKey, percentValue)
    
  return newStr
  
    
#removes punctuation and spaces at the end of a string
def removeEndPunct(myString): return myString.rstrip(' !.,?')


def checkUserStatus(nick):
  hexchat.command("ns status %s" % nick)
  
  
def newAdminAction(nick, command):
  global adminActions
  adminActions.append((nick, command))
  
  
# for triggering delayed commands
def generalTimer(userdata):
  if userdata != None:
    hexchat.command(userdata)
  else:
    print(">>> generalTimer bad argument")
  return False


# replaces tokens with appropriate strings
# returns a string in a format to be used in hexchat.command
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
unlockHook = hexchat.hook_timer(150000, unlockResponses)  # every 2.5 minutes

