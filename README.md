# DiskInfo
Name: DiskInfo  
Version: 1.5  
Platform: Windows  
A small utility to check basic information about your drive right in the command line interface.
## Usage:
Usage:  
  diskinfo [option] [drive...]  
### Options:  
- -l, /l, --letter  
    List all available drives (drive letters only)  
    Example: diskinfo -l  
  - -n, /n, --label  
    Show drive labels with drive letters  
    Example: diskinfo.py -n C:\  
      - --json  
    Show drive info with format json.  
Example: diskinfo --json  
  - --table  
    Show drive info with format table.  
    Example: diskinfo --table
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
  - -v, /v, --version  
    Show program version  
  - -h, /h, --help  
    Show this help message  
## Notes:
  - If no option is provided, the program will display all drive information.
  - Valid drive format: C:\ or D:.
  - By default, the drives are arranged in descending order.
## Download:
Download at:  
https://github.com/NguyenVuHoangLong2012/DiskInfo/releases/latest/
