![DiskInfo](asset/DiskInfo.png)

# DiskInfo
![Version: 3.5](https://img.shields.io/github/v/release/Hoang-Long2012/DiskInfo)
![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue)
![License: MIT License](https://img.shields.io/github/license/Hoang-Long2012/DiskInfo)

A small utility to check basic information about your drive.

---

## Features:
- Drive usage.
- Sort by used/free/total.
- Filter by drive type.
- Watch drives in real time.
- JSON and table output.
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

- Show the drive using the most space:
```
diskinfo --sort used --top 1
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
Show drive information in JSON format.  
Example: diskinfo --json

- --table  
Show drive information in table format.  
Example: diskinfo --table

- --simple  
Show a compact/minimal view of drive information.  
Works with normal and table display modes.  
Example: diskinfo --table --simple

- -s, /s, --sort [FIELD]  
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

- -t, /t, --type [TYPE]  
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
Show only drives above the specified usage percentage.  
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
Supported formats: CSV, JSON, TXT, Markdown, INI, XML, TOML, HTML, XLSX and YAML.  
Example: diskinfo --export report.txt

- -b, /b, --beep  
Beep when a drive is almost full.  
Example: diskinfo --beep

- -v, /v, --version  
Show program version  

- -h, /h, --help  
Show help message  

---

## Drive Types:

The `--type` option supports the following drive types:

| Type | Aliases |
| --- | --- |
| USB drive | `usb`, `removable` |
| Local disk drive | `local`, `disk`, `fixed` |
| Network drive | `network`, `net` |
| CD/DVD drive | `cd`, `dvd` |
| RAM disk drive | `ram` |
| Unknown | `unknown` |

---

## Usage Status:

Drive usage is categorized as:

| Usage | Status |
| --- | --- |
| 0-79% | 🟢 Healthy |
| 80-89% | 🟡 Warning |
| 90-100% | 🔴 Critical |

---

## Notes:
- If no option is provided, the program will display all drive information.
- Valid drive format: C:\, D:/ or E:.
- By default, the drives are arranged in descending order.
- The export format is detected from the file extension.
- Some system drives may appear as "No root directory".

---

## Download:
You can install DiskInfo by:
```
winget install HoangLong.DiskInfo
```
Or download from:  
[Release page](https://github.com/Hoang-Long2012/DiskInfo/releases/latest/)  
You can read changelog in:  
[CHANGELOG.md](CHANGELOG.md)  

---

## Translation:

You can contribute translations to DiskInfo by:

1. Forking this repository.
2. Translating the `diskinfo.pot` file located in `locale`.
3. Creating a language directory inside `locale` with an `LC_MESSAGES` directory.
4. Adding the generated `.mo` file.
5. Creating a pull request.

---

## Contributing:

Pull requests are welcome.  
Feel free to open issues for bugs or feature requests.

---

## License:
This project is licensed under the:
[MIT License](LICENSE)

---

© Copyright (c) 2026 Hoang-Long2012