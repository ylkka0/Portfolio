"""Live English/Finnish text; changing language never touches fishing state."""
import tkinter as tk
from tkinter import ttk
import weakref

EN = {
 'Tauolla. F8 jatkaa.':'Paused. F8 resumes.',
 'Näppäin ei mennyt peliin. Tarkista pelin ja botin oikeustaso.':'Key input failed. Check that the game and bot use compatible privilege levels.',
 'Taustapainalluksen kohde puuttuu.':'No target window for background input.',
 'Taustaviestin lähetys epäonnistui. Tarkista pelin ja botin oikeustaso.':'Background input failed. Check the game and bot privilege levels.',
 'Äänilähde vaihtui. Siirry WoWiin ja käynnistä F8:lla.':'Audio source changed. Switch to WoW and start with F8.',
 'Vaihdetaan äänilaitetta...':'Switching audio device...',
 'Suodatus vaihtui. Heitä ensin itse ja jatka F8:lla.':'Filter changed. Cast manually, then resume with F8.',
 'Tila vaihtui. Heitä ensin itse ja käynnistä WoWissa F8:lla.':'Mode changed. Cast manually and start with F8 in WoW.',
 'Babysit-tauko {v0}/{v1}. Jatketaan automaattisesti uudella heitolla.':'Babysit break {v0}/{v1}. Fishing will resume automatically with a new cast.',
 'tausta, kokeellinen':'background, experimental',
 'normaali':'normal',
 'Käynnissä ({v0}). Odotetaan molskahdusta...':'Running ({v0}). Waiting for a splash...',
 'Babysit pois päältä':'Babysit disabled',
 'Osumataso: ei vielä osumaa | Äänenvoimakkuusraja -36 dBFS':'Splash level: no detection yet | Minimum level -36 dBFS',
 'Varoheitto: 32-35 s ilman tunnistettua nostoa':'Recovery cast: 32–35 s without a detected bite',
 'Avataan äänilaitetta...':'Opening audio source...',
 'Äänilaite: avataan Windowsin oletusulostuloa':'Audio: opening the Windows default output',
 'Osumatarkkuus 0.00 | Äänitaso 0.0000':'Detection 0.00 | Audio level 0.0000',
 'Odotetaan äänivirtaa...':'Waiting for audio...',
 'F8 = käynnistä / tauko     F9 = lopeta':'F8 = start / pause     F9 = quit',
 'Äänikuuntelu ei ole valmis. Katso virhe tai odota hetki.':'Audio capture is not ready. Check the error or wait a moment.',
 'WoW-kohde ei ole käytettävissä. Heitä uudelleen ja jatka F8:lla.':'WoW target is unavailable. Cast again and resume with F8.',
 'Babysit poistettiin tauolla. Heitä itse ja jatka F8:lla.':'Babysit disabled during a break. Cast manually and resume with F8.',
 'Babysit-tauko {v0}/{v1}: jäljellä ':'Babysit break {v0}/{v1}: remaining ',
 'Babysit-tauko {v0}/{v1} noin ':'Babysit break {v0}/{v1} in about ',
 'Vaihda WoW-ikkunaan ja paina siellä F8. Tunnistettu: ':'Switch to WoW and press F8 there. Detected: ',
 'Ei tunnistettua nostoa 32-35 s: uusi heitto. Varoheitot {v0}.':'No bite detected for 32–35 s: recasting. Recovery casts: {v0}.',
 'Ikkuna vaihtui tai WoW sulkeutui. Heitä uudelleen ja jatka F8:lla.':'Window changed or WoW closed. Cast again and resume with F8.',
 'Varoheitto tauolla Babysit-tauon ajan':'Recovery timer paused during the Babysit break',
 'Taustatila (kokeellinen): painallukset vain WoW-ikkunaan':'Background mode (experimental): send keys only to WoW',
 'Babysit: 1–2 taukoa 52–109 min aikaikkunassa (1:02–4:18)':'Babysit: 1–2 breaks in a 52–109 min window (1:02–4:18 each)',
 'Kuuntele vain WoWia (striimien äänet eivät kuulu bottiin)':'Listen only to WoW (ignore stream audio)',
 'Muita pelaajia vieressä? Hylkää hiljaiset molskahdukset':'Other players nearby? Reject quiet splashes',
 'Kalaparvisuodatus: tarkista äänen rakenne ennen nostoa':'School filter: check the sound pattern before reeling in',
 'Kalaparvisuodatus lisää noin 0,5 s tunnistusviivettä.':'The school filter adds about 0.5 s of detection latency.',
 'Voimistumiskerroin: pienempi = herkempi (oletus 2,0)':'Trigger ratio: lower = more sensitive (default 2.0)',
 'Vain WoW -tilassa äänilaitevalikkoa ei käytetä. F8 valitsee WoWin.\nHeitä ensin itse, siirry WoWiin ja paina F8.\nTaustatilassa voit tämän jälkeen vaihtaa toiseen ohjelmaan.\nNormaalitilassa ikkunan vaihto tauottaa. F8 tauottaa molemmissa tiloissa.':
 'WoW-only mode ignores the device menu. F8 selects the WoW process.\nCast manually, switch to WoW and press F8.\nIn background mode you may then switch to another application.\nNormal mode pauses on focus loss. F8 pauses either mode.',
 'Lopeta (F9)':'Quit (F9)',
 'Ei toistoäänilaitteita. Tarkista kuulokkeet/kaiuttimet.':'No playback devices found. Check your headphones/speakers.',
 'Babysit-tauko alkaa tämän heiton päätyttyä.':'The Babysit break will start after the current cast finishes.',
 'Babysit valittu. Ajastus alkaa F8-käynnistyksestä.':'Babysit enabled. Its schedule starts when you press F8.',
 'Babysit-tauko päättyi. Uusi heittopainallus lähetetty.':'Babysit break finished. A new cast key was sent.',
 'Varoheitto {v0:.1f} s kuluttua ilman tunnistettua nostoa | Tehty {v1}':'Recovery in {v0:.1f} s without a detected bite | Completed: {v1}',
 'Vain WoW (PID {v0}) - muut sovellukset ohitetaan':'WoW only (PID {v0}) — other applications excluded',
 'Heittopainallus lähetetty. Syklejä: {v0}. Odotetaan...':'Cast key sent. Cycles: {v0}. Waiting...',
 'Nostetaan / heitetään uudelleen...':'Reeling in / recasting...',
 'Varoheitto tauolla (32-35 s käynnistyksen/heiton jälkeen)':'Recovery timer paused (32–35 s after start/cast)',
 'Äänenvoimakkuusraja {v0:.1f} dBFS (oikealle = tiukempi)':'Minimum level {v0:.1f} dBFS (right = stricter)',
 'KAIKKI äänet: ':'ALL audio: ',
 'Äänilaite: ':'Audio source: ',
 'Valmis. Heitä ensin itse ja paina WoWissa F8.':'Ready. Cast manually, then press F8 in WoW.',
 'Piikki {v0:.2f}x | Hyväksytty {v1:.2f}x | Raja {v2:.2f}x | Ääni {v3:.5f}':'Peak {v0:.2f}x | Accepted {v1:.2f}x | Threshold {v2:.2f}x | Audio {v3:.5f}',
 'Vain WoW: siirry peliin ja paina F8':'WoW only: switch to the game and press F8',
 'Äänivirhe: ':'Audio error: ',
 'hyväksytty':'accepted',
 'liian hiljainen':'too quiet',
 'Viimeisin osuma {v0:.1f} dBFS: {v1} | Raja {v2:.1f} dBFS':'Last splash {v0:.1f} dBFS: {v1} | Threshold {v2:.1f} dBFS',
 'Äänivirta on hiljainen. Jos peli soi, valitse toinen äänilaite yllä.':'Audio is quiet. If the game is audible, check the source/device selection.',
 'Äänipiikki ({v0:.2f}x). Nostetaan...':'Audio peak ({v0:.2f}x). Reeling in...',
 'Suodatus odottaa sopivan rakenteista molskahdusta. Pelkkä voimakas piikki ei riitä nostoon.':'The filter is waiting for a matching splash pattern. Loudness alone is not enough.',
 'Ääntä tulee. Jos molskahdus jää rajan alle, laske kerrointa hieman.':'Audio is present. Lower the trigger ratio slightly if splashes stay below it.',
 'Äänipiikki ylitti rajan. Käynnistä F8:lla. Taustatilan pelituki täytyy kokeilla.':'Audio exceeded the threshold. Start with F8. Background support depends on the game.',
 'Virhe: ':'Error: ',
 ' kuluttua':' from now',
 'Sulje botti. Tallennetaan valitun laitteen KAIKKI toistoäänet 45 sekunnilta.':'Close the bot. This records ALL playback audio from the selected device for 45 seconds.',
 'Hiljennä muut sovellukset. Kalasta itse kalaparvessa tallennuksen aikana.':'Silence other applications. Fish manually in a school while recording.',
 'Tarvitaan pienet molskahdukset ja oikea nostomolskahdus samaan tallenteeseen.':'Include the small splashes and the real bite splash in the same recording.',
 'Paina Enter aloittaaksesi. Siirry sitten WoWiin ja heitä itse: ':'Press Enter to start, then switch to WoW and cast manually: ',
 'TALLENNUS KÄYNNISSA (45 s). Ohjelma ei paina mitään näppäinta.':'RECORDING (45 s). No keys will be pressed.',
 'Kerro, missä kohdassa kuului oikea nostomolskahdus, jos tiedat.':'If possible, note when the real bite splash occurred.',
 'Toistoäänilaitteita ei löytynyt.':'No playback devices found.',
 'Virheellinen laitenumero.':'Invalid device number.',
 'Valmis! Lähetä tämä WAV-tiedosto keskusteluun:\n':'Done! Attach this WAV file to the conversation:\n',
 'Tallennus epäonnistui:':'Recording failed:',
 'Valitse laitteen numero, tai Enter = oletus: ':'Choose a device number, or press Enter for the default: ',
 ' (oletus)':' (default)',
 'WoW-äänikuuntelu pysähtyi. Katso process_audio.log.':'WoW audio capture stopped. See process_audio.log.',
 'WoW-äänikuuntelun äänimuoto on virheellinen.':'Unexpected audio format from WoW capture.',
 'Aan nayte on liian lyhyt tai ääneton.':'The audio sample is too short or silent.',
 'Äänikanavien maara vaihtui.':'The audio channel count changed.',
}
FI_OVERRIDES={
 'Aan nayte on liian lyhyt tai ääneton.':'Ääninäyte on liian lyhyt tai äänetön.',
 'Äänikanavien maara vaihtui.':'Äänikanavien määrä vaihtui.',
 'TALLENNUS KÄYNNISSA (45 s). Ohjelma ei paina mitään näppäinta.':'TALLENNUS KÄYNNISSÄ (45 s). Ohjelma ei paina mitään näppäintä.',
 'Kerro, missä kohdassa kuului oikea nostomolskahdus, jos tiedat.':'Kerro, missä kohdassa kuului oikea nostomolskahdus, jos tiedät.',
}
_language='FIN'
_bindings=weakref.WeakValueDictionary()


class Text:
    def __init__(self,key,**values):self.key=key;self.values=values
    def __str__(self):
        template=EN.get(self.key,self.key) if _language=='ENG' else FI_OVERRIDES.get(self.key,self.key)
        return template.format(**self.values)
    def __format__(self,spec):return format(str(self),spec)
    def __add__(self,other):return CompositeText(self,other)
    def __radd__(self,other):return CompositeText(other,self)
    def __contains__(self,value):return value in str(self)


class CompositeText(Text):
    def __init__(self,*parts):self.parts=parts
    def __str__(self):return ''.join(str(part) for part in self.parts)


def tr(key,**values):return Text(key,**values)


def set_language(language):
    global _language
    if language not in ('ENG','FIN'):language='FIN'
    _language=language
    for binding in list(_bindings.values()):
        try:binding.refresh_language()
        except tk.TclError:pass


def get_language():return _language


class StringVar(tk.StringVar):
    def __init__(self,*args,value='',**kwargs):
        self.message=value
        super().__init__(*args,value=str(value),**kwargs)
        _bindings[id(self)]=self
    def set(self,value):
        self.message=value
        super().set(str(value))
    def refresh_language(self):super().set(str(self.message))


class _Widget:
    def __init__(self,*args,**kwargs):
        self.message=kwargs.get('text')
        if self.message is not None:kwargs['text']=str(self.message)
        super().__init__(*args,**kwargs)
        _bindings[id(self)]=self
    def refresh_language(self):
        if self.message is not None:self.configure(text=str(self.message))


class Label(_Widget,ttk.Label):pass
class Checkbutton(_Widget,ttk.Checkbutton):pass
class Button(_Widget,ttk.Button):pass
