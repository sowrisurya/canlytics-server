import logging
from logging.handlers import TimedRotatingFileHandler

class Logger:
	def __new__(cls, *args, **kwargs):
		if not hasattr(cls, "_instance"):
			cls._instance = super(Logger, cls).__new__(cls)
		return cls._instance

	def __init__(self, name, level = logging.DEBUG, format = "%(asctime)s:%(levelname)s:%(message)s", datefmt = "%d-%b-%y %H:%M:%S", filename = "logs.log"):
		self.logger = logging.getLogger(name)
		self.logger.setLevel(level)
		self.formatter = logging.Formatter(format, datefmt)
		self.file_handler = logging.FileHandler(filename)
		self.file_handler.setFormatter(self.formatter)
		self.logger.addHandler(self.file_handler)
		time_handler = TimedRotatingFileHandler(filename, when = "midnight", interval = 1, backupCount=5)
		time_handler.setFormatter(self.formatter)
		self.logger.addHandler(time_handler)

	def debug(self, message):
		self.logger.debug(message)

	def info(self, message):
		self.logger.info(message)

	def warning(self, message):
		self.logger.warning(message)

	def error(self, message):
		self.logger.error(message)

	def critical(self, message):
		self.logger.critical(message)