"""
	FishingPlanet addon for NVDA
	sistema di comandi accessibili per FishingPlanet
	autore: Luca Profita
	NikName: Nemex81
	e-mail: nemex1981@gmail.com
"""

import time
import threading
import ctypes
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
import config
import addonHandler
import contentRecog
import contentRecog.uwpOcr
import screenBitmap
import locationHelper
import tones
from scriptHandler import script
from globalCommands import commands, SCRCAT_TEXTREVIEW
from difflib import SequenceMatcher

# Inizializzazione traduzioni
addonHandler.initTranslation()

# Configurazione OCR
confspec = {
    "cropUp": "integer(0,100,default=0)",
    "cropLeft": "integer(0,100,default=0)",
    "cropRight": "integer(0,100,default=0)",
    "cropDown": "integer(0,100,default=0)",
    "interval": "float(0.0,10.0,default=1.0)",
    "threshold": "float(0.0,1.0,default=0.5)"
}
config.conf.spec["fishingplanet_ocr"] = confspec

# Profili Zone Predefiniti
ZONE_PROFILES = {
    "full": {
        "cropUp": 0,
        "cropDown": 0,
        "cropLeft": 0,
        "cropRight": 0,
        "interval": 1.5,
        "name": "schermo completo",
        "description": "Scansione dell'intero schermo"
    },
    "bottom": {
        "cropUp": 50,
        "cropDown": 0,
        "cropLeft": 0,
        "cropRight": 0,
        "interval": 0.5,
        "name": "metà inferiore",
        "description": "Zona pesca - metà inferiore dello schermo"
    },
    "right": {
        "cropUp": 0,
        "cropDown": 0,
        "cropLeft": 50,
        "cropRight": 0,
        "interval": 1.0,
        "name": "metà destra",
        "description": "Zona negozio - metà destra dello schermo"
    },
    "center": {
        "cropUp": 25,
        "cropDown": 25,
        "cropLeft": 25,
        "cropRight": 25,
        "interval": 1.0,
        "name": "centro schermo",
        "description": "Area centrale dello schermo"
    }
}


class AppModule(appModuleHandler.AppModule):

	#TRANSLATORS: category for VLC input gestures
	scriptCategory = _("FishingPlanet")


	#@@# metodi di classe

	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)
		
		# OCR state
		self.ocrActive = False
		self.currentZone = "full"
		self.prevString = ""
		self.ocrCounter = 0
		self.ocrThread = None
		self.recog = None
		
		# Risoluzione schermo
		user32 = ctypes.windll.user32
		self.resX = user32.GetSystemMetrics(0)
		self.resY = user32.GetSystemMetrics(1)

	def setZone(self, zoneName):
		"""
		Imposta il profilo zona attivo e aggiorna la configurazione.
		
		Args:
			zoneName (str): Nome del profilo da ZONE_PROFILES
		"""
		if zoneName not in ZONE_PROFILES:
			ui.message(_("Zona non valida"))
			return
		
		self.currentZone = zoneName
		profile = ZONE_PROFILES[zoneName]
		
		# Aggiorna configurazione
		cfg = config.conf["fishingplanet_ocr"]
		cfg["cropUp"] = profile["cropUp"]
		cfg["cropDown"] = profile["cropDown"]
		cfg["cropLeft"] = profile["cropLeft"]
		cfg["cropRight"] = profile["cropRight"]
		cfg["interval"] = profile["interval"]
		
		# Notifica utente
		ui.message(_("Zona: {}").format(profile["name"]))

	def cropRectLTWH(self, baseRect):
		"""
		Applica i valori di crop al rettangolo base.
		
		Args:
			baseRect: Rettangolo base locationHelper.RectLTWH
		
		Returns:
			locationHelper.RectLTWH: Rettangolo con crop applicato
		"""
		cfg = config.conf["fishingplanet_ocr"]
		
		if baseRect is None:
			return locationHelper.RectLTWH(0, 0, 0, 0)
		
		newLeft = int((baseRect.left + baseRect.width) * cfg['cropLeft'] / 100.0)
		newTop = int((baseRect.top + baseRect.height) * cfg['cropUp'] / 100.0)
		newWidth = int(baseRect.width - (baseRect.width * cfg['cropRight'] / 100.0))
		newHeight = int(baseRect.height - (baseRect.height * cfg['cropDown'] / 100.0))
		
		return locationHelper.RectLTWH(newLeft, newTop, newWidth, newHeight)

	def ocrLoop(self):
		"""
		Loop principale di scansione OCR.
		Esegue scansioni continue finché self.ocrActive è True.
		"""
		cfg = config.conf["fishingplanet_ocr"]
		
		while self.ocrActive:
			try:
				self.performOCR()
				time.sleep(cfg["interval"])
			except Exception as e:
				import logHandler
				logHandler.log.error(f"FishingPlanet OCR loop error: {e}", exc_info=True)
				time.sleep(1.0)  # Attesa maggiore in caso di errore

	def performOCR(self):
		"""
		Esegue una singola scansione OCR sulla zona attiva.
		"""
		try:
			# Calcola area da scansionare
			baseRect = locationHelper.RectLTWH(0, 0, self.resX, self.resY)
			scanRect = self.cropRectLTWH(baseRect)
			
			left, top, width, height = scanRect
			
			# Inizializza recognizer
			self.recog = contentRecog.uwpOcr.UwpOcr()
			
			# Crea immagine info
			imgInfo = contentRecog.RecogImageInfo.createFromRecognizer(
				left, top, width, height, self.recog
			)
			
			# Cattura schermo
			sb = screenBitmap.ScreenBitmap(imgInfo.recogWidth, imgInfo.recogHeight)
			pixels = sb.captureImage(left, top, width, height)
			
			# Esegui OCR
			self.recog.recognize(pixels, imgInfo, self.recog_onResult)
			
			# Cleanup periodico
			self.ocrCounter += 1
			if self.ocrCounter > 9:
				del self.recog
				self.recog = None
				self.ocrCounter = 0
				
		except Exception as e:
			import logHandler
			logHandler.log.error(f"FishingPlanet performOCR error: {e}", exc_info=True)

	def recog_onResult(self, result):
		"""
		Callback risultato OCR. Filtra duplicati usando threshold.
		
		Args:
			result: Oggetto risultato OCR
		"""
		try:
			# Crea oggetto dummy per estrarre testo
			o = type('NVDAObject', (), {})()
			info = result.makeTextInfo(o, textInfos.POSITION_ALL)
			
			# Calcola similarità con testo precedente
			threshold = SequenceMatcher(None, self.prevString, info.text).ratio()
			
			cfg = config.conf["fishingplanet_ocr"]
			
			# Annuncia solo se sufficientemente diverso e non vuoto
			if (threshold < cfg['threshold'] and 
				info.text != "" and 
				info.text.strip() != ""):
				ui.message(info.text)
				self.prevString = info.text
				
		except Exception as e:
			import logHandler
			logHandler.log.error(f"FishingPlanet recog_onResult error: {e}", exc_info=True)


	#@@# sezione comandi script

	@script(
		description=_("Attiva o disattiva la scansione OCR automatica"),
		gesture="kb:nvda+alt+l"
	)
	def script_toggleOCR(self, gesture):
		"""
		Avvia/ferma il loop OCR con feedback audio distintivo.
		"""
		if not self.ocrActive:
			self.ocrActive = True
			tones.beep(444, 333)  # Beep alto = avvio
			zoneName = ZONE_PROFILES[self.currentZone]["name"]
			ui.message(_("OCR avviato - zona: {}").format(zoneName))
			
			# Avvia thread OCR
			self.ocrThread = threading.Thread(target=self.ocrLoop)
			self.ocrThread.daemon = True
			self.ocrThread.start()
		else:
			self.ocrActive = False
			tones.beep(222, 333)  # Beep basso = stop
			ui.message(_("OCR fermato"))
			
			# Attendi terminazione thread (max 2 secondi)
			if self.ocrThread:
				self.ocrThread.join(timeout=2.0)

	@script(
		description=_("Imposta scansione OCR su schermo completo"),
		gesture="kb:nvda+alt+1"
	)
	def script_zoneFull(self, gesture):
		self.setZone("full")

	@script(
		description=_("Imposta scansione OCR su metà inferiore dello schermo (pesca)"),
		gesture="kb:nvda+alt+2"
	)
	def script_zoneBottom(self, gesture):
		self.setZone("bottom")

	@script(
		description=_("Imposta scansione OCR su metà destra dello schermo (negozio)"),
		gesture="kb:nvda+alt+3"
	)
	def script_zoneRight(self, gesture):
		self.setZone("right")

	@script(
		description=_("Imposta scansione OCR su centro schermo"),
		gesture="kb:nvda+alt+4"
	)
	def script_zoneCenter(self, gesture):
		self.setZone("center")

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

	def terminate(self):
		"""
		Cleanup quando addon viene disabilitato o NVDA chiuso.
		"""
		# Ferma OCR se attivo
		if self.ocrActive:
			self.ocrActive = False
			if self.ocrThread:
				self.ocrThread.join(timeout=2.0)
		
		# Cleanup recognizer
		if self.recog:
			try:
				del self.recog
			except:
				pass
		
		super(AppModule, self).terminate()

