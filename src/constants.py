Domain = "diskinfo"
def N_(Text):
	return Text
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
Usage_Levels = [
	{
		"min": 90,
		"key": "critical",
		"label": "Critical",
		"icon": "🔴"
	},
	{
		"min": 80,
		"key": "warning",
		"label": "Warning",
		"icon": "🟡"
	},
	{
		"min": 0,
		"key": "healthy",
		"label": "Healthy",
		"icon": "🟢"
	}
]
Sort_Keys = {
	"usage": "percent",
	"used": "used",
	"free": "free",
	"total": "total"
}
CLI_Drive_Icons = {
	"Unknown": "❓",
	"No root directory": "🚫",
	"USB drive": "🔌",
	"Local disk drive": "💽",
	"Network drive": "🌐",
	"CD/DVD drive": "💿",
	"Ram disk drive": "⚡"
}
CLI_FS_Colors = {
	"NTFS": "cyan",
	"FAT32": "yellow",
	"exFAT": "green",
	"FAT": "yellow",
	"ReFS": "bright_cyan",
	"ext2": "green",
	"ext3": "green",
	"ext4": "bright_green",
	"btrfs": "blue",
	"xfs": "bright_blue",
	"zfs": "bright_magenta",
	"HFS": "magenta",
	"HFS+": "bright_magenta",
	"APFS": "bright_white",
	"CDFS": "magenta",
	"UDF": "purple",
	"NFS": "blue",
	"SMB": "bright_blue",
	"RAW": "red",
	"Unknown": "grey50"
}
CLI_Status_Colors = {
	"critical": "red",
	"warning": "yellow",
	"healthy": "green"
}
GUI_Drive_Icons = {
	"USB drive": "SP_DriveFDIcon",
	"Local disk drive": "SP_DriveHDIcon",
	"Network drive": "SP_DriveNetIcon",
	"CD/DVD drive": "SP_DriveCDIcon",
	"Ram disk drive": "SP_DriveHDIcon",
	"Unknown": "SP_DriveHDIcon"
}
GUI_FS_Colors = {
	"NTFS": "#00ffff",
	"FAT32": "#ffff00",
	"EXFAT": "#00ff00",
	"RAW": "#ff0000",
	"Unknown": "#aaaaaa"
}
GUI_Status_Colors = {
	"healthy": "#00cc66",
	"warning": "#ffaa00",
	"critical": "#ff3333"
}
GUI_Headers = {
	"drive": N_("Drive"),
	"label": N_("Label"),
	"type": N_("Type"),
	"fs": N_("File System"),
	"used": N_("Used space"),
	"free": N_("Free space"),
	"total": N_("Capacity"),
	"percent": N_("Usage %"),
	"status": N_("Status")
}
Center_Columns = ["used", "free", "total", "percent", "status"]
Color_Columns = ["used", "free"]
GUI_Simple_Columns = [
	N_("drive"),
	N_("label"),
	N_("percent"),
	N_("status")
]