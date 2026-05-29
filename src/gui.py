from PySide6.QtGui import QColor, QBrush, QDesktopServices, QAction, QActionGroup, QStandardItemModel, QStandardItem, QAccessible
from PySide6.QtCore import QTimer, Qt, QUrl, QFileInfo, QPropertyAnimation, QEasingCurve, QEvent
from cli import getVersion
from datetime import datetime
from i18n import loadLanguages, InitTranslation, loadLanguage, saveLanguage
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
		Language = None
		try:
			Language = loadLanguage()
		except Exception as Error:
			Lang_Path = utils.getFilePath("lang.txt")
			QT.QMessageBox.critical(self, "Error", f"Cannot load {Lang_Path}\n{Error}")
		self._ = lambda s, **kwargs: s.format(**kwargs)
		try:
			if Language:
				self.Translation = InitTranslation(Language)
				self._ = self.Translation.translate
		except Exception as Error:
			Locale_Path = utils.getFilePath("locale")
			QT.QMessageBox.critical(self, "Error", f"Cannot load {Locale_Path}\n{Error}")
		self.setWindowTitle(self._("DiskInfo version {version}", version=getVersion()))
		self.resize(900, 500)
		self.Sort = None
		self.Reverse = True
		self.Type = None
		self.Top = None
		self.Percent = None
		self.Simple = False
		self.Bytes = True
		self.Current_Timeout = 0
		self.IconProvider = QT.QFileIconProvider()
		self.buildMenu()
		self.buildToolbar()
		self.buildTable()
		self.buildStatusBar()
		self.loadData()
		self.Timer = QTimer()
		self.Timer.timeout.connect(self.refreshData)
	def keyPressEvent(self, Event):
		if Event.key() == Qt.Key_F6:
			self.Toolbar.setFocus()
			Actions = self.Toolbar.actions()
			if Actions:
				Button = self.Toolbar.widgetForAction(Actions[0])
				if Button:
					Button.setFocus()
			return None
		elif Event.key() == Qt.Key_Escape:
			self.Table.setFocus()
			return None
		super().keyPressEvent(Event)
	def eventFilter(self, Object, Event):
		if Event.type() == QEvent.KeyPress:
			if Event.key() in (Qt.Key_Return, Qt.Key_Enter):
				if isinstance(Object, QT.QToolButton):
					Object.click()
					return True
		return super().eventFilter(Object, Event)
	def buildMenu(self):
		self.Menu = self.menuBar()
		self.Menu.setNativeMenuBar(True)
		self.Menu.setFocusPolicy(Qt.StrongFocus)
		self.Menu.setVisible(True)
		self.buildFileMenu()
		self.buildViewMenu()
		self.buildHelpMenu()
	def createExportAction(self, Parent):
		Action = QAction(self._("Export"), Parent)
		Action.setIcon(self.Export.icon())
		Action.setShortcut(self.Export.shortcut())
		Action.triggered.connect(self.exportFile)
		return Action
	def buildFileMenu(self):
		self.File_Menu = self.Menu.addMenu(self._("&File"))
		self.Export = QAction(self._("&Export"), self)
		self.Export.setShortcut("Ctrl+E")
		self.Export.setIcon(self.style().standardIcon(QT.QStyle.SP_DialogSaveButton))
		self.Export.triggered.connect(self.exportFile)
		self.File_Menu.addAction(self.Export)
		self.Exit = QAction(self._("&Exit"), self)
		self.Exit.setShortcut("Alt+F4")
		self.Exit.setIcon(self.style().standardIcon(QT.QStyle.SP_DialogCloseButton))
		self.Exit.triggered.connect(self.exitApp)
		self.File_Menu.addAction(self.Exit)
	def buildViewMenu(self):
		self.View_Menu = self.Menu.addMenu(self._("&View"))
		self.Refresh = QAction(self._("&Refresh"), self)
		self.Refresh.setShortcut("F5")
		self.Refresh.setIcon(self.style().standardIcon(QT.QStyle.SP_BrowserReload))
		self.Refresh.triggered.connect(self.refreshData)
		self.View_Menu.addAction(self.Refresh)
		Sort_By_Menu = QT.QMenu(self._("&Sort by"), self.View_Menu)
		Sort_By_Menu.setIcon(self.style().standardIcon(QT.QStyle.SP_FileDialogDetailedView))
		Sort_By_Group = QActionGroup(Sort_By_Menu)
		Sort_By_Group.setExclusive(True)
		Usage = QAction(self._("&Usage"), Sort_By_Menu)
		Usage.setCheckable(True)
		Usage.triggered.connect(lambda: self.setSort("usage"))
		Sort_By_Menu.addAction(Usage)
		Sort_By_Group.addAction(Usage)
		Used = QAction(self._("&Used"), Sort_By_Menu)
		Used.setCheckable(True)
		Used.triggered.connect(lambda: self.setSort("used"))
		Sort_By_Menu.addAction(Used)
		Sort_By_Group.addAction(Used)
		Free = QAction(self._("&Free"), Sort_By_Menu)
		Free.setCheckable(True)
		Free.triggered.connect(lambda: self.setSort("free"))
		Sort_By_Menu.addAction(Free)
		Sort_By_Group.addAction(Free)
		Total = QAction(self._("&Total"), Sort_By_Menu)
		Total.setCheckable(True)
		Total.triggered.connect(lambda: self.setSort("total"))
		Sort_By_Menu.addAction(Total)
		Sort_By_Group.addAction(Total)
		Reverse_Group = QActionGroup(Sort_By_Menu)
		Reverse_Group.setExclusive(True)
		Ascending = QAction(self._("&Ascending"), Sort_By_Menu)
		Ascending.setCheckable(True)
		Ascending.triggered.connect(lambda: self.setReverse(False))
		Sort_By_Menu.addAction(Ascending)
		Reverse_Group.addAction(Ascending)
		Descending = QAction(self._("&Descending"), Sort_By_Menu)
		Descending.setCheckable(True)
		Descending.setChecked(True)
		Descending.triggered.connect(lambda: self.setReverse(True))
		Sort_By_Menu.addAction(Descending)
		Reverse_Group.addAction(Descending)
		self.View_Menu.addMenu(Sort_By_Menu)
		Type_Menu = QT.QMenu(self._("&Type"), self.View_Menu)
		Type_Menu.setIcon(self.style().standardIcon(QT.QStyle.SP_DriveHDIcon))
		Type_Group = QActionGroup(Type_Menu)
		Type_Group.setExclusive(True)
		All = QAction(self._("&All"), Type_Menu)
		All.setCheckable(True)
		All.setChecked(True)
		All.triggered.connect(lambda: self.setType(None))
		Type_Menu.addAction(All)
		Type_Group.addAction(All)
		USB = QAction(self._("&USB"), Type_Menu)
		USB.setCheckable(True)
		USB.setIcon(self.style().standardIcon(QT.QStyle.SP_DriveFDIcon))
		USB.triggered.connect(lambda: self.setType("usb"))
		Type_Menu.addAction(USB)
		Type_Group.addAction(USB)
		Local_Disk = QAction(self._("&Local disk"), Type_Menu)
		Local_Disk.setCheckable(True)
		Local_Disk.setIcon(self.style().standardIcon(QT.QStyle.SP_DriveHDIcon))
		Local_Disk.triggered.connect(lambda: self.setType("disk"))
		Type_Menu.addAction(Local_Disk)
		Type_Group.addAction(Local_Disk)
		Network_Disk = QAction(self._("&Network disk"), Type_Menu)
		Network_Disk.setCheckable(True)
		Network_Disk.setIcon(self.style().standardIcon(QT.QStyle.SP_DriveNetIcon))
		Network_Disk.triggered.connect(lambda: self.setType("network"))
		Type_Menu.addAction(Network_Disk)
		Type_Group.addAction(Network_Disk)
		CD_DVD = QAction(self._("&CD / DVD Drive"), Type_Menu)
		CD_DVD.setCheckable(True)
		CD_DVD.setIcon(self.style().standardIcon(QT.QStyle.SP_DriveCDIcon))
		CD_DVD.triggered.connect(lambda: self.setType("cd"))
		Type_Menu.addAction(CD_DVD)
		Type_Group.addAction(CD_DVD)
		Ram_Disk = QAction(self._("&Ram disk"), Type_Menu)
		Ram_Disk.setCheckable(True)
		Ram_Disk.setIcon(self.style().standardIcon(QT.QStyle.SP_ComputerIcon))
		Ram_Disk.triggered.connect(lambda: self.setType("ram"))
		Type_Menu.addAction(Ram_Disk)
		Type_Group.addAction(Ram_Disk)
		Unknown = QAction(self._("&Unknown"), Type_Menu)
		Unknown.setCheckable(True)
		Unknown.setIcon(self.style().standardIcon(QT.QStyle.SP_MessageBoxQuestion))
		Unknown.triggered.connect(lambda: self.setType("unknown"))
		Type_Menu.addAction(Unknown)
		Type_Group.addAction(Unknown)
		self.View_Menu.addMenu(Type_Menu)
		self.Auto_Refresh = QAction(self._("&Auto refresh"), self)
		self.Auto_Refresh.setCheckable(True)
		self.Auto_Refresh.setShortcut("Ctrl+R")
		self.Auto_Refresh.setIcon(self.style().standardIcon(QT.QStyle.SP_MediaPlay))
		self.Auto_Refresh.triggered.connect(self.setTimer)
		self.View_Menu.addAction(self.Auto_Refresh)
		Top = QAction(self._("&Top"), self.View_Menu)
		Top.setShortcut("Ctrl+T")
		Top.setIcon(self.style().standardIcon(QT.QStyle.SP_ArrowUp))
		Top.triggered.connect(self.setTop)
		self.View_Menu.addAction(Top)
		Percent = QAction(self._("&Usage"), self.View_Menu)
		Percent.setShortcut("Ctrl+U")
		Percent.setIcon(self.style().standardIcon(QT.QStyle.SP_DialogApplyButton))
		Percent.triggered.connect(self.setUsage)
		self.View_Menu.addAction(Percent)
		self.Simple_Mode = QAction(self._("&Simple"), self)
		self.Simple_Mode.setShortcut("F8")
		self.Simple_Mode.setCheckable(True)
		self.Simple_Mode.setIcon(self.style().standardIcon(QT.QStyle.SP_FileDialogListView))
		self.Simple_Mode.triggered.connect(self.setSimple)
		self.View_Menu.addAction(self.Simple_Mode)
		self.Show_Bytes = QAction(self._("&Show bytes"), self)
		self.Show_Bytes.setCheckable(True)
		self.Show_Bytes.setChecked(True)
		self.Show_Bytes.triggered.connect(self.setShowBytes)
		self.View_Menu.addAction(self.Show_Bytes)
		Layout_Menu = QT.QMenu(self._("&Layout"), self.View_Menu)
		Toolbar = QAction(self._("&Toolbar"), Layout_Menu)
		Toolbar.setCheckable(True)
		Toolbar.setChecked(True)
		Toolbar.triggered.connect(self.showToolbar)
		Layout_Menu.addAction(Toolbar)
		Status_Bar = QAction(self._("&Status bar"), Layout_Menu)
		Status_Bar.setCheckable(True)
		Status_Bar.setChecked(True)
		Status_Bar.triggered.connect(self.showStatusBar)
		Layout_Menu.addAction(Status_Bar)
		self.View_Menu.addMenu(Layout_Menu)
		Lang_Menu = QT.QMenu(self._("&Language"), self.Menu)
		Lang_Group = QActionGroup(Lang_Menu)
		Lang_Group.setExclusive(True)
		Current_Lang = loadLanguage()
		if not Current_Lang:
			Current_Lang = "en"
		try:
			Languages = loadLanguages()
		except Exception:
			Languages = ["en"]
		if Languages is None:
			Languages = ["en"]
		for Lang in Languages:
			Action = QAction(self._(f"&{Lang}"), Lang_Menu)
			Action.setCheckable(True)
			if Lang == Current_Lang:
				Action.setChecked(True)
			Action.triggered.connect(lambda checked, l=Lang: self.setLanguage(l))
			Lang_Menu.addAction(Action)
			Lang_Group.addAction(Action)
		self.View_Menu.addMenu(Lang_Menu)
	def buildHelpMenu(self):
		self.Help_Menu = self.Menu.addMenu(self._("&Help"))
		About = QAction(self._("&About"), self.Help_Menu)
		About.setIcon(self.style().standardIcon(QT.QStyle.SP_MessageBoxInformation))
		About.triggered.connect(self.about)
		self.Help_Menu.addAction(About)
		Readme = QAction(self._("&Readme"), self.Help_Menu)
		Readme.setShortcut("F1")
		Readme.setIcon(self.style().standardIcon(QT.QStyle.SP_FileIcon))
		Readme.triggered.connect(self.readme)
		self.Help_Menu.addAction(Readme)
		Changelog = QAction(self._("&Changelog"), self.Help_Menu)
		Changelog.setIcon(self.style().standardIcon(QT.QStyle.SP_FileDialogDetailedView))
		Changelog.triggered.connect(self.changelog)
		self.Help_Menu.addAction(Changelog)
		Homepage = QAction(self._("&Homepage"), self.Help_Menu)
		Homepage.setIcon(self.style().standardIcon(QT.QStyle.SP_DirLinkIcon))
		Homepage.triggered.connect(self.homepage)
		self.Help_Menu.addAction(Homepage)
		License = QAction(self._("&License"), self.Help_Menu)
		License.setIcon(self.style().standardIcon(QT.QStyle.SP_FileDialogInfoView))
		License.triggered.connect(self.license)
		self.Help_Menu.addAction(License)
	def showToolbar(self, Enabled):
		self.Toolbar.setVisible(Enabled)
	def showStatusBar(self, Enabled):
		self.Status.setVisible(Enabled)
	def buildToolbar(self):
		self.Toolbar = self.addToolBar("Main")
		self.Toolbar.setFocusPolicy(Qt.StrongFocus)
		self.Toolbar.setMovable(False)
		self.Toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		self.Toolbar.setVisible(True)
		self.Toolbar.addAction(self.Refresh)
		self.Toolbar.addAction(self.Export)
		self.Toolbar.addAction(self.Exit)
		self.Toolbar.addSeparator()
		self.Toolbar.addAction(self.Auto_Refresh)
		self.Toolbar.addAction(self.Simple_Mode)
		self.Toolbar.addAction(self.Show_Bytes)
		for Action in self.Toolbar.actions():
			Button = self.Toolbar.widgetForAction(Action)
			if Button:
				Button.setFocusPolicy(Qt.StrongFocus)
				Button.installEventFilter(self)
	def buildStatusBar(self):
		self.Status = self.statusBar()
		self.Status.setVisible(True)
		self.Drive_Label = QT.QLabel(self._("Drives: {drives}", drives=0))
		self.Total_Label = QT.QLabel(self._("Total: {total}", total=0))
		self.Used_Label = QT.QLabel(self._("Used: {used}", used=0))
		self.Free_Label = QT.QLabel(self._("Free: {free}", free=0))
		self.Filter_Label = QT.QLabel(self._("Filter: {filter}", filter=self._("All")))
		self.Auto_Label = QT.QLabel(self._("Auto refresh: {state}", state=self._("Off")))
		self.Timeout_Label = QT.QLabel(self._("Timeout: {timeout}", timeout=self._("Disabled")))
		self.Refresh_Label = QT.QLabel(self._("Last refresh: {last_refresh}", last_refresh=self._("Never")))
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
		self.Table.setAccessibleName(self._("Drive info"))
		self.Header = self.Table.horizontalHeader()
		self.Header.setSectionResizeMode(QT.QHeaderView.ResizeToContents)
		self.Header.setStretchLastSection(True)
		self.Header.setDefaultAlignment(Qt.AlignCenter)
		self.Header.setHighlightSections(False)
		self.Header.sectionClicked.connect(self.onHeaderClicked)
		self.Header.setSortIndicatorShown(True)
		self.Drive_Icon_Label = QT.QLabel()
		self.Drive_Icon_Label.setPixmap(self.style().standardIcon(QT.QStyle.SP_DriveHDIcon).pixmap(24, 24))
		Container = QT.QWidget()
		Layout = QT.QVBoxLayout(Container)
		Layout.setContentsMargins(0, 0, 0, 0)
		Layout.addWidget(self.Drive_Icon_Label)
		Layout.addWidget(self.Table)
		self.setCentralWidget(Container)
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
			Datas = data.getData(Sort=Sort, Reverse=Reverse, filterType=[Type] if Type else None, Top=Top, Percent=Percent, Exclude=None)
		except error.DataEmptyError as Error:
			if Error.code == error.DataErrorCode.Invalid_Drives:
				QT.QMessageBox.critical(self, "Error", self._("Invalid drives"))
			elif Error.code == error.DataErrorCode.No_Drive:
				QT.QMessageBox.critical(self, "Error",self._( "No drive information"))
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
			try:
				Percent = int(Value or 0)
			except (TypeError, ValueError):
				Percent = 0
			Cell.setForeground(QBrush(QColor(Style["color"])))
			Cell.setData(Percent, Qt.UserRole)
			Cell.setData(Style["color"], Qt.UserRole + 1)
			Cell.setText(f"{Percent:.0f}%")
		elif Key in constants.Color_Columns:
			Cell.setForeground(QBrush(QColor(Style["color"])))
			Size = f"{utils.formatSize(Value)} ({Value} Bytes)" if self.Bytes else f"{utils.formatSize(Value)}"
			Cell.setText(Size)
		elif Key == "total":
			Size = f"{utils.formatSize(Value)} ({Value} Bytes)" if self.Bytes else f"{utils.formatSize(Value)}"
			Cell.setText(Size)
		if Key in constants.Center_Columns:
			Cell.setTextAlignment(Qt.AlignCenter)
		return Cell
	def createProgressBar(self, Item):
		Value = Item.data(Qt.UserRole) or 0
		Color = Item.data(Qt.UserRole + 1) or "#00aa55"
		Bar = AnimatedProgressBar()
		Bar.setRange(0, 100)
		Bar.setAnimatedValue(Value)
		Bar.setFormat(f"{Value}%")
		Bar.setTextVisible(True)
		Bar.setAlignment(Qt.AlignCenter)
		Bar.setFocusPolicy(Qt.StrongFocus)
		Bar.setEnabled(True)
		Bar.setAccessibleName(self._("Usage"))
		Bar.setAccessibleDescription(self._("{value} percent used", value=Value))
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
		self.Drive_Label.setText(self._("Drives: {drives}", drives=len(Datas)))
		Total_Size = sum(Item.get("total", 0) for Item in Datas)
		Total_STR = f"{utils.formatSize(Total_Size)} ({Total_Size} Bytes)" if self.Bytes else utils.formatSize(Total_Size)
		self.Total_Label.setText(self._("Total: {total}", total=Total_STR))
		Used_Size = sum(Item.get("used", 0) for Item in Datas)
		Used_STR = f"{utils.formatSize(Used_Size)} ({Used_Size} Bytes)" if self.Bytes else utils.formatSize(Used_Size)
		self.Used_Label.setText(self._("Used: {used}", used=Used_STR))
		Free_Size = sum(Item.get("free", 0) for Item in Datas)
		Free_STR = f"{utils.formatSize(Free_Size)} ({Free_Size} Bytes)" if self.Bytes else utils.formatSize(Free_Size)
		self.Free_Label.setText(self._("Free: {free}", free=Free_STR))
		self.Columns = []
		Seen = set()
		for Item in Datas:
			for Key in Item.keys():
				if self.Simple:
					if Key not in constants.GUI_Simple_Columns:
						continue
				if Key not in Seen:
					Seen.add(Key)
					self.Columns.append(Key)
		self.Headers = [self._(constants.GUI_Headers.get(Key, Key.replace("_", " ").title())) for Key in self.Columns]
		self.Model.setHorizontalHeaderLabels(self.Headers)
		for RowIndex, Item in enumerate(Datas):
			Row = []
			for Key in self.Columns:
				Value = Item.get(Key, "")
				Row.append(self.makeCell(Key, Value, Item))
			self.Model.appendRow(Row)
			if "percent" in self.Columns:
				try:
					Col = self.Columns.index("percent")
					Item = Row[Col]
					Index = self.Model.index(RowIndex, Col)
					self.Table.setIndexWidget(Index, self.createProgressBar(Item))
				except IndexError:
					pass
		self.Table.resizeColumnsToContents()
	def refreshData(self):
		if self.Percent is not None and not self.Sort:
			self.Sort = "usage"
		if self.Top and not self.Sort:
			self.Sort = "used"
		self.animateRefresh()
		self.loadData(self.Sort, self.Reverse, self.Type, self.Top, self.Percent)
		self.updateLastRefresh()
		self.Table.setFocus()
	def updateLastRefresh(self):
		Time = datetime.now().strftime("%H:%M:%S")
		self.Refresh_Label.setText(self._("Last refresh: {last_refresh}", last_refresh=Time))
	def showContextMenu(self, Pos):
		Menu = QT.QMenu(self)
		Copy_Cell = QAction(self._("Copy &Cell"), self)
		Copy_Row = QAction(self._("Copy &Row"), self)
		Copy_Column = QAction(self._("Copy &Column"), self)
		Copy_Cell.triggered.connect(self.copyCell)
		Copy_Row.triggered.connect(self.copyRow)
		Copy_Column.triggered.connect(self.copyColumn)
		Menu.addAction(Copy_Cell)
		Menu.addAction(Copy_Row)
		Menu.addAction(Copy_Column)
		Menu.addAction(self.createExportAction(Menu))
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
	def setType(self, Mode):
		Text = self._(Mode.title()) if Mode else self._("All")
		self.Type = Mode
		self.refreshData()
		self.Filter_Label.setText(self._("Filter: {filter}", filter=Text))
	def setTop(self):
		Input, OK = QT.QInputDialog.getInt(self, self._("Top"), self._("Top drives:"), 5, 0, 100)
		if OK:
			if Input == 0:
				self.Top = None
			else:
				self.Top = Input
			self.refreshData()
	def setUsage(self):
		Input, OK = QT.QInputDialog.getDouble(self, self._("Usage"), self._("Minimum usage %:"), 90, 0, 100, 2)
		if OK:
			if Input == 0:
				self.Percent = None
			else:
				self.Percent = Input
			self.refreshData()
	def setTimer(self):
		Input, OK = QT.QInputDialog.getDouble(self, self._("Auto refresh"), self._("Seconds:"), 2, 0, 60, 2)
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
		Text = self._("On") if Enabled else self._("Off")
		self.Auto_Refresh.setChecked(Enabled)
		self.Auto_Refresh.setIcon(self.style().standardIcon(Icon))
		self.Auto_Label.setText(self._("Auto refresh: {state}", state=Text))
		if not self.Current_Timeout == 0:
			self.Timeout_Label.setText(self._("Timeout: {timeout}s", timeout=f"{self.Current_Timeout:g}"))
		else:
			self.Timeout_Label.setText(self._("Timeout: {timeout}", timeout=self._("Disabled")))
	def exportFile(self):
		Path, File_Type = QT.QFileDialog.getSaveFileName(self, self._("Export"), "Report.txt", "Text Files (*.txt);;CSV Files (*.csv);;JSON Files (*.json);;Markdown Files (*.md);;INI Files (*.ini);;XML Files (*.xml);;Yaml Files (*.yaml);;Excel Files (*.xlsx);;Web Files (*.html);;Toml Files (*.toml)", "Text Files (*.txt)")
		if not Path:
			return None
		Ext = File_Type.split("*")[-1].replace(")", "")
		if not Path.lower().endswith(Ext):
			Path += Ext
		try:
			export.exportData(Path, Sort=self.Sort, Reverse=self.Reverse, filterType=[self.Type] if self.Type else None, Top=self.Top, Percent=self.Percent, Exclude=None)
			QT.QMessageBox.information(self, self._("Success"), self._("Export completed.\nExported to {path}", path=Path))
		except ValueError:
			QT.QMessageBox.critical(self, self._("Error"), self._("Unsupported format"))
		except error.FileWriteError:
			QT.QMessageBox.critical(self, self._("Error"), self._("Cannot write {path}", path=Path))
		except error.DataEmptyError as Error:
			if Error.code == error.DataErrorCode.Invalid_Drives:
				QT.QMessageBox.critical(self, self._("Error"), self._("Invalid drives"))
			elif Error.code == error.DataErrorCode.No_Drive:
				QT.QMessageBox.critical(self, self._("Error"), self._("No drive information"))
		except error.DataOutOfLimitError as Error:
			if Error.code == error.DataErrorCode.Top_Limit:
				QT.QMessageBox.critical(self, self._("Error"), self._(Error.message))
			elif Error.code == error.DataErrorCode.Usage_Limit:
				QT.QMessageBox.critical(self, self._("Error"), self._(Error.message))
	def homepage(self):
		QDesktopServices.openUrl(QUrl("https://github.com/Hoang-Long2012/DiskInfo"))
	def readme(self):
		try:
			os.startfile(utils.getFilePath("README.MD"))
		except Exception as Error:
			QT.QMessageBox.critical(self, self._("Error"), self._("Cannot open README.md\n{error}", error=self._(str(Error))))
	def changelog(self):
		try:
			os.startfile(utils.getFilePath("CHANGELOG.MD"))
		except Exception as Error:
			QT.QMessageBox.critical(self, self._("Error"), self._("Cannot open CHANGELOG.md\n{error}", error=self._(str(Error))))
	def license(self):
		try:
			os.startfile(utils.getFilePath("LICENSE"))
		except Exception as Error:
			QT.QMessageBox.critical(self, self._("Error"), self._("Cannot open LICENSE\n{error}", error=self._(str(Error))))
	def about(self):
		Box = QT.QMessageBox(self)
		Box.setWindowTitle(self._("About DiskInfo"))
		Box.setIcon(QT.QMessageBox.Information)
		Box.setTextFormat(Qt.RichText)
		Box.setText(
			self._("""
<h2>DiskInfo version {version}</h2>
<p>Simple disk information viewer for Windows.</p>
<p><b>Author:</b> Hoang Long</p>
<p>
<a href="https://github.com/Hoang-Long2012/DiskInfo">
Project Homepage
</a>
</p>
""",
		version=getVersion()))
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
	def setSimple(self, Enabled):
		Icon = QT.QStyle.SP_FileDialogDetailedView if Enabled else QT.QStyle.SP_FileDialogListView
		Text = self._("Detailed") if Enabled else self._("Simple")
		self.Simple = Enabled
		self.refreshData()
		self.Simple_Mode.setText(Text)
		self.Simple_Mode.setIcon(self.style().standardIcon(Icon))
	def setShowBytes(self, Enabled):
		self.Bytes = Enabled
		self.refreshData()
	def setLanguage(self, Lang):
		saveLanguage(Lang)
		QT.QMessageBox.information(self, self._("Success"), self._("Language changed successfully.\nPlease restart app to apply language change."))
class AccessibleModel(QStandardItemModel):
	def data(self, Index, Role):
		if not Index.isValid():
			return super().data(Index, Role)
		if Role == Qt.AccessibleTextRole:
			Header = self.headerData(Index.column(), Qt.Horizontal, Qt.DisplayRole)
			Value = super().data(Index, Qt.DisplayRole)
			if Header is not None and Value is not None:
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
	QAccessible.setActive(True)
	Window = MainWindow()
	Window.show()
	Window.raise_()
	Window.activateWindow()
	Window.Table.setFocus()
	sys.exit(App.exec())
if __name__ == "__main__":
	main()