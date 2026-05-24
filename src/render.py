from rich import box
from rich.text import Text as text
from rich.panel import Panel as panel
from rich.console import Console as console, Group as group
from rich.table import Table as table
from rich.syntax import Syntax as syntax
from rich.progress_bar import ProgressBar
import data
import utils
import core
import error
import json
import sys
Console = console()
def safeGetData(AllDrive=True, Volumes=None, Sort=None, Reverse=True, filterType=None, Top=None, Percent=None, Exclude=None):
	try:
		Data = data.getData(AllDrive=AllDrive, Volumes=Volumes, Sort=Sort, Reverse=Reverse, filterType=filterType, Top=Top, Percent=Percent, Exclude=Exclude)
	except error.DataEmptyError as Error:
		if Error.code == error.DataErrorCode.No_Drive:
			Console.print("No drive information")
			sys.exit(2)
		elif Error.code == error.DataErrorCode.Invalid_Drives:
			Console.print("Invalid drives")
			sys.exit(2)
	except error.DataOutOfLimitError as Error:
		if Error.code == error.DataErrorCode.Usage_Limit:
			Console.print("Usage must be between 0 and 100.")
			sys.exit(2)
		elif Error.code == error.DataErrorCode.Top_Limit:
			Console.print("Top must be >= 1")
			sys.exit(2)
	return Data
def makeUsageLine(Percent, Color):
	Grid = table.grid(padding=(0,1))
	Grid.add_column(no_wrap=True)
	Grid.add_column()
	Grid.add_column(no_wrap=True)
	Grid.add_row(text("Used percentage:", style=Color), ProgressBar(total=100, completed=Percent, width=20, complete_style=Color), text(f"{Percent:.0f}%", style=Color))
	return Grid
def makeUsageBar(Percent, Color):
	Grid = table.grid(padding=(0,1))
	Grid.add_column(ratio=1)
	Grid.add_column(no_wrap=True)
	Grid.add_row(ProgressBar(total=100, completed=Percent, width=20, complete_style=Color), text(f"{Percent:.0f}%", style=Color))
	return Grid
def renderTextDriveInfo(Datas, Simple=False, Bytes=True, Beep=False):
	Panels = []
	for Data in Datas:
		Top = text()
		Volume = Data["drive"].replace("\\", "")
		Label = Data.get("label") or "No label"
		if not Simple:
			Top.append(f"Label: {Label}\n")
		else:
			Top.append(f"Label: {Label}")
		Type = Data.get("type", "Unknown")
		Drive_Icon = utils.getDriveIcon(Type)
		if not Simple:
			Top.append(f"Type: {Drive_Icon} {Type}\n")
		FS = Data.get("fs") or "Unknown"
		FS_Color = utils.getFsColor(FS)
		if not Simple:
			Top.append("File system: ")
			Top.append(f"{FS}\n", style=FS_Color)
		Style = utils.getUsageStyle(Data.get("percent"))
		Color = Style["color"]
		Icon = Style["icon"]
		Status = Data.get("status") or "unknown"
		Used = Data.get("used") or 0
		Used_STR = f"{utils.formatSize(Used)} ({Used} Bytes)" if Bytes else f"{utils.formatSize(Used)}"
		if not Simple:
			Top.append("Used space: ")
			Top.append(Used_STR, style=Color)
		Percent = Data.get("percent") or 0
		if Beep:
			if Percent >= 90:
				utils.beep()
		Free = Data.get("free") or 0
		Free_STR = f"{utils.formatSize(Free)} ({Free} Bytes)\n" if Bytes else f"{utils.formatSize(Free)}\n"
		Bottom = text()
		if not Simple:
			Bottom.append("Free space: ")
			Bottom.append(Free_STR, style=Color)
		Total = Data.get("total") or 0
		Total_STR = f"{utils.formatSize(Total)} ({Total} Bytes)\n" if Bytes else f"{utils.formatSize(Total)}\n"
		if not Simple:
			Bottom.append("Capacity: ")
			Bottom.append(Total_STR)
		Bottom.append("Status: ")
		Bottom.append(f"{Icon} {Status}", style=Color)
		Content = group(Top, makeUsageLine(Percent, Color), Bottom)
		Title = text.assemble(f"{Drive_Icon} Drive: ", (Volume, Color))
		Panel = panel(Content, title=Title, border_style=Color, box=box.SIMPLE)
		Panels.append(Panel)
	return group(*Panels)
def renderJsonDriveInfo(Data):
	return syntax(json.dumps(Data, indent=2, ensure_ascii=False), "json")
def renderTableDriveInfo(Data, Simple=False, Beep=False):
	Title = text("Drive info", style="bold")
	Table = table(title=Title, title_justify="center", show_lines=False, box=box.SIMPLE, expand=False, pad_edge=False, show_header=True, header_style="bold")
	Table.add_column("Drive", justify="left")
	Table.add_column("Label", justify="left")
	if not Simple:
		Table.add_column("Used", justify="center")
		Table.add_column("Free", justify="center")
	Table.add_column("Usage", justify="right")
	Table.add_column("Status", justify="right")
	for Item in Data:
		Volume = Item["drive"].replace("\\", "")
		Style = utils.getUsageStyle(Item.get("percent"))
		Color = Style["color"]
		Icon = Style["icon"]
		Status = Item.get("status") or "unknown"
		Drive_Icon = utils.getDriveIcon(Item.get("type"))
		Label = Item.get("label") or "No label"
		Used = Item.get("used") or 0
		Free = Item.get("free") or 0
		Percent = Item.get("percent") or 0
		if Beep:
			if Percent >= 90:
				utils.beep()
		if not Simple:
			Table.add_row(text(f"{Drive_Icon} {Volume}", style=Color), text(Label), text(f"{utils.formatSize(Used)}", style=Color), text(f"{utils.formatSize(Free)}", style=Color), makeUsageBar(Percent, Color), text(f"{Icon} {Status}", style=Color))
		else:
			Table.add_row(text(f"{Drive_Icon} {Volume}", style=Color), text(Label), makeUsageBar(Percent, Color), text(f"{Icon} {Status}", style=Color))
	return Table
def renderDriveInfo(AllDrive=True, Volumes=None, Mode="normal", Sort=None, Reverse=True, filterType=None, Top=None, Percent=None, Exclude=None, Simple=False, Bytes=True, Beep=True):
	Data = safeGetData(AllDrive=AllDrive, Volumes=Volumes, Sort=Sort, Reverse=Reverse, filterType=filterType, Top=Top, Percent=Percent, Exclude=Exclude)
	if Mode.lower() == "json":
		return renderJsonDriveInfo(Data)
	elif Mode.lower() == "table":
		return renderTableDriveInfo(Data, Simple, Beep)
	else:
		return renderTextDriveInfo(Data, Simple, Bytes, Beep)
def showDriveLabel(AllDrive=True, Volumes=None, Label=False):
	if AllDrive:
		Partitions = core.get_logical_drives() or []
	else:
		Partitions = utils.parseVolumeList(Volumes)
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
					Info = core.getVolumeInfo(Volume)
					Label_Name = Info[0] if Info and Info[0] else "No label"
					Console.print(f"{Label_Name} ({Volume_Name})")
				else:
					Console.print(Volume_Name)
		except Exception:
			continue
	sys.exit(0)
def renderDriveSummary(AllDrive=True, Volumes=None, Sort=None, Reverse=True, filterType=None, Top=None, Percent=None, Exclude=None, Simple=False, Bytes=True):
	Data = safeGetData(AllDrive=AllDrive, Volumes=Volumes, Sort=Sort, Reverse=Reverse, filterType=filterType, Top=Top, Percent=Percent, Exclude=Exclude)
	Text = text()
	Total = len(Data)
	Text.append(f"Drives: {Total}\n")
	Used = sum(X.get("used", 0) for X in Data)
	Used_STR = f"{utils.formatSize(Used)} ({Used} Bytes)" if Bytes else utils.formatSize(Used)
	Text.append(f"Used: {Used_STR}\n")
	Free = sum(X.get("free", 0) for X in Data)
	Free_STR = f"{utils.formatSize(Free)} ({Free} Bytes)" if Bytes else utils.formatSize(Free)
	Text.append(f"Free: {Free_STR}\n")
	Capacity = sum(X.get("total", 0) for X in Data)
	Capacity_STR = f"{utils.formatSize(Capacity)} ({Capacity} Bytes)" if Bytes else utils.formatSize(Capacity)
	if Simple:
		Text.append(f"Capacity: {Capacity_STR}")
	else:
		Text.append(f"Capacity: {Capacity_STR}\n")
	if not Simple:
		Max_Drive = max(Data, key=lambda X: X.get("percent", 0), default=None)
		Min_Drive = min(Data, key=lambda X: X.get("percent", 0), default=None)
		Max_Drive = Max_Drive["drive"]
		Min_Drive = Min_Drive["drive"]
		Text.append(f"Most used: {Max_Drive}\n")
		Text.append(f"Least used: {Min_Drive}")
	return panel(Text, title="Summary", box=box.SIMPLE)