import sqlite3 as sqlite
import sys

BANNED = 0
ADMIN = 1
SUPREME_ADMIN = 2


con = sqlite.connect('bot.db')

with con:

  cur = con.cursor()
  
  cur.execute("CREATE TABLE Items(Name TEXT)")
  
  # list of nicks that the bot recognizes as an admin or as banned users that bot won't respond to
  cur.execute("CREATE TABLE Userlist(Nick TEXT UNIQUE, Status INTEGER, Verified INTEGER)")
  cur.execute("INSERT INTO Userlist VALUES('syd',%s, 0)" % SUPREME_ADMIN)
  
  # list of channels bot will join and be active in by default
  cur.execute("CREATE TABLE Chans(Chan TEXT UNIQUE, Status INTEGER)")
  cur.execute("INSERT INTO Chans VALUES('#asdf', 1)")
  
  cur.execute("CREATE TABLE AutoResponses(Trigger TEXT, Response TEXT)")
  
  cur.execute("CREATE TABLE Messages(Nick TEXT, Chan TEXT, Message TEXT)")
  
  cur.execute("CREATE TABLE TextStorage(Trigger TEXT UNIQUE, Response TEXT)")
  
  cur.execute("CREATE TABLE UserData(Nick TEXT UNIQUE, PostCount INTEGER)")
  
  
  cur.execute("CREATE TABLE Quotes(Id INTEGER PRIMARY KEY, Nick TEXT NOT NULL, Txt TEXT NOT NULL, DateLastChecked TEXT NOT NULL)")
  cur.execute("CREATE TABLE QuoteVotes(Nick TEXT NOT NULL, Quote_Id INTEGER, Vote INTEGER NOT NULL, FOREIGN KEY(Quote_Id) REFERENCES Quotes(Id))")
  
  
  cur.execute("CREATE TABLE Log(Nick TEXT NOT NULL, Message TEXT NOT NULL, Chan TEXT NOT NULL, Date TEXT NOT NULL)")
  
  con.commit()

  
  

