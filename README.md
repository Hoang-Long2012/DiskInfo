Version = 1.4
# DiskInfo
Name: DiskInfo  
Version: {{Version}}  
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
Default order: Descending.  
Example: diskinfo --sort usage
- -r, /r, --reverse  
Reverse sort order (ascending instead of descending).  
Example: diskinfo --sort usage --reverse
  - -v, /v, --version  
    Show program version  
  - -h, /h, --help  
    Show this help message  
## Notes:
  - If no option is provided, the program will display all drive information
  - Valid drive format: C:\ or D:
## Download:
Download at:  
https://github.com/NguyenVuHoangLong2012/DiskInfo/releases/latest/
