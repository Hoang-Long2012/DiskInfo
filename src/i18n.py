from constants import Domain
import gettext
import os
import utils
def loadLanguages():
	Locale_Path = utils.getFilePath("locale")
	Languages = []
	for Lang in os.listdir(Locale_Path):
		Mo_Path = os.path.join(Locale_Path, Lang, "LC_MESSAGES", f"{Domain}.mo")
		if os.path.isfile(Mo_Path):
			Languages.append(Lang)
	return Languages
def loadLanguage():
	if not os.path.isfile(utils.getFilePath("lang.txt")):
		with open(utils.getFilePath("lang.txt"), "w", encoding="utf-8") as File:
			File.write("en")
	with open(utils.getFilePath("lang.txt"), "r", encoding="utf-8") as File:
		return File.read()
def saveLanguage(Lang):
	with open(utils.getFilePath("lang.txt"), "w", encoding="utf-8") as File:
		File.write(Lang)
class InitTranslation:
	def __init__(self, Lang):
		self.Translation = gettext.translation(Domain, localedir=utils.getFilePath("locale"), languages=[Lang] if not isinstance(Lang, list) else Lang, fallback=True)
	def translate(self, Text, *args, **kwargs):
		MSG = self.Translation.gettext(Text)
		try:
			return MSG.format(*args, **kwargs) if args or kwargs else MSG
		except Exception:
			return MSG