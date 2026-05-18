from data import getData
import os
import error
import utils
def validateData(Data):
	if not isinstance(Data, list) or not Data:
		raise error.DataEmptyError(error.DataErrorCode.Invalid_Drives, f"Data is empty or invalid")
def exportCSV(Data, Path):
	import csv
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
	import json
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
	from xml.dom.minidom import parseString
	import dicttoxml
	validateData(Data)
	XML_Bytes = dicttoxml.dicttoxml(Data, custom_root="drives", item_func=lambda x: "disk", attr_type=False)
	Dom = parseString(XML_Bytes)
	Pretty_XML = Dom.toprettyxml(indent="\t")
	try:
		with open(Path, "w", encoding="utf-8") as File:
			File.write(Pretty_XML)
	except Exception as Error:
		raise error.FileWriteError("Cannot write XML file") from Error
def exportYaml(Data, Path):
	import yaml
	validateData(Data)
	try:
		with open(Path, "w", encoding="utf-8") as File:
			yaml.dump(Data, File, allow_unicode=True)
	except Exception as Error:
		raise error.FileWriteError("Cannot write Yaml file") from Error
def exportXLSX(Data, Path):
	from openpyxl import Workbook as workbook
	from openpyxl.styles import Font, Alignment
	validateData(Data)
	try:
		Workbook = workbook()
		Worksheet = Workbook.active
		Worksheet.title = "DiskInfo"
		if not Data:
			Worksheet.append(["No data"])
			Workbook.save(Path)
			return None
		Fields = []
		Seen = set()
		for Item in Data:
			for Key in Item.keys():
				if Key not in Seen:
					Fields.append(Key)
					Seen.add(Key)
		Worksheet.append(Fields)
		for Col in range(1, len(Fields) + 1):
			Cell = Worksheet.cell(row=1, column=Col)
			Cell.font = Font(bold=True)
			Cell.alignment = Alignment(horizontal="center")
		for Item in Data:
			Row = []
			for Key in Fields:
				Value = Item.get(Key, "")
				Row.append(Value)
			Worksheet.append(Row)
		for Col in Worksheet.columns:
			Max_Len = 0
			Col_Letter = Col[0].column_letter
			for Cell in Col:
				try:
					Max_Len = max(Max_Len, len(str(Cell.value)))
				except:
					pass
			Worksheet.column_dimensions[Col_Letter].width = Max_Len + 2
		Workbook.save(Path)
	except Exception as Error:
		raise error.FileWriteError("Cannot write XLSX file") from Error
def exportHTML(Data, Path):
	from jinja2 import Environment, FileSystemLoader
	validateData(Data)
	ENV = Environment(loader=FileSystemLoader(utils.getFilePath("templates")))
	Template = ENV.get_template("template.html")
	HTML = Template.render(data=Data)
	try:
		with open(Path, "w", encoding="utf-8") as File:
			File.write(HTML)
	except Exception as e:
		raise error.FileWriteError("Cannot write HTML file") from e
def exportTOML(Data, Path):
	import toml
	validateData(Data)
	try:
		Output = {
			"drives": Data
		}
		with open(Path, "w", encoding="utf-8") as File:
			toml.dump(Output, File)
	except Exception as Error:
		raise error.FileWriteError("Cannot write TOML file") from Error
Formats = {
	".csv": exportCSV,
	".json": exportJSON,
	".txt": exportTXT,
	".md": exportMarkdown,
	".ini": exportINI,
	".xml": exportXML,
	".yaml": exportYaml,
	".xlsx": exportXLSX,
	".html": exportHTML,
	".toml": exportTOML
}
def exportData(Path, AllDrive=True, Volumes=None, Sort=None, Reverse=True, filterType=None, Top=None, Percent=None, Exclude=None):
	Data = getData(AllDrive=AllDrive, Volumes=Volumes, Sort=Sort, Reverse=Reverse, filterType=filterType, Top=Top, Percent=Percent, Exclude=Exclude)
	Path = os.path.abspath(Path.strip())
	_, Ext = os.path.splitext(Path)
	Exporter = Formats.get(Ext.lower())
	if Exporter:
		Exporter(Data, Path)
	else:
		raise ValueError("Unsupported format")