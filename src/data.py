import core
import constants
import utils
def collectDriveInfo(AllDrive=True, Volumes=None):
	if AllDrive:
		Partitions = core.get_logical_drives() or []
	else:
		Partitions = utils.parseVolumeList(Volumes)
		if Partitions is None:
			raise ValueError("Invalid drives.")
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
		except Exception:
			continue
	return Result
def sortData(Data, Type=None, Reverse=True):
	if not Data:
		return Data
	if not Type:
		return Data
	if Type.lower() == "usage":
		Data.sort(key=lambda x: x.get("percent") or 0, reverse=Reverse)
	elif Type.lower() == "used":
		Data.sort(key=lambda x: x.get("used") or 0, reverse=Reverse)
	elif Type.lower() == "free":
		Data.sort(key=lambda x: x.get("free") or 0, reverse=Reverse)
	elif Type.lower() == "total":
		Data.sort(key=lambda x: x.get("total") or 0, reverse=Reverse)
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