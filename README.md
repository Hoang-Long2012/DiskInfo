# DiskInfo
Name: DiskInfo  
Version: 2.5  
Platform: Windows  
A small utility to check basic information about your drive.
## Features:
- Drive usage.
- Sort by used/free/total.
- Filter by drive type.
- Watch realtime.
- JSON / Table output.
- Top N drives.
- Usage threshold filter.
## Usage:
Usage:  
```
diskinfo [option] [drive...]
```
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
Supported formats: CSV, JSON, TXT, Markdown, INI, XML and Yaml.  
Example: diskinfo --export report.txt
- -v, /v, --version  
Show program version  
- -h, /h, --help  
Show help message  
## Notes:
- If no option is provided, the program will display all drive information.
- Valid drive format: C:\, D:/ or E:.
- By default, the drives are arranged in descending order.
## Download:
Download at:  
https://github.com/Hoang-Long2012/DiskInfo/releases/latest/  
And read changelog at:  
https://github.com/Hoang-Long2012/DiskInfo/blob/main/CHANGELOG.md