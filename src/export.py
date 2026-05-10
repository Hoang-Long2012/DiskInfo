from data import getData
import csv
import json
import os
import error
def exportCSV(Data, Path):
	if not Data:
		raise error.DataEmptyError(error.DataErrorCode.Invalid_Drives, f"Data is empty or invalid")
	Fields = []
	Seen = set()
	for Item in Data:
		for Key in Item.keys():
			if Key not in Seen:
				Fields.append(Key)
				Seen.add(Key)
	try:
		with open(Path, "w", newline="", encoding="utf-8-sig") as File:
			Writer = csv.DictWriter(File, fieldnames=Fields, delimiter=";")
			Writer.writeheader()
			for Item in Data:
				Writer.writerow({Key: Item.get(Key, "") for Key in Fields})
	except Exception as Error:
		raise error.FileWriteError("Cannot write CSV file") from Error
def exportJSON(Data, Path):
	if not Data:
		raise error.DataEmptyError(error.DataErrorCode.Invalid_Drives, "Data is empty or invalid")
	try:
		with open(Path, "w", encoding="utf-8") as File:
			json.dump(Data, File, indent=2, ensure_ascii=False)
	except Exception as Error:
		raise error.FileWriteError("Cannot write JSON file") from Error
def exportTXT(Data, Path):
	if not Data:
		raise error.DataEmptyError(error.DataErrorCode.Invalid_Drives, "Data is empty or invalid")
	try:
		with open(Path, "w", encoding="utf-8") as File:
			for Item in Data:
				for Key, Value in Item.items():
					File.write(f"{Key}: {Value}\n")
				File.write("\n")
	except Exception as Error:
		raise error.FileWriteError("Cannot write TXT file") from Error
def exportData(Path, AllDrive=True, Volumes=None, Sort=None, Reverse=True, filterType=None, Top=None, Percent=None):
	Data = getData(AllDrive=AllDrive, Volumes=Volumes, Sort=Sort, Reverse=Reverse, filterType=filterType, Top=Top, Percent=Percent)
	Path = os.path.abspath(Path.strip())
	if Path.lower().endswith(".csv"):
		exportCSV(Data, Path)
	elif Path.lower().endswith(".json"):
		exportJSON(Data, Path)
	elif Path.lower().endswith(".txt"):
		exportTXT(Data, Path)
	else:
		raise ValueError("Unsupported format")