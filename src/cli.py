from rich.live import Live as live
from rich.console import Console as console
from constants import Type_Alias, Sort_Keys
import render
import export
import error
import sys
import argparse
import time
Console = console()
def getVersion():
	return "3.0"
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
	Console.print("    Example: diskinfo -n C:\\")
	Console.print("")
	Console.print("  --no-bytes")
	Console.print("    Hide the bytes in output text mode.")
	Console.print("    Example: diskinfo --no-bytes")
	Console.print("")
	Console.print("  -j, /j, --json")
	Console.print("    Show drive info with format json.")
	Console.print("    Example: diskinfo --json")
	Console.print("")
	Console.print("  --table")
	Console.print("    Show drive info with format table.")
	Console.print("    Example: diskinfo --table")
	Console.print("")
	Console.print("  --simple")
	Console.print("    Show a compact/minimal view of drive information.")
	Console.print("    Works with normal and table display modes.")
	Console.print("    Example: diskinfo --table --simple")
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
	Console.print("  --no-sort")
	Console.print("    Disable auto sorting of top and usage.")
	Console.print("    Example: diskinfo --usage 90 --no-sort")
	Console.print("")
	Console.print("  -S, /S, --summary")
	Console.print("    Show summary information about drives.")
	Console.print("    Example: diskinfo --summary")
	Console.print("")
	Console.print("  -E, /E, --exclude [DRIVE...]")
	Console.print("    Exclude specific drives.")
	Console.print("    Example: diskinfo --exclude C: D:")
	Console.print("")
	Console.print("  -e, /e, --export [FILE]")
	Console.print("    Export the output results to a file.")
	Console.print("    Supported formats: CSV, JSON, TXT, Markdown, INI, XML, Yaml, XLSX, HTML and TOML.")
	Console.print("    Example: diskinfo --export report.txt")
	Console.print("")
	Console.print("  -b, /b, --beep")
	Console.print("    Beep when have a drive almost full.")
	Console.print("    Example: diskinfo --beep")
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
	Parser.add_argument("--no-bytes", action="store_false", default=True)
	Parser.add_argument("-j", "--json", action="store_true")
	Parser.add_argument("--table", action="store_true")
	Parser.add_argument("--simple", action="store_true")
	Parser.add_argument("-l", "--letter", action="store_true")
	Parser.add_argument("-n", "--label", action="store_true")
	Parser.add_argument("-s", "--sort", choices=sorted(Sort_Keys))
	Parser.add_argument("-r", "--reverse", action="store_false")
	Parser.add_argument("-t", "--type", nargs="+", choices=sorted(Type_Alias))
	Parser.add_argument("-w", "--watch", nargs="?", const=2, type=float, metavar="SECONDS")
	Parser.add_argument("-T", "--top", type=int, metavar="n")
	Parser.add_argument("-u", "--usage", type=float, metavar="PERCENT")
	Parser.add_argument("--no-sort", action="store_true")
	Parser.add_argument("-S", "--summary", action="store_true")
	Parser.add_argument("-E", "--exclude", nargs="+", metavar="DRIVE")
	Parser.add_argument("-e", "--export", type=str, metavar="file")
	Parser.add_argument("-b", "--beep", action="store_true")
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
		if not Args.no_sort:
			Args.sort = "usage"
	elif Args.top and not Args.sort:
		if not Args.no_sort:
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
					Live.update(render.renderDriveInfo(AllDrive=(len(Args.drives) == 0), Volumes=Args.drives if Args.drives else None, Mode=Mode, Sort=Args.sort, Reverse=Args.reverse, filterType=Args.type, Top=Args.top, Percent=Args.usage, Exclude=Args.exclude, Simple=Args.simple, Bytes=Args.no_bytes, Beep=Args.beep))
					Live.refresh()
					time.sleep(Args.watch)
		except KeyboardInterrupt:
			Console.print("\n[yellow]Stopping...[/yellow]")
			sys.exit(0)
	if Args.export:
		try:
			export.exportData(Path=Args.export, AllDrive=(len(Args.drives) == 0), Volumes=Args.drives if Args.drives else None, Sort=Args.sort, Reverse=Args.reverse, filterType=Args.type, Top=Args.top, Percent=Args.usage, Exclude=Args.exclude)
		except ValueError:
			Console.print("Unsupported format")
			sys.exit(2)
		except error.FileWriteError:
			Console.print(f"Cannot write '{Args.export}'")
			sys.exit(2)
		except error.DataEmptyError as Error:
			if Error.code == error.DataErrorCode.Invalid_Drives:
				Console.print("Invalid drives")
				sys.exit(2)
			elif Error.code == error.DataErrorCode.No_Drive:
				Console.print("No drive information")
				sys.exit(2)
		except error.DataOutOfLimitError as Error:
			if Error.code == error.DataErrorCode.Top_Limit:
				Console.print(Error.message)
				sys.exit(2)
			elif Error.code == error.DataErrorCode.Usage_Limit:
				Console.print(Error.message)
				sys.exit(2)
	if Args.summary:
		Console.print(render.renderDriveSummary(AllDrive=(len(Args.drives) == 0), Volumes=Args.drives if Args.drives else None, Sort=Args.sort, Reverse=Args.reverse, filterType=Args.type, Top=Args.top, Percent=Args.usage, Exclude=Args.exclude, Simple=Args.simple, Bytes=Args.no_bytes))
		sys.exit(0)
	else:
		Console.print(render.renderDriveInfo(AllDrive=(len(Args.drives) == 0), Volumes=Args.drives if Args.drives else None, Mode=Mode, Sort=Args.sort, Reverse=Args.reverse, filterType=Args.type, Top=Args.top, Percent=Args.usage, Exclude=Args.exclude, Simple=Args.simple, Bytes=Args.no_bytes, Beep=Args.beep))
		sys.exit(0)
if __name__ == "__main__":
	main()