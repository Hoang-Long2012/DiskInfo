from rich import box
from rich.live import Live as live
from rich.text import Text as text
from rich.panel import Panel as panel
from rich.console import Console as console, Group as group
from rich.table import Table as table
from rich.syntax import Syntax as syntax
import sys
import ctypes
import re
import json
import argparse
import time
Console = console()
Drive_Types = {
	0: "Unknown",
	1: "No root directory",
	2: "USB drive",
	3: "Local disk drive",
	4: "Network drive",
	5: "CD/DVD drive",
	6: "Ram disk drive"
}
Type_Alias = {
	"usb": "USB drive",
	"removable": "USB drive",
	"local": "Local disk drive",
	"disk": "Local disk drive",
	"fixed": "Local disk drive",
	"network": "Network drive",
	"net": "Network drive",
	"cd": "CD/DVD drive",
	"dvd": "CD/DVD drive",
	"ram": "Ram disk drive",
	"unknown": "Unknown"
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
	if N is None:
		return "unknown"
	return f"{N / (1024 ** 3):.2f}"
def validateVolumeList(Volumes):
	if Volumes is None:
		return None
	Valid = []
	for Volume in Volumes:
		if not isinstance(Volume, str):
			Console.print(f"Invalid drives: {Volume}")
			continue
		Volume = Volume.strip()
		if not re.fullmatch(r"^[a-zA-Z]:\\?$", Volume):
			Console.print(f"Invalid drives: {Volume}")
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
			Console.print("Invalid drives.")
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
def filterDriveType(Data, Types=None):
	if not Types:
		return Data
	Valid = set()
	for Item in Types:
		Key = Item.lower().strip()
		if Key in Type_Alias:
			Valid.add(Type_Alias[Key])
	Result = []
	for Item in Data:
		if Item.get("type") in Valid:
			Result.append(Item)
	return Result
def getColor(Data):
	if (Data or 0) > 90:
		Color = "red"
	elif (Data or 0) >= 80:
		Color = "yellow"
	else:
		Color = "green"
	return Color
def renderTextDriveInfo(Datas):
	Panels = []
	for Data in Datas:
		Text = text()
		Volume = Data["drive"].replace("\\", "")
		Label = Data.get("label") or "No label"
		Text.append(f"Label: {Label}\n")
		Type = Data.get("type", "Unknown")
		Text.append(f"Type: {Type}\n")
		FS = Data.get("fs") or "Unknown"
		Text.append(f"File system: {FS}\n")
		Color = getColor(Data.get("percent"))
		Used = Data.get("used") or 0
		Text.append(f"Used space: {formatSize(Used)} GB ({Used} Bytes)\n", style=Color)
		Percent = Data.get("percent") or 0
		Text.append(f"Used percentage: {Percent:.0f}%\n", style=Color)
		Free = Data.get("free") or 0
		Text.append(f"Free space: {formatSize(Free)} GB ({Free} Bytes)\n", style=Color)
		Total = Data.get("total") or 0
		Text.append(f"Capacity: {formatSize(Total)} GB ({Total} Bytes)\n")
		Panel = panel(Text, title=f"Drive: {Volume}", border_style=Color, box=box.SIMPLE)
		Panels.append(Panel)
	return group(*Panels)
def renderJsonDriveInfo(Data):
	return syntax(json.dumps(Data, indent=2, ensure_ascii=False), "json")
def renderTableDriveInfo(Data):
	Title = "Drive info"
	Table = table(title=Title, show_lines=False, box=box.SIMPLE, expand=False, pad_edge=True, show_header=True, header_style="bold")
	Table.add_column("Drive", justify="left")
	Table.add_column("Used", justify="right")
	Table.add_column("Free", justify="right")
	Table.add_column("Usage", justify="right")
	Table.add_row("-" * len(Title))
	for Item in Data:
		Color = getColor(Item.get("percent"))
		Used = Item.get("used") or 0
		Free = Item.get("free") or 0
		Percent = Item.get("percent") or 0
		Table.add_row(Item["drive"].replace("\\", ""), f"[{Color}]{formatSize(Used)} GB[/{Color}]", f"[{Color}]{formatSize(Free)} GB[/{Color}]", f"[{Color}]{Percent:.0f}%[/{Color}]")
	return Table
def renderDriveInfo(AllDrive=True, Volumes=None, Mode="normal", Sort=None, Reverse=True, filterType=None):
	Data = collectDriveInfo(AllDrive, Volumes)
	Data = filterDriveType(Data, filterType)
	if not Data:
		Console.print("No drive information.")
		sys.exit(2)
	Data = sortData(Data, Sort, Reverse)
	if Mode.lower() == "json":
		return renderJsonDriveInfo(Data)
	elif Mode.lower() == "table":
		return renderTableDriveInfo(Data)
	else:
		return renderTextDriveInfo(Data)
def showDriveLabel(AllDrive=True, Volumes=None, Label=False):
	if AllDrive:
		Partitions = get_logical_drives()
	else:
		Partitions = parseVolumeList(Volumes)
		if Partitions is None:
			Console.print("Invalid drives.")
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
				Console.print(f"{Label_Name} ({Volume_Name})")
			else:
				Console.print(Volume_Name)
	sys.exit(0)
def getVersion():
	return "1.5"
def showVersion():
	Console.print(f"DiskInfo version {getVersion()}")
def showHelp():
	Console.print(f"DiskInfo version {getVersion()} - Drive Information Tool")
	Console.print("")
	Console.print("Usage:")
	Console.print("  diskinfo [option] [drive...]")
	Console.print("")
	Console.print("Options:")
	Console.print("  -l, /l, --letter")
	Console.print("    List all available drives (drive letters only).")
	Console.print("    Example: diskinfo -l")
	Console.print("")
	Console.print("  -n, /n, --label")
	Console.print("    Show drive labels with drive letters.")
	Console.print("    Example: diskinfo.py -n C:\\")
	Console.print("")
	Console.print("  --json")
	Console.print("    Show drive info with format json.")
	Console.print("    Example: diskinfo --json")
	Console.print("")
	Console.print("  --table")
	Console.print("    Show drive info with format table.")
	Console.print("    Example: diskinfo --table")
	Console.print("")
	Console.print("  -s, /s, --sort [usage|used|free|total]")
	Console.print("    Sort drives by specified field:")
	Console.print("      Usage  - Used percentage.")
	Console.print("      Used   - Used space.")
	Console.print("      Free   - Free space.")
	Console.print("      Total  - Total capacity.")
	Console.print("    Default order: descending.")
	Console.print("    Example: diskinfo --sort usage")
	Console.print("")
	Console.print("  -r, /r, --reverse")
	Console.print("    Reverse sort order (ascending instead of descending).")
	Console.print("    Example: diskinfo --sort usage --reverse")
	Console.print("")
	Console.print("  -t, /t, --type [usb|local|cd|network|ram]")
	Console.print("    Filter drives by type.")
	Console.print("    Example: diskinfo --type usb")
	Console.print("")
	Console.print("  -w, /w, --watch [SECONDS]")
	Console.print("    Watch drives in real time and auto-refresh display.")
	Console.print("    SECONDS defines update interval (default: 2).")
	Console.print("    Press Ctrl+C to exit watch mode.")
	Console.print("    Example: diskinfo --watch 0.5")
	Console.print("")
	Console.print("  -v, /v, --version")
	Console.print("    Show program version.")
	Console.print("")
	Console.print("  -h, /h, --help")
	Console.print("    Show this help message.")
	Console.print("")
	Console.print("Notes:")
	Console.print("  - If no option is provided, the program will display all drive information.")
	Console.print("  - Valid drive format: C:\\ or D:")
	Console.print("")
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
	Parser.add_argument("-t", "--type", nargs="+", choices=sorted(Type_Alias))
	Parser.add_argument("-w", "--watch", nargs="?", const=2, type=float, metavar="SECONDS")
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
	if Args.watch is not None:
		try:
			with live(console=Console, screen=True, auto_refresh=False) as Live:
				while True:
					Live.update(renderDriveInfo(AllDrive=(len(Args.drives) == 0), Volumes=Args.drives if Args.drives else None, Mode=Mode, Sort=Args.sort, Reverse=Args.reverse, filterType=Args.type))
					Live.refresh()
					time.sleep(Args.watch)
		except KeyboardInterrupt:
			Console.print("\n[yellow]Stopping...[/yellow]")
			sys.exit(0)
	else:
		Console.print(renderDriveInfo(AllDrive=(len(Args.drives) == 0), Volumes=Args.drives if Args.drives else None, Mode=Mode, Sort=Args.sort, Reverse=Args.reverse, filterType=Args.type))
		sys.exit(0)
if __name__ == "__main__":
	main()