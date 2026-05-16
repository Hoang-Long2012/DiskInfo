from data import getData
from xml.dom.minidom import parseString
import csv
import json
import dicttoxml
import yaml
import os
import error
def validateData(Data):
	if not isinstance(Data, list) or not Data:
		raise error.DataEmptyError(error.DataErrorCode.Invalid_Drives, f"Data is empty or invalid")
def exportCSV(Data, Path):
	validateData(Data)
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
	validateData(Data)
	try:
		with open(Path, "w", encoding="utf-8") as File:
			json.dump(Data, File, indent=2, ensure_ascii=False)
	except Exception as Error:
		raise error.FileWriteError("Cannot write JSON file") from Error
def exportTXT(Data, Path):
	validateData(Data)
	try:
		with open(Path, "w", encoding="utf-8") as File:
			for Item in Data:
				for Key, Value in Item.items():
					File.write(f"{Key}: {Value}\n")
				File.write("\n")
	except Exception as Error:
		raise error.FileWriteError("Cannot write TXT file") from Error
def exportMarkdown(Data, Path):
	validateData(Data)
	try:
		with open(Path, "w", encoding="utf-8") as File:
			for Item in Data:
				Drive = (Item.get("drive") or "Unknown").replace("\\", "")
				File.write(f"# {Drive}\n")
				for Key, Value in Item.items():
					if Key == "drive":
						continue
					File.write(f"- {Key}: {Value}  \n")
				File.write("\n")
	except Exception as Error:
		raise error.FileWriteError("Cannot write Markdown file") from Error
def exportINI(Data, Path):
	validateData(Data)
	try:
		with open(Path, "w", encoding="utf-8") as File:
			for Item in Data:
				Drive = (Item.get("drive") or "Unknown").replace("\\", "")
				File.write(f"[{Drive}]\n")
				for Key, Value in Item.items():
					if Key == "drive":
						continue
					File.write(f"{Key}={Value}\n")
				File.write("\n")
	except Exception as Error:
		raise error.FileWriteError("Cannot write INI file") from Error
def exportXML(Data, Path):
	validateData(Data)
	XML_Bytes = dicttoxml.dicttoxml(Data, custom_root="drives", item_func=lambda x: "disk", attr_type=False)
	Dom = parseString(XML_Bytes)
	Pretty_XML = Dom.toprettyxml(indent="\t")
	try:
		with open(Path, "w", encoding="utf-8") as File:
			File.write(Pretty_XML)
	except Exception as Error:
		raise error.FileWriteError("Cannot write INI file") from Error
def exportYaml(Data, Path):
	validateData(Data)
	try:
		with open(Path, "w", encoding="utf-8") as File:
			yaml.dump(Data, File, allow_unicode=True)
	except Exception as Error:
		raise error.FileWriteError("Cannot write INI file") from Error
Formats = {
	".csv": exportCSV,
	".json": exportJSON,
	".txt": exportTXT,
	".md": exportMarkdown,
	".ini": exportINI,
	".xml": exportXML,
	".yaml": exportYaml
}
def exportData(Path, AllDrive=True, Volumes=None, Sort=None, Reverse=True, filterType=None, Top=None, Percent=None):
	Data = getData(AllDrive=AllDrive, Volumes=Volumes, Sort=Sort, Reverse=Reverse, filterType=filterType, Top=Top, Percent=Percent)
	Path = os.path.abspath(Path.strip())
	_, Ext = os.path.splitext(Path)
	Exporter = Formats.get(Ext.lower())
	if Exporter:
		Exporter(Data, Path)
	else:
		raise ValueError("Unsupported format")