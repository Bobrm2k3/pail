import re, string, botDbAccess


class quoteObject(object):

  def __init__(self, nick = '', text = []):
  
    self.nick = nick
    self.quoteText = text
    self.id = 0
    self.downvotes = []
    
    
  # tries to fill the object with data from a database, returns True is successful
  def fillFromDbNick(self, db, nick):
    result = db.txtRecallNick(nick)
    if result == None:
      return False
    
    self.id, self.nick, self.quoteText, self.downvotes = result
    
    return True
    
    
  # tries to fill the object with data from a database, returns True is successful
  def fillFromDbId(self, db, id):
    result = db.txtRecallId(id)
    if result == None:
      return False
    
    self.id, self.nick, self.quoteText, self.downvotes = result
    
    return True
  
  
  def saveToDb(self, db):
    db.txtSave(self.nick, self.quoteText)
