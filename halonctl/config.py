class ConfigContainer(dict):
	def update(self, data):
		self.__dict__.update(data)

config = ConfigContainer()
