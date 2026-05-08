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
Drive_Icons = {
	"Unknown": "❓",
	"No root directory": "🚫",
	"USB drive": "🔌",
	"Local disk drive": "💽",
	"Network drive": "🌐",
	"CD/DVD drive": "💿",
	"Ram disk drive": "⚡"
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
	if not Mask:
		return None
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
def collectDriveInfo(AllDrive=True, Volumes=None):
	if AllDrive:
		Partitions = get_logical_drives() or []
	else:
		Partitions = parseVolumeList(Volumes)
		if Partitions is None:
			Console.print("Invalid drives.")
			sys.exit(2)
	Result = []
	for Partition in Partitions:
		try:
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
				"total": Usage.get("total"),
				"status": getUsageStyle(Usage.get("percent"))["status"]
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
		if Key in Type_Alias:
			Valid.add(Type_Alias[Key])
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
	return Drive_Icons.get(Type) or "❓"
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
		Style = getUsageStyle(Data.get("percent"))
		Color = Style["color"]
		Icon = Style["icon"]
		Status = Data.get("status") or "unknown"
		Used = Data.get("used") or 0
		Text.append(f"Used space: {formatSize(Used)} ({Used} Bytes)\n", style=Color)
		Percent = Data.get("percent") or 0
		Text.append(f"Used percentage: {Percent:.0f}%\n", style=Color)
		Free = Data.get("free") or 0
		Text.append(f"Free space: {formatSize(Free)} ({Free} Bytes)\n", style=Color)
		Total = Data.get("total") or 0
		Text.append(f"Capacity: {formatSize(Total)} ({Total} Bytes)\n")
		Text.append(f"Status: {Icon} {Status}", style=Color)
		Drive_Icon = getDriveIcon(Type)
		Panel = panel(Text, title=text(f"{Drive_Icon} Drive: {Volume}", style=Color), border_style=Color, box=box.SIMPLE)
		Panels.append(Panel)
	return group(*Panels)
def renderJsonDriveInfo(Data):
	return syntax(json.dumps(Data, indent=2, ensure_ascii=False), "json")
def renderTableDriveInfo(Data):
	Title = text("Drive info", style="bold")
	Table = table(title=Title, title_justify="center", show_lines=False, box=box.SIMPLE, expand=False, pad_edge=False, show_header=True, header_style="bold")
	Table.add_column("Drive", justify="left")
	Table.add_column("Label", justify="left")
	Table.add_column("Used", justify="center")
	Table.add_column("Free", justify="center")
	Table.add_column("Usage", justify="right")
	Table.add_column("Status", justify="right")
	for Item in Data:
		Volume = Item["drive"].replace("\\", "")
		Style = getUsageStyle(Item.get("percent"))
		Color = Style["color"]
		Icon = Style["icon"]
		Status = Item.get("status") or "unknown"
		Drive_Icon = getDriveIcon(Item.get("type"))
		Label = Item.get("label") or "No label"
		Used = Item.get("used") or 0
		Free = Item.get("free") or 0
		Percent = Item.get("percent") or 0
		Table.add_row(text(f"{Drive_Icon} {Volume}", style=Color), text(Label), text(f"{formatSize(Used)}", style=Color), text(f"{formatSize(Free)}", style=Color), text(f"{Percent:.0f}%", style=Color), text(f"{Icon} {Status}", style=Color))
	return Table
def renderDriveInfo(AllDrive=True, Volumes=None, Mode="normal", Sort=None, Reverse=True, filterType=None, Top=None, Percent=None):
	Data = collectDriveInfo(AllDrive, Volumes)
	Data = filterDriveType(Data, filterType)
	if Percent is not None:
		if Percent < 0 or Percent > 100:
			Console.print("Usage must be between 0 and 100.")
			sys.exit(2)
		Data = filterPercent(Data, Percent)
	if not Data:
		Console.print("No drive information.")
		sys.exit(2)
	Data = sortData(Data, Sort, Reverse)
	if isinstance(Top, int):
		if Top <= 0:
			Console.print("Top must be >= 1")
			sys.exit(2)
		Data = Data[:Top]
	if Mode.lower() == "json":
		return renderJsonDriveInfo(Data)
	elif Mode.lower() == "table":
		return renderTableDriveInfo(Data)
	else:
		return renderTextDriveInfo(Data)
def showDriveLabel(AllDrive=True, Volumes=None, Label=False):
	if AllDrive:
		Partitions = get_logical_drives() or []
	else:
		Partitions = parseVolumeList(Volumes)
		if Partitions is None:
			Console.print("Invalid drives.")
			sys.exit(127)
	Seen = set()
	for Partition in Partitions:
		try:
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
		except Exception:
			continue
	sys.exit(0)
def getVersion():
	return "1.6"
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
	Console.print("  -j, /j, --json")
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
	Console.print("    Default order: descending (largest/highest first).")
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
	Console.print("  -T, /T, --top [NUMBER_OF_DRIVES]")
	Console.print("    Show top N drives after sorting.")
	Console.print("    Example: diskinfo --sort used --top 1")
	Console.print("")
	Console.print("  -u, /u, --usage [PERCENT]")
	Console.print("    Show only drives with some usage.")
	Console.print("    Example: diskinfo --usage 90")
	Console.print("")
	Console.print("  -v, /v, --version")
	Console.print("    Show program version.")
	Console.print("")
	Console.print("  -h, /h, --help")
	Console.print("    Show this help message.")
	Console.print("")
	Console.print("Notes:")
	Console.print("  - If no option is provided, the program will display all drive information.")
	Console.print("  - Valid drive format: C:\\, D:/ or E:.")
	Console.print("  - By default, the drives are arranged in descending order.")
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
	Parser.add_argument("-j", "--json", action="store_true")
	Parser.add_argument("--table", action="store_true")
	Parser.add_argument("-l", "--letter", action="store_true")
	Parser.add_argument("-n", "--label", action="store_true")
	Parser.add_argument("-s", "--sort", choices=["usage", "used", "free", "total"])
	Parser.add_argument("-r", "--reverse", action="store_false")
	Parser.add_argument("-t", "--type", nargs="+", choices=sorted(Type_Alias))
	Parser.add_argument("-w", "--watch", nargs="?", const=2, type=float, metavar="SECONDS")
	Parser.add_argument("-T", "--top", type=int, metavar="n")
	Parser.add_argument("-u", "--usage", type=float, metavar="PERCENT")
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
	if Args.usage is not None and not Args.sort:
		Args.sort = "usage"
	elif Args.top and not Args.sort:
		Args.sort = "used"
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
		if Args.watch <= 0:
			Console.print("Watch interval must be > 0.")
			sys.exit(2)
		try:
			with live(console=Console, screen=True, auto_refresh=False) as Live:
				while True:
					Live.update(renderDriveInfo(AllDrive=(len(Args.drives) == 0), Volumes=Args.drives if Args.drives else None, Mode=Mode, Sort=Args.sort, Reverse=Args.reverse, filterType=Args.type, Top=Args.top, Percent=Args.usage))
					Live.refresh()
					time.sleep(Args.watch)
		except KeyboardInterrupt:
			Console.print("\n[yellow]Stopping...[/yellow]")
			sys.exit(0)
	else:
		Console.print(renderDriveInfo(AllDrive=(len(Args.drives) == 0), Volumes=Args.drives if Args.drives else None, Mode=Mode, Sort=Args.sort, Reverse=Args.reverse, filterType=Args.type, Top=Args.top, Percent=Args.usage))
		sys.exit(0)
if __name__ == "__main__":
	main()