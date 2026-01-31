# FishingPlanet OCR - Addon NVDA

## Descrizione

Addon NVDA per il gioco FishingPlanet che integra un sistema OCR (riconoscimento ottico caratteri) intelligente con zone predefinite dello schermo. Permette ai giocatori non vedenti di ricevere informazioni visive automaticamente tramite sintesi vocale.

## Requisiti

- NVDA 2021.1 o superiore
- Windows 10/11 con OCR lingua italiana installata
- FishingPlanet installato

## Comandi Principali

### Controllo OCR

- **NVDA+ALT+L**: Attiva o disattiva la scansione OCR automatica
  - Beep alto (444 Hz): OCR avviato
  - Beep basso (222 Hz): OCR fermato

### Zone Predefinite

- **NVDA+ALT+1**: Scansione schermo completo (tutto lo schermo)
- **NVDA+ALT+2**: Scansione metà inferiore (ideale durante la pesca)
- **NVDA+ALT+3**: Scansione metà destra (ideale nel negozio)
- **NVDA+ALT+4**: Scansione centro schermo (menu e dialoghi)

### Altri Comandi

- **NVDA+ALT+C**: Centra il mouse (raddrizza visuale)
- **NVDA+H**: Sistema di aiuto FishingPlanet

## Installazione

1. Scaricare il file `.nvda-addon` dalla sezione Releases
2. Aprire il file (NVDA lo riconoscerà automaticamente)
3. Confermare l'installazione quando richiesto
4. Riavviare NVDA se necessario

## Utilizzo Tipico

### Durante la Pesca

1. Avviare FishingPlanet e raggiungere la schermata di pesca
2. Premere **NVDA+ALT+2** per impostare la zona "metà inferiore"
3. Premere **NVDA+ALT+L** per avviare la scansione OCR
4. NVDA leggerà automaticamente i messaggi che appaiono nella parte bassa dello schermo
5. Premere **NVDA+ALT+L** per fermare quando non più necessario

### Nel Negozio

1. Aprire il negozio nel gioco
2. Premere **NVDA+ALT+3** per impostare la zona "metà destra"
3. Premere **NVDA+ALT+L** per avviare la scansione
4. Navigare tra i prodotti: NVDA leggerà le descrizioni che appaiono a destra

### Menu e Dialoghi

1. Premere **NVDA+ALT+4** per la zona "centro schermo"
2. Avviare OCR con **NVDA+ALT+L**
3. I messaggi centrali verranno letti automaticamente

## Configurazione Avanzata

Le impostazioni OCR sono memorizzate nella configurazione NVDA e includono:

- **Intervallo scansione**: Tempo tra una scansione e l'altra (default: varia per zona)
- **Threshold similarità**: Sensibilità al rilevamento cambiamenti testo (default: 0.5)
- **Crop percentuali**: Definizione precise delle zone (modificabile manualmente)

Per accedere: le impostazioni sono nella sezione `[fishingplanet_ocr]` del file di configurazione NVDA.

## Risoluzione Problemi

### L'OCR non legge nulla

- Verificare che Windows OCR sia installato (Impostazioni > Ora e lingua > Lingua > Italiano > Opzioni > OCR)
- Controllare che FishingPlanet sia in modalità finestra o borderless (non fullscreen esclusivo)
- Provare ad aumentare l'intervallo di scansione se il testo cambia molto rapidamente

### NVDA legge troppo spesso lo stesso testo

- Il threshold di similarità può essere troppo basso
- Modificare il valore `threshold` nella configurazione (valori più alti = meno ripetizioni)

### Rallentamenti o lag

- L'OCR consuma risorse: provare ad aumentare l'intervallo di scansione
- Utilizzare zone più piccole invece dello schermo completo
- Fermare l'OCR quando non necessario

## Note sulla Performance

- **Uso memoria**: ~50-100 MB aggiuntivi durante OCR attivo
- **Uso CPU**: 5-10% medio (dipende dalla dimensione zona e intervallo)
- **Latenza**: ~200-500ms per scansione (dipende da risoluzione zona)

## Crediti

Basato sul sistema OCR di LION addon (vortex1024)

Autore: Luca Profita (Nemex81)  
Email: nemex1981@gmail.com  
Versione: 0.2.0

## Licenza

GPL v2 (compatibile con NVDA)
