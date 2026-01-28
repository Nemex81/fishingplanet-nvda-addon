"""
	FishingPlanet addon for NVDA
	sistema di comandi accessibili per FishingPlanet
	autore: Luca Profita
	NikName: Nemex81
	e-mail: nemex1981@gmail.com
"""

import  time
import winUser
import wx
import api
import review
import ui
import textInfos
import braille
import speech
import mouseHandler
import appModuleHandler
from scriptHandler import script
from globalCommands import commands, SCRCAT_TEXTREVIEW


class AppModule(appModuleHandler.AppModule):

	#TRANSLATORS: category for VLC input gestures
	scriptCategory = _("FishingPlanet")


	#@@# metodi di classe

	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)


	#@@# sezione comandi script

	@script(
		description=_("help system per Fishing Planet"),
		gesture="kb:nvda+h"
	)
	def script_fishingplanet_Help_system(self, gesture):
		string = "benvenuto in FishingPlanet help system."
		ui.message(string)


	@script(
		description=_("Centra il mouse (raddrizza la visuale)."),
		gesture="kb:nvda+alt+c"
	)
	def script_FP_centerMouse(self, gesture):
		# Centro del monitor principale (display 0)
		x, y, w, h = wx.Display(0).GetGeometry()
		centerX = x + (w // 2)
		centerY = y + (h // 2)

		winUser.setCursorPos(centerX, centerY)
		ui.message(_("centrato"))

