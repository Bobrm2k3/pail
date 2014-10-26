Steps to install pail:
  Download and install python 2.6
  Download and install xchat 2.0+
  Download and install pip for the python 2.6
  Use pip to install the following libraries: requests, PyMarkovChain
  Register a nick for the bot on the IRC server you want to run it on
  Create a text file in the project directory with only the bot's IRC idenfity password in it
  Edit and run gen/gendb.py to initialize the database (at the very least, set yourself as supreme admin)
  Edit and run gen/configFileSetup.py to generate the bot.conf config file
  Remove machine specific functions from the chanMsgFunctions list in bot.py such as openCsServer
  From xchat, load the bot e.g. /py load C:/bot/bot.py


Issues you may have:
   ValueError: invalid \x escape
   Module has no __module_name__ defined
   
  try using the full path name when telling xchat to open the bot
  e.g. /py load C:/bot/bot.py
  use / instead of \ for this, even if you're running windows
