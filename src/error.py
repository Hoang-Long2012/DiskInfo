from enum import Enum, auto
class DataErrorCode(Enum):
	No_Drive = auto()
	Invalid_Drives = auto()
	Usage_Limit = auto()
	Top_Limit = auto()
class FileWriteError(OSError):
	pass
class DataError(Exception):
	def __init__(self, Code, Message):
		self.code = Code
		self.message = Message
		super().__init__(Message)
class DataEmptyError(DataError):
	pass
class DataNotFoundError(DataError):
	pass
class DataInvalidError(DataError):
	pass
class DataOutOfLimitError(DataError):
	pass