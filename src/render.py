from rich import box
from rich.text import Text as text
from rich.panel import Panel as panel
from rich.console import Console as console, Group as group
from rich.table import Table as table
from rich.syntax import Syntax as syntax
import data
import utils
import core
import json
import sys
Console = console()
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
		Style = utils.getUsageStyle(Data.get("percent"))
		Color = Style["color"]
		Icon = Style["icon"]
		Status = Data.get("status") or "unknown"
		Used = Data.get("used") or 0
		Text.append(f"Used space: {utils.formatSize(Used)} ({Used} Bytes)\n", style=Color)
		Percent = Data.get("percent") or 0
		Text.append(f"Used percentage: {Percent:.0f}%\n", style=Color)
		Free = Data.get("free") or 0
		Text.append(f"Free space: {utils.formatSize(Free)} ({Free} Bytes)\n", style=Color)
		Total = Data.get("total") or 0
		Text.append(f"Capacity: {utils.formatSize(Total)} ({Total} Bytes)\n")
		Text.append(f"Status: {Icon} {Status}", style=Color)
		Drive_Icon = utils.getDriveIcon(Type)
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
		Style = utils.getUsageStyle(Item.get("percent"))
		Color = Style["color"]
		Icon = Style["icon"]
		Status = Item.get("status") or "unknown"
		Drive_Icon = utils.getDriveIcon(Item.get("type"))
		Label = Item.get("label") or "No label"
		Used = Item.get("used") or 0
		Free = Item.get("free") or 0
		Percent = Item.get("percent") or 0
		Table.add_row(text(f"{Drive_Icon} {Volume}", style=Color), text(Label), text(f"{utils.formatSize(Used)}", style=Color), text(f"{utils.formatSize(Free)}", style=Color), text(f"{Percent:.0f}%", style=Color), text(f"{Icon} {Status}", style=Color))
	return Table
def renderDriveInfo(AllDrive=True, Volumes=None, Mode="normal", Sort=None, Reverse=True, filterType=None, Top=None, Percent=None):
	try:
		Data = data.collectDriveInfo(AllDrive, Volumes)
	except ValueError:
		Console.print("Invalid drives.")
		sys.exit(2)
	Data = data.filterDriveType(Data, filterType)
	if Percent is not None:
		if Percent < 0 or Percent > 100:
			Console.print("Usage must be between 0 and 100.")
			sys.exit(2)
		Data = data.filterPercent(Data, Percent)
	if not Data:
		Console.print("No drive information.")
		sys.exit(2)
	Data = data.sortData(Data, Sort, Reverse)
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