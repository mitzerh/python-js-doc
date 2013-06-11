# 
# Just the simple script to fire up JSDoc...
# 
import sys, getopt
import modules.JSDoc as JSDoc
import ConfigParser

# default config to use @ config.ini
config_use = 'default'
config_file = './conf/config.ini'


# MAIN
def main():
	global config_use

	arguments = sys.argv[1:]
	arg_config = 0

	try:
		options, args = getopt.getopt(arguments, '', ['config='])
	except getopt.GetoptError:
		self.__getOut()

	for opt, arg in options:

		# config to use
		if opt == '--config':
			config_use = arg

	config = setConfig()

	JSDoc.parse(config)

# set config
def setConfig():
	
	cfg = ConfigParser.ConfigParser()
	cfg.read(config_file)

	if cfg.has_section(config_use) and config_use != 'default':
		cfg_items = cfg.items(config_use)
		print 'Using \'' + config_use + '\' configuration'
	else:
		cfg_items = cfg.items('default')
		print 'Using default configuration'

	config = {}
	for i, c in enumerate(cfg_items):
		config[c[0]] = c[1]

	return config


# start here
if __name__ == '__main__':
	main()
