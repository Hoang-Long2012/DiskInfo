from rich.console import Console as console
import constants
import re
Console = console()
def formatSize(N):
	if N is None:
		return "unknown"
	Units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "BB"]
	Size = float(N)
	for Unit in Units:
		if Size < 1024 or Unit == Units[-1]:
			if Unit == "Bytes":
				return f"{int(Size)} {Unit}"
			elif Size >= 100:
				return f"{Size:.0f} {Unit}"
			elif Size >= 10:
				return f"{Size:.1f} {Unit}"
			return f"{Size:.2f} {Unit}"
		Size /= 1024
def validateVolumeList(Volumes):
	if Volumes is None:
		return None
	Valid = []
	Invalid = []
	for Volume in Volumes:
		if not isinstance(Volume, str):
			Invalid.append(Volume)
			continue
		Volume = Volume.strip()
		if not re.fullmatch(r"^[a-zA-Z]:[/\\]?$", Volume):
			Invalid.append(Volume)
			continue
		Valid.append(Volume)
	if Invalid:
		Invalid_Drives = ", ".join(Invalid)
		Console.print(f"Invalid drives: {Invalid_Drives}")
	if Valid:
		return Valid
	else:
		return None
def parseVolumeList(Volumes=None):
	Volumes = validateVolumeList(Volumes)
	if Volumes:
		for Item, Volume in enumerate(Volumes):
			if not Volume.lower().endswith("\\"):
				Volumes[Item] = Volume + "\\"
		return Volumes
	else:
		return None
def getUsageStyle(Data):
	if (Data or 0) > 90:
		return {
			"color": "red",
			"icon": "🔴",
			"status": "Critical"
		}
	elif (Data or 0) >= 80:
		return {
			"color": "yellow",
			"icon": "🟡",
			"status": "Warning"
		}
	else:
		return {
			"color": "green",
			"icon": "🟢",
			"status": "Healthy"
		}
def getDriveIcon(Type):
	return constants.Drive_Icons.get(Type) or "❓"
def getFsColor(Fs):
	if not Fs:
		return "grey50"
	Key = str(Fs).strip()
	return constants.FS_Colors.get(Key, constants.FS_Colors.get(Key.upper(), "white"))