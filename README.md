![DiskInfo](asset/DiskInfo.png)

# DiskInfo
![Version: 3.5](https://img.shields.io/github/v/release/Hoang-Long2012/DiskInfo)
![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue)

A small utility to check basic information about your drive.

---

## Features:
- Drive usage.
- Sort by used/free/total.
- Filter by drive type.
- Watch realtime.
- JSON / Table output.
- Top N drives.
- Usage threshold filter.

---

## Usage:
Usage:  
```
diskinfo [option] [drive...]
```

---

## Examples:

- Show all drive information:
```
diskinfo
```
- Show only drive letters:
```
diskinfo --letter
```
- Show drives in table format:
```
diskinfo --table --simple
```
- Sort drives by used space:
```
diskinfo --sort used
```
- Show the most used drive:
```
diskinfo --sort usage --top 1
```
- Watch drives in real time:
```
diskinfo --watch 1
```
- Show drives with more than 90% usage:
```
diskinfo --usage 90
```
- Export drive information:
```
diskinfo --export report.json
```
- Show JSON output:
```
diskinfo --json
```
- Find full drives and export the result:
```
diskinfo --usage 90 --export full-drives.csv
```
- Monitor USB drives:
```
diskinfo --type usb --watch 5
```
- Show the largest drives:
```
diskinfo --sort total --top 3
```
- Show information about specific drives:
```
diskinfo C: D:
```

---

### Options:  
- -l, /l, --letter  
List all available drives (drive letters only)  
Example: diskinfo -l
- -n, /n, --label  
Show drive labels with drive letters  
Example: diskinfo -n C:\
- --no-bytes  
Hide the bytes in output text mode.  
Example: diskinfo --no-bytes
- -j, /j, --json  
Show drive info with format json.  
Example: diskinfo --json
- --table  
Show drive info with format table.  
Example: diskinfo --table
- --simple  
Show a compact/minimal view of drive information.  
Works with normal and table display modes.  
Example: diskinfo --table --simple
- -s, /s, --sort  
Sort drives by specified field:  
+ Usage  - Used percentage.  
+ Used   - Used space.  
+ Free   - Free space.  
+ Total  - Total capacity.  
Default order: Descending (largest/highest first).  
Example: diskinfo --sort usage
- -r, /r, --reverse  
Reverse sort order (ascending instead of descending).  
Example: diskinfo --sort usage --reverse
- -t, /t, --type  
Filter drives by type.  
Example: diskinfo --type usb
- -w, /w, --watch [SECONDS]  
Watch drives in real time and auto-refresh display.  
SECONDS defines update interval (default: 2).  
Press Ctrl+C to exit watch mode.  
Example: diskinfo --watch 0.5
- -T, /T, --top [NUMBER_OF_DRIVES]  
Show top N drives after sorting.  
Example: diskinfo --sort used --top 1
- -u, /u, --usage [PERCENT]  
Show only drives with some usage.  
Example: diskinfo --usage 90
- --no-sort  
Disable auto sorting of top and usage.  
Example: diskinfo --usage 90 --no-sort
- -S, /S, --summary  
  Show summary information about drives.  
Example: diskinfo --summary
- -E, /E, --exclude [DRIVE...]  
Exclude specific drives.  
Example: diskinfo --exclude C: D:
- -e, /e, --export [FILE]  
Export the output results to a file.  
Supported formats: CSV, JSON, TXT, Markdown, INI, XML, Toml, HTML, XLSX and YAML.  
Example: diskinfo --export report.txt
- -b, /b, --beep  
Beep when have a drive almost full.  
Example: diskinfo --beep
- -v, /v, --version  
Show program version  
- -h, /h, --help  
Show help message  

---

## Notes:
- If no option is provided, the program will display all drive information.
- Valid drive format: C:\, D:/ or E:.
- By default, the drives are arranged in descending order.

---

## Download:
You can install DiskInfo by:
```
winget install HoangLong.DiskInfo
```
Or download from:  
[Release page](https://github.com/Hoang-Long2012/DiskInfo/releases/latest/)  
You can read changelog in:  
[CHANGELOG.md](https://github.com/Hoang-Long2012/DiskInfo/blob/main/CHANGELOG.md)  

---

## Translation:
You can contribute translations to DiskInfo by forking this repo.  
Translating the diskinfo.pot file located in locale.  
Creating a directory representing your language inside locale which creates the LC_MESSAGES directory and dropping the .mo file from the .po file you translated into it.  
Creating a pr to this repo.

---

## Contributing:

Pull requests are welcome.  
Feel free to open issues for bugs or feature requests.

---

## License:
[![MIT License](https://img.shields.io/github/license/Hoang-Long2012/DiskInfo)](LICENSE)

---

© Copyright (c) 2026 Hoang-Long2012