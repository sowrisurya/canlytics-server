import logging

file_haneler = logging.FileHandler("logs.log")
file_haneler.setLevel(logging.DEBUG)
file_haneler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(message)s"))