from rich import print, box
import rich.table as table
import rich.console as console
import sys
import ctypes
import re
import json
import argparse
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
			"drive": Partition,
			"label": Info[0],
			"type": Drive_Types.get(Drive_Type, "Unknown"),
			"fs": Info[1],
			"used": Usage.get("used"),
			"percent": Usage.get("percent"),
			"free": Usage.get("free"),
			"total": Usage.get("total")
		})
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
def getColor(Data):
	if (Data or 0) > 90:
		Color = "red"
	elif (Data or 0) == 90:
		Color = "yellow"
	else:
		Color = "green"
	return Color
def printDriveInfo(Datas):
	for Data in Datas:
		print("Drive:", Data["drive"].replace("\\", ""))
		print("Label:", Data.get("label", "No label"))
		print(f"Type: {Data.get("type", "Unknown")}")
		print("File system:", Data.get("fs", "Unknown"))
		Color = getColor(Data.get("percent"))
		print(f"Used space: [{Color}]{formatSize(Data.get("used"))} GB ({Data.get("used")} Bytes)[/{Color}]")
		print(f"Used percentage: [{Color}]{Data.get("percent"):.0f}%[/{Color}]")
		print(f"Free space: [{Color}]{formatSize(Data.get("free"))} GB ({Data.get("free")} Bytes)[/{Color}]")
		print(f"Capacity: {formatSize(Data.get("total"))} GB ({Data.get("total")} Bytes)")
		print()
def printJsonDriveInfo(Data, Sort=None):
	print(json.dumps(Data, indent=2))
def printTableDriveInfo(Data):
	Console = console.Console()
	Table = table.Table(title="Drive info", show_lines=False, box=box.SIMPLE, expand=False, pad_edge=True)
	Table.add_column("Drive", justify="left")
	Table.add_column("Used", justify="right")
	Table.add_column("Free", justify="right")
	Table.add_column("Usage", justify="right")
	for Item in Data:
		Color = getColor(Item.get("percent"))
		Table.add_row(Item["drive"].replace("\\", ""), f"[{Color}]{formatSize(Item.get("used"))} GB[/{Color}]", f"[{Color}]{formatSize(Item.get("free"))} GB[/{Color}]", f"[{Color}]{Item.get("percent"):.0f}%[/{Color}]")
	Console.print(Table)
def showDriveInfo(AllDrive=True, Volumes=None, Mode="normal", Sort=None, Reverse=True):
	Data = collectDriveInfo(AllDrive, Volumes)
	if not Data:
		print("No drive information.")
		sys.exit(2)
	Data = sortData(Data, Sort, Reverse)
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
	return "1.4"
def showVersion():
	print(f"DiskInfo version {getVersion()}")
def showHelp():
	print(f"DiskInfo version {getVersion()} - Drive Information Tool")
	print("")
	print("Usage:")
	print("  diskinfo [option] [drive...]")
	print("")
	print("Options:")
	print("  -l, /l, --letter")
	print("    List all available drives (drive letters only).")
	print("    Example: diskinfo -l")
	print("")
	print("  -n, /n, --label")
	print("    Show drive labels with drive letters.")
	print("    Example: diskinfo.py -n C:\\")
	print("")
	print("  --json")
	print("    Show drive info with format json.")
	print("    Example: diskinfo --json")
	print("")
	print("  --table")
	print("    Show drive info with format table.")
	print("    Example: diskinfo --table")
	print("")
	print("  -s, /s, --sort [usage|used|free|total]")
	print("    Sort drives by specified field:")
	print("      Usage  - Used percentage.")
	print("      Used   - Used space.")
	print("      Free   - Free space.")
	print("      Total  - Total capacity.")
	print("    Default order: descending.")
	print("    Example: diskinfo --sort usage")
	print("")
	print("  -r, /r, --reverse")
	print("    Reverse sort order (ascending instead of descending).")
	print("    Example: diskinfo --sort usage --reverse")
	print("")
	print("  -v, /v, --version")
	print("    Show program version.")
	print("")
	print("  -h, /h, --help")
	print("    Show this help message.")
	print("")
	print("Notes:")
	print("  - If no option is provided, the program will display all drive information.")
	print("  - Valid drive format: C:\\ or D:")
	print("")
def normalizeWindowsArgs(argv):
	Normalized = []
	for Arg in argv:
		if Arg.startswith("/") and len(Arg) > 1:
			if len(Arg) == 2:
				Normalized.append("-" + Arg[1:2])
			else:
				Normalized.append("--" + Arg[1:])
		else:
			Normalized.append(Arg)
	return Normalized
def parseArgs():
	ArgsList = normalizeWindowsArgs(sys.argv[1:])
	Parser = argparse.ArgumentParser(add_help=False)
	Parser.add_argument("drives", nargs="*")
	Parser.add_argument("--json", action="store_true")
	Parser.add_argument("--table", action="store_true")
	Parser.add_argument("-l", "--letter", action="store_true")
	Parser.add_argument("-n", "--label", action="store_true")
	Parser.add_argument("-s", "--sort", choices=["usage", "used", "free", "total"])
	Parser.add_argument("-r", "--reverse", action="store_false")
	Parser.add_argument("-h", "--help", action="store_true")
	Parser.add_argument("-v", "--version", action="store_true")
	return Parser.parse_args(ArgsList)
def main():
	Args = parseArgs()
	Mode = "normal"
	if Args.json:
		Mode = "json"
	elif Args.table:
		Mode = "table"
	if Args.help:
		showHelp()
		sys.exit(0)
	if Args.version:
		showVersion()
		sys.exit(0)
	if Args.letter:
		if Args.drives:
			showDriveLabel(AllDrive=False, Volumes=Args.drives, Label=False)
		else:
			showDriveLabel(Label=False)
	if Args.label:
		if Args.drives:
			showDriveLabel(AllDrive=False, Volumes=Args.drives, Label=True)
		else:
			showDriveLabel(Label=True)
	showDriveInfo(AllDrive=(len(Args.drives) == 0), Volumes=Args.drives if Args.drives else None, Mode=Mode, Sort=Args.sort, Reverse=Args.reverse)
if __name__ == "__main__":
	main()