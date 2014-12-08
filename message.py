import re, string, hexchat

MAX_MESSAGE_SAVE = 5

class msgObject(object):
  # takes the string list that hexchat provides
  def __init__(self):
    self.prevData = {}
    self.channel = ''
    self.userName = ''
    self.rawStr = ''
    
  
  def strUpdate(self, inputStr, channel):
  
    #save data of last things said in the channel before the new data overwrites it
    if self.channel:
      #if no entry for the channel exists, create it
      if self.channel not in self.prevData.keys():
        self.prevData[self.channel] = [[self.userName, self.rawStr]]
      else:
        self.prevData[self.channel].insert(0, [self.userName, self.rawStr])
        
        # remove oldest saved message is it's over the save limit for the channel
        if len(self.prevData[self.channel]) > MAX_MESSAGE_SAVE:
          self.prevData[self.channel].pop()
          
    self.channel = channel
  
    #remove non-ascii characters
    inputStr = [re.sub('[^\x00-\x7F]', '#', word) for word in inputStr]
  
    self.userName = inputStr[0]
    self.rawStr = ' '.join(inputStr[1:])
    
    #save and lop off access level
    self.accessLevel = inputStr[-1:][0]
    if self.rawStr[-1:] in ['@','%','~','&','+']:
      self.rawStr = self.rawStr[:-2]
      
    #formStr is the same as rawStr with all punctuation removed
    self.formStr = self.rawStr
    for punct in ['.',',',':',';',"'",'"','!','?']:
      self.formStr = self.formStr.replace(punct,'')
      
    self.rawWords = self.rawStr.split(' ')
    self.formWords = self.formStr.split(' ')
    
    # create and sanitize a list of nicks in the channel for reg exp
    self.nicklist = [x.nick.lower() for x in hexchat.get_list('users')]
    self.nicklistUpper = [x.nick for x in hexchat.get_list('users')]
    self.reNicklist = '|'.join([x.replace('|','\|').replace('[','\[').replace(']','\]') for x in self.nicklist])
  
    
    
  # returns true if the regular expression matches rawStr
  def rawMatchRe(self, expression):
    self.regExpResult = re.match(expression, self.rawStr, re.IGNORECASE)
    return self.regExpResult != None
    
  def formMatchRe(self, expression):
    self.regExpResult = re.match(expression, self.formStr, re.IGNORECASE)
    return self.regExpResult != None

  # returns true if the regular expression is in rawStr
  def rawSearchRe(self, expression):
    self.regExpResult = re.search(expression, self.rawStr, re.IGNORECASE)
    return self.regExpResult != None
    
  def formSearchRe(self, expression):
    self.regExpResult = re.search(expression, self.formStr, re.IGNORECASE)
    return self.regExpResult != None
   
  #returns result of most recent reg exp call
  def getRegExpResult(self): return self.regExpResult
  
  def getAccessLevel(self): return self.accessLevel
  def getUserName(self): return self.userName
  def getRawLen(self): return len(self.rawWords)
  def getFormLen(self): return len(self.formWords)
  
  #takes a channel name, number lines, and opional nick
  #returns the nick and text of the number of things said in that channel
  #returns an empty list if argument doesn't have an entry
  def getPrevData(self, channel, number = 1, nick = None):
    if channel not in self.prevData:
      return []
      
    if number > MAX_MESSAGE_SAVE: number = MAX_MESSAGE_SAVE
    
    prevMessages = self.prevData[channel]
    prevMessages.reverse()
    
    # if a specific nick is specified, pick out only the messages that match
    if nick != None:
      validMessages = []
      for post in prevMessages:
        if post[0].lower() == nick.lower():
          validMessages.append(post[1])
        
    else:
      validMessages = [x[1] for x in prevMessages]
      
    
    return validMessages[-number:]
    
    
  #gets the nick of the last person to post a in a channel
  def getPrevNick(self, channel):
    if channel in self.prevData:
      return self.prevData[channel][0][0]
    else:
      return None
  
  def hasPrevData(self, channel):
    return (channel in self.prevData)

  
  
  