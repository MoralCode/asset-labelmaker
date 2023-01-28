from configparser import ConfigParser, NoOptionError

class ConfigFinder:

	def __init__(self, configfilename, configsection="Default"):
		self.config = ConfigParser()
		self.config.read(configfilename)
		self.section = configsection

	def getString(self, key, default=""):
		try:
			return self.config.get(self.section, key)
		except (KeyError, NoOptionError) as e:
			return default

	def getInteger(self, key):
		val = self.getString(key, default=None)
		if val:
			return int(val)
		else:
			return val

	def getFloat(self, key):
		val = self.getString(key, default=None)
		if val:
			return float(val)
		else:
			return val

	def getBoolean(self, key):
		val = self.getString(key, default=None)
		val = val.lower()
		return val == "true"