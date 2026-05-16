from PySide6.QtGui import QColor, QBrush, QDesktopServices, QAction, QActionGroup, QStandardItemModel, QStandardItem
from PySide6.QtCore import QTimer, Qt, QUrl, QFileInfo, QPropertyAnimation, QEasingCurve
from cli import getVersion
from datetime import datetime
import PySide6.QtWidgets as QT
import sys
import data
import export
import error
import constants
import utils
import os
class MainWindow(QT.QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle(f"DiskInfo version {getVersion()}")
		self.resize(900, 500)
		self.Sort = None
		self.Reverse = True
		self.Type = None
		self.Top = None
		self.Percent = None
		self.Current_Timeout = 0
		self.IconProvider = QT.QFileIconProvider()
		self.buildMenu()
		self.buildToolbar()
		self.buildTable()
		self.buildStatusBar()
		self.loadData()
		self.Timer = QTimer()
		self.Timer.timeout.connect(self.refreshData)
	def buildMenu(self):
		self.Menu = self.menuBar()
		self.Menu.setNativeMenuBar(True)
		self.Menu.setFocusPolicy(Qt.NoFocus)
		self.buildFileMenu()
		self.buildViewMenu()
		self.buildHelpMenu()
	def buildFileMenu(self):
		self.File_Menu = self.Menu.addMenu("&File")
		self.Export = QAction("&Export", self.File_Menu)
		self.Export.setShortcut("Ctrl+E")
		self.Export.setIcon(self.style().standardIcon(QT.QStyle.SP_DialogSaveButton))
		self.Export.triggered.connect(self.exportFile)
		self.File_Menu.addAction(self.Export)
		self.Exit = QAction("Exit", self.File_Menu)
		self.Exit.setShortcut("Alt+F4")
		self.Exit.setIcon(self.style().standardIcon(QT.QStyle.SP_DialogCloseButton))
		self.Exit.triggered.connect(self.exitApp)
		self.File_Menu.addAction(self.Exit)
	def buildViewMenu(self):
		self.View_Menu = self.Menu.addMenu("&View")
		self.Refresh = QAction("&Refresh", self.View_Menu)
		self.Refresh.setShortcut("F5")
		self.Refresh.setIcon(self.style().standardIcon(QT.QStyle.SP_BrowserReload))
		self.Refresh.triggered.connect(self.refreshData)
		self.View_Menu.addAction(self.Refresh)
		Sort_By_Menu = QT.QMenu("&Sort by", self.View_Menu)
		Sort_By_Menu.setIcon(self.style().standardIcon(QT.QStyle.SP_FileDialogDetailedView))
		Sort_By_Group = QActionGroup(Sort_By_Menu)
		Sort_By_Group.setExclusive(True)
		Usage = QAction("&Usage", Sort_By_Menu)
		Usage.setCheckable(True)
		Usage.triggered.connect(lambda: self.setSort("usage"))
		Sort_By_Menu.addAction(Usage)
		Sort_By_Group.addAction(Usage)
		Used = QAction("U&sed", Sort_By_Menu)
		Used.setCheckable(True)
		Used.triggered.connect(lambda: self.setSort("used"))
		Sort_By_Menu.addAction(Used)
		Sort_By_Group.addAction(Used)
		Free = QAction("&Free", Sort_By_Menu)
		Free.setCheckable(True)
		Free.triggered.connect(lambda: self.setSort("free"))
		Sort_By_Menu.addAction(Free)
		Sort_By_Group.addAction(Free)
		Total = QAction("&Total", Sort_By_Menu)
		Total.setCheckable(True)
		Total.triggered.connect(lambda: self.setSort("total"))
		Sort_By_Menu.addAction(Total)
		Sort_By_Group.addAction(Total)
		Reverse_Group = QActionGroup(Sort_By_Menu)
		Reverse_Group.setExclusive(True)
		Ascending = QAction("&Ascending", Sort_By_Menu)
		Ascending.setCheckable(True)
		Ascending.triggered.connect(lambda: self.setReverse(False))
		Sort_By_Menu.addAction(Ascending)
		Reverse_Group.addAction(Ascending)
		Descending = QAction("&Descending", Sort_By_Menu)
		Descending.setCheckable(True)
		Descending.setChecked(True)
		Descending.triggered.connect(lambda: self.setReverse(True))
		Sort_By_Menu.addAction(Descending)
		Reverse_Group.addAction(Descending)
		self.View_Menu.addMenu(Sort_By_Menu)
		Type_Menu = QT.QMenu("&Type", self.View_Menu)
		Type_Menu.setIcon(self.style().standardIcon(QT.QStyle.SP_DriveHDIcon))
		Type_Group = QActionGroup(Type_Menu)
		Type_Group.setExclusive(True)
		All = QAction("&All", Type_Menu)
		All.setCheckable(True)
		All.setChecked(True)
		All.triggered.connect(lambda: self.setType(None))
		Type_Menu.addAction(All)
		Type_Group.addAction(All)
		USB = QAction("&USB", Type_Menu)
		USB.setCheckable(True)
		USB.setIcon(self.style().standardIcon(QT.QStyle.SP_DriveFDIcon))
		USB.triggered.connect(lambda: self.setType("usb"))
		Type_Menu.addAction(USB)
		Type_Group.addAction(USB)
		Local_Disk = QAction("&Local disk", Type_Menu)
		Local_Disk.setCheckable(True)
		Local_Disk.setIcon(self.style().standardIcon(QT.QStyle.SP_DriveHDIcon))
		Local_Disk.triggered.connect(lambda: self.setType("disk"))
		Type_Menu.addAction(Local_Disk)
		Type_Group.addAction(Local_Disk)
		Network_Disk = QAction("&Network", Type_Menu)
		Network_Disk.setCheckable(True)
		Network_Disk.setIcon(self.style().standardIcon(QT.QStyle.SP_DriveNetIcon))
		Network_Disk.triggered.connect(lambda: self.setType("network"))
		Type_Menu.addAction(Network_Disk)
		Type_Group.addAction(Network_Disk)
		CD_DVD = QAction("&CD / DVD", Type_Menu)
		CD_DVD.setCheckable(True)
		CD_DVD.setIcon(self.style().standardIcon(QT.QStyle.SP_DriveCDIcon))
		CD_DVD.triggered.connect(lambda: self.setType("cd"))
		Type_Menu.addAction(CD_DVD)
		Type_Group.addAction(CD_DVD)
		Ram_Disk = QAction("&Ram disk", Type_Menu)
		Ram_Disk.setCheckable(True)
		Ram_Disk.setIcon(self.style().standardIcon(QT.QStyle.SP_ComputerIcon))
		Ram_Disk.triggered.connect(lambda: self.setType("ram"))
		Type_Menu.addAction(Ram_Disk)
		Type_Group.addAction(Ram_Disk)
		Unknown = QAction("&Unknown", Type_Menu)
		Unknown.setCheckable(True)
		Unknown.setIcon(self.style().standardIcon(QT.QStyle.SP_MessageBoxQuestion))
		Unknown.triggered.connect(lambda: self.setType("unknown"))
		Type_Menu.addAction(Unknown)
		Type_Group.addAction(Unknown)
		self.View_Menu.addMenu(Type_Menu)
		self.Auto_Refresh = QAction("&Auto refresh", self.View_Menu)
		self.Auto_Refresh.setCheckable(True)
		self.Auto_Refresh.setShortcut("Ctrl+R")
		self.Auto_Refresh.setIcon(self.style().standardIcon(QT.QStyle.SP_MediaPlay))
		self.Auto_Refresh.triggered.connect(self.setTimer)
		self.View_Menu.addAction(self.Auto_Refresh)
		Top = QAction("&Top", self.View_Menu)
		Top.setShortcut("Ctrl+T")
		Top.setIcon(self.style().standardIcon(QT.QStyle.SP_ArrowUp))
		Top.triggered.connect(self.setTop)
		self.View_Menu.addAction(Top)
		Percent = QAction("&Usage", self.View_Menu)
		Percent.setShortcut("Ctrl+U")
		Percent.setIcon(self.style().standardIcon(QT.QStyle.SP_DialogApplyButton))
		Percent.triggered.connect(self.setUsage)
		self.View_Menu.addAction(Percent)
	def buildHelpMenu(self):
		self.Help_Menu = self.Menu.addMenu("&Help")
		About = QAction("&About", self.Help_Menu)
		About.setIcon(self.style().standardIcon(QT.QStyle.SP_MessageBoxInformation))
		About.triggered.connect(self.about)
		self.Help_Menu.addAction(About)
		Readme = QAction("&Readme", self.Help_Menu)
		Readme.setShortcut("F1")
		Readme.setIcon(self.style().standardIcon(QT.QStyle.SP_FileIcon))
		Readme.triggered.connect(self.readme)
		self.Help_Menu.addAction(Readme)
		Changelog = QAction("&Changelog", self.Help_Menu)
		Changelog.setIcon(self.style().standardIcon(QT.QStyle.SP_FileDialogDetailedView))
		Changelog.triggered.connect(self.changelog)
		self.Help_Menu.addAction(Changelog)
		Homepage = QAction("&Homepage", self.Help_Menu)
		Homepage.setIcon(self.style().standardIcon(QT.QStyle.SP_DirLinkIcon))
		Homepage.triggered.connect(self.homepage)
		self.Help_Menu.addAction(Homepage)
		License = QAction("&License", self.Help_Menu)
		License.setIcon(self.style().standardIcon(QT.QStyle.SP_FileDialogInfoView))
		License.triggered.connect(self.license)
		self.Help_Menu.addAction(License)
	def buildToolbar(self):
		self.Toolbar = self.addToolBar("Main")
		self.Toolbar.setFocusPolicy(Qt.NoFocus)
		self.Toolbar.setMovable(False)
		self.Toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		self.Toolbar.addAction(self.Refresh)
		self.Toolbar.addAction(self.Export)
		self.Toolbar.addAction(self.Exit)
		self.Toolbar.addSeparator()
		self.Toolbar.addAction(self.Auto_Refresh)
	def buildStatusBar(self):
		self.Status = self.statusBar()
		self.Drive_Label = QT.QLabel("Drives: 0")
		self.Total_Label = QT.QLabel("Total: 0")
		self.Used_Label = QT.QLabel("Used: 0")
		self.Free_Label = QT.QLabel("Free: 0")
		self.Filter_Label = QT.QLabel("Filter: All")
		self.Auto_Label = QT.QLabel("Auto refresh: Off")
		self.Timeout_Label = QT.QLabel("Timeout: Disabled")
		self.Refresh_Label = QT.QLabel("Last refresh: Never")
		self.Status.addPermanentWidget(self.Drive_Label)
		self.Status.addPermanentWidget(self.Total_Label)
		self.Status.addPermanentWidget(self.Used_Label)
		self.Status.addPermanentWidget(self.Free_Label)
		self.Status.addPermanentWidget(self.Filter_Label)
		self.Status.addPermanentWidget(self.Auto_Label)
		self.Status.addPermanentWidget(self.Timeout_Label)
		self.Status.addPermanentWidget(self.Refresh_Label)
	def buildTable(self):
		self.Table = QT.QTableView()
		self.Model = AccessibleModel()
		self.Table.setModel(self.Model)
		self.Table.setSortingEnabled(False)
		self.Table.setAlternatingRowColors(True)
		self.Table.setSelectionBehavior(QT.QAbstractItemView.SelectRows)
		self.Table.setEditTriggers(QT.QAbstractItemView.NoEditTriggers)
		self.Table.setFocusPolicy(Qt.StrongFocus)
		self.Table.setTabKeyNavigation(True)
		self.Table.setContextMenuPolicy(Qt.CustomContextMenu)
		self.Table.customContextMenuRequested.connect(self.showContextMenu)
		self.Table.setStyleSheet("""
			QHeaderView::section {
				background:#202020;
				color:white;
				padding:6px;
				border:1px solid #333;
				font-weight:bold;
			}
		""")
		self.Table.setAlternatingRowColors(True)
		self.Table.setStyleSheet(self.Table.styleSheet() + """
			QTableView {
				gridline-color:#444;
				alternate-background-color:#1e1e1e;
				background:#121212;
				color:white;
				selection-background-color:#0078d7;
			}
			QTableView::item:hover {
				background:#2a2a2a;
			}
		""")
		self.Table.setAccessibleName("Drive info")
		self.Header = self.Table.horizontalHeader()
		self.Header.setSectionResizeMode(QT.QHeaderView.ResizeToContents)
		self.Header.setStretchLastSection(True)
		self.Header.setDefaultAlignment(Qt.AlignCenter)
		self.Header.setHighlightSections(False)
		self.Header.sectionClicked.connect(self.onHeaderClicked)
		self.Header.setSortIndicatorShown(True)
		self.Header.setAccessibleName("Header")
		self.setCentralWidget(self.Table)
		self.Opacity = QT.QGraphicsOpacityEffect()
		self.Table.setGraphicsEffect(self.Opacity)
		self.Fade_Animation = QPropertyAnimation(self.Opacity, b"opacity")
		self.Fade_Animation.setDuration(250)
		self.Fade_Animation.setEasingCurve(QEasingCurve.InOutQuad)
	def animateRefresh(self):
		self.Fade_Animation.stop()
		self.Fade_Animation.setStartValue(0.3)
		self.Fade_Animation.setEndValue(1.0)
		self.Fade_Animation.start()
	def loadData(self, Sort=None, Reverse=True, Type=None, Top=None, Percent=None):
		Datas = None
		try:
			Datas = data.getData(Sort=Sort, Reverse=Reverse, filterType=[Type] if Type else None, Top=Top, Percent=Percent)
		except error.DataEmptyError as Error:
			if Error.code == error.DataErrorCode.Invalid_Drives:
				QT.QMessageBox.critical(self, "Error", "Invalid drives")
			elif Error.code == error.DataErrorCode.No_Drive:
				QT.QMessageBox.critical(self, "Error", "No drive information")
		except error.DataOutOfLimitError as Error:
			if Error.code == error.DataErrorCode.Top_Limit:
				QT.QMessageBox.critical(self, "Error", Error.message)
			elif Error.code == error.DataErrorCode.Usage_Limit:
				QT.QMessageBox.critical(self, "Error", Error.message)
		if not Datas:
			self.Model.clear()
			return None
		self.fillModel(Datas)
	def makeCell(self, Key, Value, RowData):
		Text = "" if Value is None else str(Value)
		Cell = QStandardItem(Text)
		Style = utils.getUsageStyle(RowData.get("percent"), "gui")
		if Key == "drive":
			Icon = self.IconProvider.icon(QFileInfo(str(Value)))
			Cell.setIcon(Icon)
			Cell.setForeground(QBrush(QColor(Style["color"])))
			Cell.setText(Text.replace("\\", ""))
		elif Key == "fs":
			Color = utils.getFsColor(Value, "gui")
			Cell.setForeground(QBrush(QColor(Color)))
		elif Key == "status":
			Cell.setForeground(QBrush(QColor(Style["color"])))
		elif Key == "percent":
			Percent = int(Value)
			Cell.setForeground(QBrush(QColor(Style["color"])))
			Cell.setData(Percent, Qt.UserRole)
			Cell.setData(Style["color"], Qt.UserRole + 1)
			Cell.setText(f"{Percent:.0f}%")
		elif Key in constants.Color_Columns:
			Cell.setForeground(QBrush(QColor(Style["color"])))
			Cell.setText(f"{utils.formatSize(Value)} ({Value} Bytes)")
		elif Key == "total":
			Cell.setText(f"{utils.formatSize(Value)} ({Value} Bytes)")
		if Key in constants.Center_Columns:
			Cell.setTextAlignment(Qt.AlignCenter)
		return Cell
	def createProgressBar(self, Item):
		Value = Item.data(Qt.UserRole) or 0
		Color = Item.data(Qt.UserRole + 1) or "#00aa55"
		Bar = AnimatedProgressBar()
		Bar.setRange(0, 100)
		Bar.setValue(Value)
		Bar.setFormat(f"{Value}%")
		Bar.setTextVisible(True)
		Bar.setAlignment(Qt.AlignCenter)
		Bar.setFocusPolicy(Qt.StrongFocus)
		Bar.setEnabled(True)
		Bar.setAccessibleName("Usage")
		Bar.setAccessibleDescription(f"{Value} percent used")
		Bar.setStyleSheet(f"""
			QProgressBar {{
				border:1px solid #666;
				border-radius:4px;
				text-align:center;
				background:#1e1e1e;
			}}
			QProgressBar::chunk {{
				background:{Color};
			}}
		""")
		return Bar
	def fillModel(self, Datas):
		self.Model.clear()
		if not Datas:
			return None
		self.Drive_Label.setText(f"Drives: {len(Datas)}")
		Total_Size = sum(Item.get("total", 0) for Item in Datas)
		self.Total_Label.setText(f"Total: {utils.formatSize(Total_Size)}")
		Used_Size = sum(Item.get("used", 0) for Item in Datas)
		self.Used_Label.setText(f"Used: {utils.formatSize(Used_Size)}")
		Free_Size = sum(Item.get("free", 0) for Item in Datas)
		self.Free_Label.setText(f"Free: {utils.formatSize(Free_Size)}")
		self.Columns = []
		Seen = set()
		for Item in Datas:
			for Key in Item.keys():
				if Key not in Seen:
					Seen.add(Key)
					self.Columns.append(Key)
		self.Headers = [constants.GUI_Headers.get(Key, Key.replace("_", " ").title()) for Key in self.Columns]
		self.Model.setHorizontalHeaderLabels(self.Headers)
		for RowIndex, Item in enumerate(Datas):
			Row = []
			for Key in self.Columns:
				Value = Item.get(Key, "")
				Row.append(self.makeCell(Key, Value, Item))
			self.Model.appendRow(Row)
			if "percent" in self.Columns:
				Col = self.Columns.index("percent")
				Item = Row[Col]
				Index = self.Model.index(RowIndex, Col)
				self.Table.setIndexWidget(Index, self.createProgressBar(Item))
		self.Table.resizeColumnsToContents()
	def refreshData(self):
		self.animateRefresh()
		self.loadData(self.Sort, self.Reverse, self.Type, self.Top, self.Percent)
		self.updateLastRefresh()
	def updateLastRefresh(self):
		Time = datetime.now().strftime("%H:%M:%S")
		self.Refresh_Label.setText(f"Last refresh: {Time}")
	def showContextMenu(self, Pos):
		Menu = QT.QMenu(self)
		Copy_Cell = QAction("Copy Cell", self)
		Copy_Row = QAction("Copy Row", self)
		Copy_Column = QAction("Copy Column", self)
		Copy_Cell.triggered.connect(self.copyCell)
		Copy_Row.triggered.connect(self.copyRow)
		Copy_Column.triggered.connect(self.copyColumn)
		Menu.addAction(Copy_Cell)
		Menu.addAction(Copy_Row)
		Menu.addAction(Copy_Column)
		Menu.addAction(self.Export)
		Menu.exec(self.Table.viewport().mapToGlobal(Pos))
	def onHeaderClicked(self, Index):
		Key = self.Columns[Index]
		if not Key:
			return None
		if self.Sort == Key:
			self.Reverse = not self.Reverse
		else:
			self.Sort = Key
			self.Reverse = True
		self.Header.setSortIndicator(Index, Qt.DescendingOrder if self.Reverse else Qt.AscendingOrder)
		self.refreshData()
	def exitApp(self):
		self.close()
	def setSort(self, mode):
		self.Sort = mode
		self.refreshData()
	def setReverse(self, value):
		self.Reverse = value
		self.refreshData()
	def setType(self, mode):
		Text = mode.title() if mode else "All"
		self.Type = mode
		self.refreshData()
		self.Filter_Label.setText(f"Filter: {Text}")
	def setTop(self):
		Input, OK = QT.QInputDialog.getInt(self, "Top", "Top drives:", 5, 0, 100)
		if OK:
			if Input == 0:
				self.Top = None
			else:
				self.Top = Input
			self.refreshData()
	def setUsage(self):
		Input, OK = QT.QInputDialog.getDouble(self, "Usage", "Minimum usage %:", 90, 0, 100, 2)
		if OK:
			if Input == 0:
				self.Percent = None
			else:
				self.Percent = Input
			self.refreshData()
	def setTimer(self):
		Input, OK = QT.QInputDialog.getDouble(self, "Auto refresh", "Seconds:", 2, 0, 60, 2)
		if OK:
			self.Current_Timeout = Input
			if Input == 0:
				self.Timer.stop()
				self.updateAutoActions(False)
			else:
				if self.Timer.isActive():
					self.Timer.stop()
				self.Timer.start(int(Input * 1000))
				self.updateAutoActions(True)
		else:
			self.updateAutoActions(self.Timer.isActive())
	def updateAutoActions(self, Enabled):
		Icon = QT.QStyle.SP_MediaPause if Enabled else QT.QStyle.SP_MediaPlay
		Text = "On" if Enabled else "Off"
		self.Auto_Refresh.setChecked(Enabled)
		self.Auto_Refresh.setIcon(self.style().standardIcon(Icon))
		self.Auto_Label.setText(f"Auto refresh: {Text}")
		if not self.Current_Timeout == 0:
			self.Timeout_Label.setText(f"Timeout: {self.Current_Timeout:g}s")
		else:
			self.Timeout_Label.setText(f"Timeout: Disabled")
	def exportFile(self):
		Path, File_Type = QT.QFileDialog.getSaveFileName(self, "Export", "Report.txt", "Text Files (*.txt);;CSV Files (*.csv);;JSON Files (*.json);;Markdown Files (*.md);;INI Files (*.ini);;XML Files (*.xml);;Yaml Files (*.yaml);;Excel Files (*.xlsx)", "Text Files (*.txt)")
		if not Path:
			return None
		Ext = File_Type.split("*")[-1].replace(")", "")
		if not Path.lower().endswith(Ext):
			Path += Ext
		try:
			export.exportData(Path, Sort=self.Sort, Reverse=self.Reverse, filterType=[self.Type] if self.Type else None, Top=self.Top, Percent=self.Percent)
			QT.QMessageBox.information(self, "Success", f"Export completed.\nExported to {Path}")
		except ValueError:
			QT.QMessageBox.critical(self, "Error", "Unsupported format")
		except error.FileWriteError:
			QT.QMessageBox.critical(self, "Error", f"Cannot write {Path}")
		except error.DataEmptyError as Error:
			if Error.code == error.DataErrorCode.Invalid_Drives:
				QT.QMessageBox.critical(self, "Error", "Invalid drives")
			elif Error.code == error.DataErrorCode.No_Drive:
				QT.QMessageBox.critical(self, "Error", "No drive information")
		except error.DataOutOfLimitError as Error:
			if Error.code == error.DataErrorCode.Top_Limit:
				QT.QMessageBox.critical(self, "Error", Error.message)
			elif Error.code == error.DataErrorCode.Usage_Limit:
				QT.QMessageBox.critical(self, "Error", Error.message)
	def homepage(self):
		QDesktopServices.openUrl(QUrl("https://github.com/Hoang-Long2012/DiskInfo"))
	def readme(self):
		try:
			os.startfile(utils.getFilePath("README.MD"))
		except Exception:
			QT.QMessageBox.warning(self, "Error", "Cannot open README.md")
	def changelog(self):
		try:
			os.startfile(utils.getFilePath("CHANGELOG.MD"))
		except Exception:
			QT.QMessageBox.warning(self, "Error", "Cannot open CHANGELOG.md")
	def license(self):
		try:
			os.startfile(utils.getFilePath("LICENSE"))
		except Exception:
			QT.QMessageBox.warning(self, "Error", "Cannot open LICENSE")
	def about(self):
		Box = QT.QMessageBox(self)
		Box.setWindowTitle("About DiskInfo")
		Box.setIcon(QT.QMessageBox.Information)
		Box.setTextFormat(Qt.RichText)
		Box.setText(
			f"""
<h2>DiskInfo {getVersion()}</h2>
<p>Simple disk information viewer for Windows.</p>
<p><b>Author:</b> Hoang Long</p>
<p>
<a href="https://github.com/Hoang-Long2012/DiskInfo">
Project Homepage
</a>
</p>
"""
		)
		Box.setStandardButtons(QT.QMessageBox.Ok)
		Box.exec()
	def copyCell(self):
		Index = self.Table.selectionModel().currentIndex()
		if not Index.isValid():
			return None
		Text = "" if Index.data() is None else Index.data()
		QT.QApplication.clipboard().setText(str(Text))
	def copyRow(self):
		Index = self.Table.selectionModel().currentIndex()
		if not Index.isValid():
			return None
		Row = Index.row()
		Col_Count = self.Model.columnCount()
		Values = []
		for Col in range(Col_Count):
			I = self.Model.index(Row, Col)
			Values.append("" if I.data() is None else str(I.data()))
		QT.QApplication.clipboard().setText("\t".join(Values))
	def copyColumn(self):
		Index = self.Table.selectionModel().currentIndex()
		if not Index.isValid():
			return None
		Col = Index.column()
		Row_Count = self.Model.rowCount()
		Values = []
		for Row in range(Row_Count):
			I = self.Model.index(Row, Col)
			Values.append("" if I.data() is None else str(I.data()))
		QT.QApplication.clipboard().setText("\n".join(Values))
class AccessibleModel(QStandardItemModel):
	def data(self, Index, Role):
		if not Index.isValid():
			return super().data(Index, Role)
		if Role == Qt.AccessibleTextRole:
			Header = self.headerData(Index.column(), Qt.Horizontal, Qt.DisplayRole)
			Value = super().data(Index, Qt.DisplayRole)
			if Header and Value:
				return f"{Header}: {Value}"
			return Value
		return super().data(Index, Role)
class AnimatedProgressBar(QT.QProgressBar):
	def __init__(self):
		super().__init__()
		self.Animation = QPropertyAnimation(self, b"value")
		self.Animation.setDuration(400)
		self.Animation.setEasingCurve(QEasingCurve.OutCubic)
	def setAnimatedValue(self, Value):
		self.Animation.stop()
		self.Animation.setStartValue(self.value())
		self.Animation.setEndValue(Value)
		self.Animation.start()
def main():
	App = QT.QApplication(sys.argv)
	App.setApplicationName("DiskInfo")
	App.setApplicationVersion(getVersion())
	Window = MainWindow()
	Window.show()
	Window.raise_()
	Window.activateWindow()
	Window.Table.setFocus()
	sys.exit(App.exec())
if __name__ == "__main__":
	main()