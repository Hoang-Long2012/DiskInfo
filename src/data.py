import core
import constants
import utils
import error
def collectDriveInfo(AllDrive=True, Volumes=None):
	if AllDrive:
		Partitions = core.get_logical_drives() or []
	else:
		Partitions = utils.parseVolumeList(Volumes)
		if Partitions is None:
			raise error.DataEmptyError(error.DataErrorCode.Invalid_Drives, "Invalid drives.")
	Result = []
	for Partition in Partitions:
		try:
			Info = core.getVolumeInfo(Partition) or [None, None]
			Drive_Type = core.getDriveType(Partition)
			Usage = core.getDriveUsage(Partition) or {
				"total": None,
				"free": None,
				"used": None,
				"percent": None
			}
			Result.append({
				"drive": Partition,
				"label": Info[0],
				"type": constants.Drive_Types.get(Drive_Type, "Unknown"),
				"fs": Info[1],
				"used": Usage.get("used"),
				"percent": Usage.get("percent"),
				"free": Usage.get("free"),
				"total": Usage.get("total"),
				"status": utils.getUsageStyle(Usage.get("percent"))["status"]
			})
		except OSError:
			continue
	return Result
def sortData(Data, Type=None, Reverse=True):
	if not Data:
		return Data
	if not Type:
		return Data
	Data.sort(key=lambda x: x.get(constants.Sort_Keys.get(Type)) or 0, reverse=Reverse)
	return Data
def filterDriveType(Data, Types=None):
	if not Types:
		return Data
	Valid = set()
	for Item in Types:
		Key = Item.lower().strip()
		if Key in constants.Type_Alias:
			Valid.add(constants.Type_Alias[Key])
	Result = []
	for Item in Data:
		if Item.get("type") in Valid:
			Result.append(Item)
	return Result
def filterPercent(Data, Percent=90):
	if not isinstance(Percent, (int, float)):
		return Data
	Result = []
	for Item in Data:
		if (Item.get("percent") or 0) >= Percent:
			Result.append(Item)
	return Result
def filterExclude(Data, Exclude=None):
	Exclude = utils.parseVolumeList(Exclude)
	if not Exclude:
		return Data
	Seen = set()
	for Drive in Exclude:
		if not isinstance(Drive, str):
			continue
		Seen.add(Drive)
	Result = []
	for Item in Data:
		Drive = (Item.get("drive") or "").upper()
		if Drive not in Seen:
			Result.append(Item)
	return Result
def getData(AllDrive=True, Volumes=None, Sort=None, Reverse=True, filterType=None, Top=None, Percent=None, Exclude=None):
	Data = collectDriveInfo(AllDrive, Volumes)
	Data = filterExclude(Data, Exclude)
	Data = filterDriveType(Data, filterType)
	if Percent is not None:
		if Percent < 0 or Percent > 100:
			raise error.DataOutOfLimitError(error.DataErrorCode.Usage_Limit, "Usage must be between 0 and 100.")
		Data = filterPercent(Data, Percent)
	if not Data:
		raise error.DataEmptyError(error.DataErrorCode.No_Drive, "No drive information")
	Data = sortData(Data, Sort, Reverse)
	if isinstance(Top, int):
		if Top <= 0:
			raise error.DataOutOfLimitError(error.DataErrorCode.Top_Limit, "Top must be >= 1")
		Data = Data[:Top]
	return Data