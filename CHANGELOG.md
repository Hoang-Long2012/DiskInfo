# Changelog

## DiskInfo version 2.5
- Made some internal code modifications.
- Added --no-bytes to hide bytes values ​​in output text mode.

---

## DiskInfo version 2.4
- Add support for TOML export format.

---

## DiskInfo version 2.3
- Add HTML export format support.

---

## DiskInfo version 2.2
- Add status bar to gui.
- Add simple display mode to the gui.
- Improved gui accessibility.

---

## DiskInfo version 2.1
- Add support for export format XLSX (Excel file).
- Improved gui accessibility.

---

## DiskInfo version 2.0
- Add XML and Yaml format support for export.
- Improved output with --simple.

---

## DiskInfo version 1.9
- Added gui, you can now view information about your drive by running the DiskInfo_GUI.exe file in the folder you extracted from the zip file below.
- Added new export formats, added Markdown and INI.
- Improved output text mode.
- Added --simple You can now only view the absolutely necessary parameters about your drive using --simple. Currently --simple works with text mode and table mode.

---

## DiskInfo version 1.8
- Improved output text mode.
- Add --no-sort, you can now use --no-sort to disable auto sorting of top and usage.
- Add -i, /i, --export, you can now export your output to a file. Supported formats are txt, json and csv, more formats will be possible in the future.

---

## DiskInfo version 1.7
- Refactored codebase into modular architecture
- Improved maintainability and cleaner internal structure
- Added usage progress bars in text view
- Added usage progress bars in table view
- Improved output layout and spacing
- Added filesystem color highlighting
- Better foundation for future updates

---

## DiskInfo version 1.6
- Added -T; /T; --top to show top N drives after sorting.
- Added -u; /u; --usage to filter drives by used percentage.
- Added drive health status: Healthy, Warning, Critical.
- Added drive type icons for clearer output.
- Improved auto sorting when using --top or --usage.
- Improved table and normal output formatting.
- Improved validation and error handling.
- Code cleanup and internal improvements.

---

## DiskInfo version 1.5
- Add -t; /t; --type, you can now select the drive types you want to see with -t; /t; --type.
- Add -w; /w; --watch, when using -w; /w; --watch DiskInfo will after a certain amount of time can be specified with -w; /w; --watch seconds (default is 2) rechecks information of existing or specified drives. To stop this you can use Control+C.
- Improved output, now the output of both json, table and regular text is nicer and easier to read.

---

## DiskInfo version 1.4
- Removed -i; /i; --info, you can now use diskinfo [drives...] directly.
- Improved the table format of --table, now the table of --table displays better and only displays necessary information.
- Fixed --table's table overflowing when displayed.
- Improved output, DiskInfo output is now nicer and easier to understand.
- Added -s; /S; --sort, you can now customize how DiskInfo sorts drives by usage, used, free or total. The default is to sort in descending order.
- Added -r; /r; --reverse to reverse the sort order of the drives.

---

## DiskInfo version 1.3
- Clean and improve code.
- Added --json, you can now use --json to display output in json format.
- Added --table, you can now use --table to display output in table format.

---

## DiskInfo version 1.2
- DiskInfo now automatically highlights drives that are 90% or more used in red, yellow for drives that are 80% or more, and green for drives that are 80% or less.

---

## DiskInfo version 1.1
- Added --label, --letter their functions are similar to -l, /l and -n /n.
- Added -i, /i, --info, you can now view single or multiple drive information using diskinfo -i [drive...].
- You can now view the label or letter of a given drive or drives using diskinfo -n [drive...] and diskinfo -l [drive...].
- Added -v, /v, --version and -h, /h, --help.

---

## DiskInfo 1.0
- First release version.