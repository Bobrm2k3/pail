Actions to set up bot.py for your own use:
   Requires xchat, python 2.6, requests library, pysqlite library, sqlite3
   Edit and run gen/gendb.py to initialize the database (at the very least, set yourself as supreme admin)
   Edit and run gen/configFileSetup.py to generate the bot.conf config file
   Edit passwordFile to indicate a text file with the bot's IRC identify password


Issues you may have:
   ValueError: invalid \x escape
   Module has no __module_name__ defined
   
  try using the full path name when telling xchat to open the bot
  e.g. /py load C:/bot/bot.py
  use / instead of \ for this, even if you're running windows


Installing python modules on windows:
  https://www.youtube.com/watch?v=ddpYVA-7wq4 