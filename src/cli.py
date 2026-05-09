from rich.live import Live as live
from rich.console import Console as console
from constants import Type_Alias
import render
import sys
import argparse
import time
Console = console()
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
			render.showDriveLabel(AllDrive=False, Volumes=Args.drives, Label=False)
		else:
			render.showDriveLabel(Label=False)
	if Args.label:
		if Args.drives:
			render.showDriveLabel(AllDrive=False, Volumes=Args.drives, Label=True)
		else:
			render.showDriveLabel(Label=True)
	if Args.watch is not None:
		if Args.watch <= 0:
			Console.print("Watch interval must be > 0.")
			sys.exit(2)
		try:
			with live(console=Console, screen=True, auto_refresh=False) as Live:
				while True:
					Live.update(render.renderDriveInfo(AllDrive=(len(Args.drives) == 0), Volumes=Args.drives if Args.drives else None, Mode=Mode, Sort=Args.sort, Reverse=Args.reverse, filterType=Args.type, Top=Args.top, Percent=Args.usage))
					Live.refresh()
					time.sleep(Args.watch)
		except KeyboardInterrupt:
			Console.print("\n[yellow]Stopping...[/yellow]")
			sys.exit(0)
	else:
		Console.print(render.renderDriveInfo(AllDrive=(len(Args.drives) == 0), Volumes=Args.drives if Args.drives else None, Mode=Mode, Sort=Args.sort, Reverse=Args.reverse, filterType=Args.type, Top=Args.top, Percent=Args.usage))
		sys.exit(0)
if __name__ == "__main__":
	main()