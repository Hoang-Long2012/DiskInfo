from rich.console import Console as console
from winsound import MessageBeep as messageBeep
import constants
import re
import os
import sys
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
def getUsageStyle(Value, Interface="cli"):
	Value = float(Value or 0)
	for Level in constants.Usage_Levels:
		if Value >= Level["min"]:
			Key = Level["key"]
			if Interface == "cli":
				Color = constants.CLI_Status_Colors.get(Key, "white")
			else:
				Color = constants.GUI_Status_Colors.get(Key, "#ffffff")
			return {
				"color": Color,
				"icon": Level["icon"],
				"status": Level["label"],
				"key": Key
			}
def getDriveIcon(Type, Interface="cli"):
	if Interface == "cli":
		return constants.CLI_Drive_Icons.get(Type) or "❓"
	else:
		return constants.GUI_Drive_Icons.get(Type) or "SP_DriveHDIcon"
def getFsColor(Fs, Interface="cli"):
	if not Fs:
		if Interface == "cli":
			return "grey50"
		else:
			return "#aaaaaa"
	Key = str(Fs).strip()
	if Interface == "cli":
		return constants.CLI_FS_Colors.get(Key, constants.CLI_FS_Colors.get(Key.upper(), "white"))
	else:
		return constants.GUI_FS_Colors.get(Key, constants.GUI_FS_Colors.get(Key.upper(), "#aaaaaa"))
def getBasePath():
	if getattr(sys, "frozen", False):
		return os.path.abspath(os.path.dirname(sys.executable))
	return os.path.abspath(os.path.dirname(__file__))
def getFilePath(Name):
	Base = os.path.dirname(os.path.abspath(getBasePath()))
	return os.path.join(Base, Name)
def beep():
	messageBeep(-1)