import ConfigParser

config = ConfigParser.RawConfigParser()


config.add_section('Section')
config.set('Section', 'name', 'pail')
config.set('Section', 'server', 'frozen.coldfront.net')
config.set('Section', 'port', '6667')
config.set('Section', 'passwordFile', 'a9v823h4aio38t.txt')
config.set('Section', 'database', 'bot.db')

# Writing configuration file to 'bot.conf'
with open('bot.conf', 'wb') as configfile:
    config.write(configfile)