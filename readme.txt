Actions to set up bot.py for your own use:
   Requires xchat, python (using version 2.6, others probably work), requests library, pysqlite library, sqlite3
   Edit and run gendb.py to initialize the database (at the very least, set yourself as supreme admin)
   Edit bot.conf as necessary
   Edit passwordFile to indicate a text file with the bot's IRC identify password
   Make any changes to the code that you want;  The copyright is GPL for a reason


Issues you may have:
   ValueError: invalid \x escape
   Module has no __module_name__ defined
   
  try using the full path name when telling xchat to open the bot
  e.g. /py load C:/bot/bot.py
  use / instead of \ for this, even if you're running windows


Installing python modules on windows:
  https://www.youtube.com/watch?v=ddpYVA-7wq4 