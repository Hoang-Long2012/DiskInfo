import ctypes
def getLogicalDriveStrings():
	Length = ctypes.windll.kernel32.GetLogicalDriveStringsW(0, None)
	Buffer = ctypes.create_unicode_buffer(Length)
	Result = ctypes.windll.kernel32.GetLogicalDriveStringsW(Length, Buffer)
	if not Result:
		return None
	return Buffer[:].rstrip('\0').split('\0')
def get_logical_drives():
	Mask = ctypes.windll.kernel32.GetLogicalDrives()
	if not Mask:
		return None
	Drives = []
	for I in range(26):
		if Mask & (1 << I):
			Drives.append(f"{chr(65 + I)}:\\")
	return Drives
def getDrivesList():
	Drives = getLogicalDriveStrings()
	if Drives:
		return Drives
	Drives = get_logical_drives()
	if Drives:
		return Drives
	return None
def getDriveUsage(Drive):
	Free = ctypes.c_ulonglong()
	Total = ctypes.c_ulonglong()
	Total_Free = ctypes.c_ulonglong()
	Result = ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(Drive), ctypes.byref(Free), ctypes.byref(Total), ctypes.byref(Total_Free))
	if not Result:
		return None
	Used = Total.value - Free.value
	Percent = (Used / Total.value) * 100 if Total.value else 0
	return {
		"total": Total.value,
		"used": Used,
		"free": Free.value,
		"percent": Percent
	}
def getVolumeInfo(Drive):
	if not Drive.endswith("\\"):
		Drive += "\\"
	Volume_name_buffer = ctypes.create_unicode_buffer(261)
	Fs_name_buffer = ctypes.create_unicode_buffer(261)
	Result = ctypes.windll.kernel32.GetVolumeInformationW(ctypes.c_wchar_p(Drive), Volume_name_buffer, len(Volume_name_buffer), None, None, None, Fs_name_buffer, len(Fs_name_buffer))
	if Result:
		return [
			Volume_name_buffer.value,
			Fs_name_buffer.value
		]
	else:
		return None
def getDriveType(Drive):
	return ctypes.windll.kernel32.GetDriveTypeW(ctypes.c_wchar_p(Drive))