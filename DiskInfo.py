from rich import print
import sys
import ctypes
import re
import json
import tabulate
Drive_Types = {
	0: "Unknown",
	1: "No root directory",
	2: "USB drive",
	3: "Local disk drive",
	4: "Network drive",
	5: "CD/DVD drive",
	6: "Ram disk drive"
}
def get_logical_drives():
	Mask = ctypes.windll.kernel32.GetLogicalDrives()
	Drives = []
	for I in range(26):
		if Mask & (1 << I):
			Drives.append(f"{chr(65 + I)}:\\")
	return Drives
def getDriveUsage(Drive):
	Free = ctypes.c_ulonglong()
	Total = ctypes.c_ulonglong()
	Total_Free = ctypes.c_ulonglong()
	Result = ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(Drive), ctypes.byref(Free), ctypes.byref(Total), ctypes.byref(Total_Free))
	if not Result:
		return None
	Used = Total.value - Free.value
	Percent = (Used / Total.value) * 100 if Total.value else 0
	return {
		"total": Total.value,
		"used": Used,
		"free": Free.value,
		"percent": Percent
	}
def getVolumeInfo(Drive):
	if not Drive.endswith("\\"):
		Drive += "\\"
	Volume_name_buffer = ctypes.create_unicode_buffer(261)
	Fs_name_buffer = ctypes.create_unicode_buffer(261)
	Result = ctypes.windll.kernel32.GetVolumeInformationW(ctypes.c_wchar_p(Drive), Volume_name_buffer, len(Volume_name_buffer), None, None, None, Fs_name_buffer, len(Fs_name_buffer))
	if Result:
		return [
			Volume_name_buffer.value,
			Fs_name_buffer.value
		]
	else:
		return None
def getDriveType(Drive):
	return ctypes.windll.kernel32.GetDriveTypeW(ctypes.c_wchar_p(Drive))
def formatSize(N):
	return f"{N / (1024 ** 3):.2f}"
def validateVolumeList(Volumes):
	if Volumes is None:
		return None
	Valid = []
	for Volume in Volumes:
		if not isinstance(Volume, str):
			print(f"Invalid drives: {Volume}")
			continue
		Volume = Volume.strip()
		if not re.fullmatch(r"^[a-zA-Z]:\\?$", Volume):
			print(f"Invalid drives: {Volume}")
			continue
		Valid.append(Volume)
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
def collectDriveInfo(AllDrive=True, Volumes=None):
	if AllDrive:
		Partitions = get_logical_drives()
	else:
		Partitions = parseVolumeList(Volumes)
		if Partitions is None:
			print("Invalid drives.")
			sys.exit(2)
	Result = []
	for Partition in Partitions:
		Info = getVolumeInfo(Partition) or [None, None]
		Drive_Type = getDriveType(Partition)
		Usage = getDriveUsage(Partition) or {
			"total": None,
			"free": None,
			"used": None,
			"percent": None
		}
		Result.append({
			"volume": Partition,
			"label": Info[0],
			"fs": Info[1],
			"type": Drive_Types.get(Drive_Type, "Unknown"),
			"total": Usage.get("total"),
			"free": Usage.get("free"),
			"used": Usage.get("used"),
			"percent": Usage.get("percent")
		})
	return Result
def printDriveInfo(Datas):
	for Data in Datas:
		print("Volume:", Data["volume"].replace("\\", ""))
		print("Label:", Data.get("label", "No label"))
		print(f"Type: {Data.get("type", "Unknown")}")
		print("File system:", Data.get("fs", "Unknown"))
		print(f"Used space: {formatSize(Data.get("used"))} GB ({Data.get("used")} Bytes)")
		if Data.get("percent") > 90:
			Color = "red"
		elif Data.get("percent") == 90:
			Color = "yellow"
		else:
			Color = "green"
		print(f"Used percentage: [{Color}]{Data.get("percent"):.2f}%[/{Color}]")
		print(f"Free space: {formatSize(Data.get("free"))} GB ({Data.get("free")} Bytes)")
		print(f"Capacity: {formatSize(Data.get("total"))} GB ({Data.get("total")} Bytes)")
		print()
def printJsonDriveInfo(Data):
	print(json.dumps(Data, indent=2))
def printTableDriveInfo(Data):
	print(tabulate.tabulate(Data, headers="keys", tablefmt="grid"))
def showDriveInfo(AllDrive=True, Volumes=None, Mode="normal"):
	Data = collectDriveInfo(AllDrive, Volumes)
	if Mode.lower() == "json":
		printJsonDriveInfo(Data)
	elif Mode.lower() == "table":
		printTableDriveInfo(Data)
	else:
		printDriveInfo(Data)
	sys.exit(0)
def showDriveLabel(AllDrive=True, Volumes=None, Label=False):
	if AllDrive:
		Partitions = get_logical_drives()
	else:
		Partitions = parseVolumeList(Volumes)
		if Partitions is None:
			print("Invalid drives.")
			sys.exit(127)
	Seen = set()
	for Partition in Partitions:
		Volume = Partition
		Volume_Name = Volume.replace("\\", "")
		if Volume not in Seen:
			Seen.add(Volume)
			if Label:
				Info = getVolumeInfo(Volume)
				Label_Name = Info[0] if Info and Info[0] else "No label"
				print(f"{Label_Name} ({Volume_Name})")
			else:
				print(Volume_Name)
	sys.exit(0)
def getVersion():
	return "1.3"
def showVersion():
	print(f"DiskInfo version {getVersion()}")
def showHelp():
	print(f"DiskInfo version {getVersion()} - Drive Information Tool")
	print("")
	print("Usage:")
	print("  diskinfo [option] [drive...]")
	print("")
	print("Options:")
	print("  -i, /i, --info")
	print("    Show detailed drive information")
	print("    Example: diskinfo -i C:\\ D:\\")
	print("")
	print("  -l, /l, --letter")
	print("    List all available drives (drive letters only)")
	print("    Example: diskinfo -l")
	print("")
	print("  -n, /n, --label")
	print("    Show drive labels with drive letters")
	print("    Example: diskinfo.py -n C:\\")
	print("")
	print("  --json")
	print("    show drive info with format json.")
	print("    Example: diskinfo --json")
	print("")
	print("  --table")
	print("    show drive info with format table.")
	print("    Example: diskinfo --table")
	print("")
	print("  -v, /v, --version")
	print("    Show program version")
	print("")
	print("  -h, /h, --help")
	print("    Show this help message")
	print("")
	print("Notes:")
	print("  - If no option is provided, the program will display all drive information")
	print("  - Valid drive format: C:\\ or D:")
	print("")
def main():
	Mode = "normal"
	if "--json" in sys.argv:
		Mode = "json"
		sys.argv.remove("--json")
	elif "--table" in sys.argv:
		Mode = "table"
		sys.argv.remove("--table")
	if len(sys.argv) < 2:
		showDriveInfo(Mode=Mode)
	else:
		Flag = sys.argv[1]
		if Flag.lower().startswith(("/n", "--label", "-n")):
			if len(sys.argv) < 3:
				showDriveLabel(Label=True)
			else:
				showDriveLabel(AllDrive=False, Volumes=sys.argv[2:], Label=True)
		elif Flag.lower().startswith(("/l", "--letter", "-l")):
			if len(sys.argv) < 3:
				showDriveLabel(Label=False)
			else:
				showDriveLabel(AllDrive=False, Volumes=sys.argv[2:], Label=False)
		elif Flag.lower().startswith(("-i", "--info", "/i")):
			if len(sys.argv) < 3:
				showDriveInfo(Mode=Mode)
			else:
				showDriveInfo(AllDrive=False, Volumes=sys.argv[2:], Mode=Mode)
		elif Flag.lower().startswith(("-v", "--version", "/v")):
			showVersion()
			sys.exit(0)
		elif Flag.lower().startswith(("-h", "--help", "/h")):
			showHelp()
			sys.exit(0)
		else:
			print("Unknown option: ", Flag)
			sys.exit(1)
if __name__ == "__main__":
	main()