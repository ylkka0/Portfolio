"""Windows 11 / Python 3.12. F8 toggles, F9 exits. Start paused."""
import ctypes
from ctypes import wintypes
import json
import logging
from pathlib import Path
import queue
import random
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import pyaudiowpatch as pa
from detector import BurstDetector, StereoSchoolDetector, RATE
from process_audio import ProcessLoopback
from ui_text import tr, set_language, get_language, StringVar as I18nVar
from ui_text import Label as I18nLabel, Checkbutton as I18nCheckbutton, Button as I18nButton

BASE = Path(__file__).resolve().parent
logging.basicConfig(filename=BASE / 'bot.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',encoding='utf-8')
USER = ctypes.WinDLL('user32', use_last_error=True)
KERNEL = ctypes.WinDLL('kernel32', use_last_error=True)
USER.GetForegroundWindow.restype = wintypes.HWND
USER.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
USER.GetAsyncKeyState.argtypes = [ctypes.c_int]
USER.GetAsyncKeyState.restype = ctypes.c_short
KERNEL.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
KERNEL.OpenProcess.restype = wintypes.HANDLE
KERNEL.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                          wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
KERNEL.CloseHandle.argtypes = [wintypes.HANDLE]
ULONG_PTR = ctypes.c_size_t


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [('wVk', wintypes.WORD), ('wScan', wintypes.WORD),
                ('dwFlags', wintypes.DWORD), ('time', wintypes.DWORD),
                ('dwExtraInfo', ULONG_PTR)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [('dx', wintypes.LONG), ('dy', wintypes.LONG),
                ('mouseData', wintypes.DWORD), ('dwFlags', wintypes.DWORD),
                ('time', wintypes.DWORD), ('dwExtraInfo', ULONG_PTR)]


class INPUTUNION(ctypes.Union):
    _fields_ = [('ki', KEYBDINPUT), ('mi', MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [('type', wintypes.DWORD), ('u', INPUTUNION)]


USER.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
USER.SendInput.restype = wintypes.UINT
USER.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
USER.PostMessageW.restype = wintypes.BOOL
USER.IsWindow.argtypes = [wintypes.HWND]
USER.IsWindow.restype = wintypes.BOOL


def key(up=False, hwnd=None):
    if hwnd is not None:
        # Address only the captured game window. Never fall back to SendInput.
        if not hwnd:
            raise ValueError(tr('Taustapainalluksen kohde puuttuu.'))
        flags = 1 | (0x39 << 16)
        if up:
            flags |= (1 << 30) | (1 << 31)
        if not USER.PostMessageW(hwnd, 0x0101 if up else 0x0100, 0x20, flags):
            raise OSError(tr('Taustaviestin lähetys epäonnistui. Tarkista pelin ja botin oikeustaso.'))
        return
    # Hardware scan code for space, not a text character.
    event = INPUT(type=1, u=INPUTUNION(ki=KEYBDINPUT(
        wVk=0, wScan=0x39, dwFlags=0x0008 | (0x0002 if up else 0))))
    if USER.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT)) != 1:
        raise OSError(tr('Näppäin ei mennyt peliin. Tarkista pelin ja botin oikeustaso.'))


def window_pid(hwnd):
    pid = wintypes.DWORD()
    USER.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def foreground():
    hwnd = USER.GetForegroundWindow()
    handle = KERNEL.OpenProcess(0x1000, False, window_pid(hwnd))
    if not handle:
        return hwnd, ''
    try:
        buf = ctypes.create_unicode_buffer(32768)
        size = wintypes.DWORD(len(buf))
        if not KERNEL.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
            return hwnd, ''
        return hwnd, Path(buf.value).name.lower()
    finally:
        KERNEL.CloseHandle(handle)


def resample(x, rate):
    if rate == RATE:
        return x.astype(np.float32)
    times = np.arange(int(round(len(x) * RATE / rate))) * rate / RATE
    return np.interp(times, np.arange(len(x)), x).astype(np.float32)


class App:
    def __init__(self, root):
        self.root = root
        try:
            saved_language=json.loads((BASE/'language.json').read_text(encoding='utf-8')).get('language','FIN')
        except (OSError,ValueError,TypeError,AttributeError):saved_language='FIN'
        set_language(saved_language)
        self.language=tk.StringVar(value=get_language())
        root.title('WoW Forever - Fishing bot')
        root.geometry('760x840')
        root.resizable(False, False)
        self.stop = threading.Event()
        self.events = queue.Queue(maxsize=30)
        self.audio_commands = queue.Queue()
        self.device_ids = []
        self.active = False
        self.ready = False
        self.down = False
        self.target = None
        self.target_pid = None
        self.held_hwnd = None
        self.session_background = False
        self.background = tk.BooleanVar(value=False)
        self.school = tk.BooleanVar(value=True)
        self.only_wow = tk.BooleanVar(value=True)
        self.nearby = tk.BooleanVar(value=False)
        self.babysit = tk.BooleanVar(value=False)
        self.break_due = None
        self.break_until = None
        self.break_plan = []
        self.break_count = 0
        self.break_number = 0
        self.baby_text = I18nVar(value=tr('Babysit pois päältä'))
        self.min_db = tk.DoubleVar(value=-36.0)
        self.volume_text = I18nVar(value=tr('Osumataso: ei vielä osumaa | Äänenvoimakkuusraja -36 dBFS'))
        self.audio_threshold = 2.0
        self.phase = 'paused'
        self.deadline = 0
        self.cast_expiry = None
        self.recoveries = 0
        self.watchdog = I18nVar(value=tr('Varoheitto: 32-35 s ilman tunnistettua nostoa'))
        self.threshold = tk.DoubleVar(value=2.0)
        self.status = I18nVar(value=tr('Avataan äänilaitetta...'))
        self.device = I18nVar(value=tr('Äänilaite: avataan Windowsin oletusulostuloa'))
        self.meter = I18nVar(value=tr('Osumatarkkuus 0.00 | Äänitaso 0.0000'))
        self.peak = 0.0
        self.peak_at = 0.0
        self.diagnostic = I18nVar(value=tr('Odotetaan äänivirtaa...'))
        self.counter = 0
        self.started = time.monotonic()
        self.previous = {0x77: False, 0x78: False}
        language_row=ttk.Frame(root)
        language_row.pack(pady=4)
        ttk.Label(language_row,text='Language / Kieli:').pack(side='left',padx=6)
        for code in ('ENG','FIN'):
            ttk.Radiobutton(language_row,text=code,value=code,variable=self.language,
                            command=self.change_language).pack(side='left',padx=5)
        for text, font in [('WoW Forever - Fishing bot', ('Segoe UI', 18, 'bold')),
                           (tr('F8 = käynnistä / tauko     F9 = lopeta'), ('Segoe UI', 11))]:
            I18nLabel(root, text=text, font=font).pack(pady=8)
        I18nLabel(root, textvariable=self.status, wraplength=530).pack(pady=10)
        I18nCheckbutton(root, text=tr('Taustatila (kokeellinen): painallukset vain WoW-ikkunaan'),
                        variable=self.background, command=self.mode_changed).pack(pady=5)
        I18nLabel(root, textvariable=self.watchdog).pack(pady=3)
        I18nCheckbutton(root,text=tr('Babysit: 1–2 taukoa 52–109 min aikaikkunassa (1:02–4:18)'),
                        variable=self.babysit,command=self.babysit_changed).pack(pady=3)
        I18nLabel(root,textvariable=self.baby_text).pack(pady=2)
        I18nCheckbutton(root, text=tr('Kuuntele vain WoWia (striimien äänet eivät kuulu bottiin)'),
                        variable=self.only_wow,command=self.source_changed).pack(pady=4)
        I18nCheckbutton(root,text=tr('Muita pelaajia vieressä? Hylkää hiljaiset molskahdukset'),
                        variable=self.nearby).pack(pady=3)
        I18nLabel(root,textvariable=self.volume_text).pack(pady=2)
        ttk.Scale(root,from_=-65,to=-15,variable=self.min_db,orient='horizontal',length=400,
                  command=lambda value:self.volume_text.set(tr('Äänenvoimakkuusraja {v0:.1f} dBFS (oikealle = tiukempi)', v0=float(value)))).pack()
        I18nCheckbutton(root, text=tr('Kalaparvisuodatus: tarkista äänen rakenne ennen nostoa'),
                        variable=self.school, command=self.school_changed).pack(pady=4)
        I18nLabel(root, textvariable=self.device, wraplength=530).pack(pady=4)
        self.device_picker = ttk.Combobox(root, state='readonly', width=85)
        self.device_picker.pack(pady=4)
        self.device_picker.bind('<<ComboboxSelected>>', self.select_device)
        I18nLabel(root, text=tr('Kalaparvisuodatus lisää noin 0,5 s tunnistusviivettä.')).pack()
        I18nLabel(root, textvariable=self.meter).pack(pady=6)
        self.level = ttk.Progressbar(root, length=420, maximum=100)
        self.level.pack(pady=3)
        I18nLabel(root, textvariable=self.diagnostic, wraplength=620).pack(pady=6)
        I18nLabel(root, text=tr('Voimistumiskerroin: pienempi = herkempi (oletus 2,0)')).pack()
        ttk.Scale(root, from_=1.3, to=8.0, variable=self.threshold,
                  orient='horizontal', length=400,
                  command=lambda value: setattr(self,'audio_threshold',float(value))).pack()
        I18nLabel(root, text=tr('Vain WoW -tilassa äänilaitevalikkoa ei käytetä. F8 valitsee WoWin.\nHeitä ensin itse, siirry WoWiin ja paina F8.\nTaustatilassa voit tämän jälkeen vaihtaa toiseen ohjelmaan.\nNormaalitilassa ikkunan vaihto tauottaa. F8 tauottaa molemmissa tiloissa.'),
                  justify='center').pack(pady=12)
        I18nButton(root, text=tr('Lopeta (F9)'), command=self.close).pack()
        root.protocol('WM_DELETE_WINDOW', self.close)
        threading.Thread(target=self.capture, daemon=True).start()
        root.after(20, self.tick)

    def post(self, event):
        try:
            self.events.put_nowait(event)
        except queue.Full:
            # UI overload: discard old detections rather than replaying them later.
            try:
                self.events.get_nowait()
            except queue.Empty:
                pass
            self.events.put_nowait(event)

    def change_language(self):
        set_language(self.language.get())
        try:
            (BASE/'language.json').write_text(json.dumps({'language':get_language()}),encoding='utf-8')
        except OSError:
            logging.exception('Could not save language preference')

    def capture(self):
        try:
            school_mode = True
            only_wow = True
            pid = None
            waiting_announced = False
            with pa.PyAudio() as p:
                devices = list(p.get_loopback_device_info_generator())
                if not devices:
                    raise RuntimeError(tr('Ei toistoäänilaitteita. Tarkista kuulokkeet/kaiuttimet.'))
                default = p.get_default_wasapi_loopback()
                index = int(default['index'])
                self.post(('devices', [(int(d['index']), d['name']) for d in devices], index))

                def command_update(command):
                    nonlocal index,only_wow,pid,school_mode,waiting_announced
                    if command[0]=='device':index=command[1]
                    elif command[0]=='school':school_mode=command[1]
                    elif command[0]=='only':
                        only_wow=command[1];pid=None;waiting_announced=False
                    elif command[0]=='process':
                        only_wow=True;pid=command[1];waiting_announced=False

                while not self.stop.is_set():
                    if only_wow and pid is None:
                        if not waiting_announced:
                            self.post(('ready',tr('Vain WoW: siirry peliin ja paina F8')))
                            waiting_announced=True
                        try:command_update(self.audio_commands.get(timeout=.1))
                        except queue.Empty:pass
                        continue
                    source=None
                    try:
                        if only_wow:
                            source=ProcessLoopback(pid)
                            rate,channels=source.rate,source.channels
                            label=tr('Vain WoW (PID {v0}) - muut sovellukset ohitetaan', v0=pid)
                        else:
                            device=p.get_device_info_by_index(index)
                            rate=int(device['defaultSampleRate']);channels=int(device['maxInputChannels'])
                            source=p.open(format=pa.paFloat32,channels=channels,rate=rate,input=True,
                                          input_device_index=index,frames_per_buffer=int(round(rate*.04)))
                            label=tr('KAIKKI äänet: ')+str(device['name'])
                        detector=StereoSchoolDetector(channels) if school_mode else BurstDetector()
                        self.post(('ready',label))
                        while not self.stop.is_set():
                            switched=False
                            while True:
                                try:command=self.audio_commands.get_nowait()
                                except queue.Empty:break
                                command_update(command);switched=True
                            if switched:break
                            if isinstance(source,ProcessLoopback):
                                packet=source.read(timeout=.1)
                                if packet is None:continue
                                x,gap=packet
                                if gap:detector.reset()
                            else:
                                raw=source.read(int(round(rate*.04)),exception_on_overflow=True)
                                x=np.frombuffer(raw,dtype=np.float32).reshape(-1,channels)
                            if isinstance(detector,StereoSchoolDetector):
                                audio=np.stack([resample(x[:,c],rate) for c in range(channels)],axis=1)
                                score,rms=detector.feed(audio,threshold=self.audio_threshold)
                                raw_score=detector.last_ratio
                                event_level=detector.last_peak if score else rms
                            else:
                                channel=int(np.argmax(np.mean(x*x,axis=0)))
                                mono=resample(x[:,channel],rate)
                                score,rms=detector.feed(mono);raw_score=score;event_level=rms
                            self.post(('score',time.monotonic(),score,rms,raw_score,event_level))
                    except Exception as exc:
                        logging.exception('Audio source failed')
                        self.post(('error',exc))
                        if only_wow:
                            pid=None;waiting_announced=True
                        else:
                            # Wait for an explicit source/device command; no automatic fallback.
                            while not self.stop.is_set():
                                try:command_update(self.audio_commands.get(timeout=.1));break
                                except queue.Empty:pass
                    finally:
                        if source is not None:source.close()
        except Exception as exc:
            logging.exception('Audio failed')
            self.post(('error', exc))

    def source_changed(self):
        self.pause(tr('Äänilähde vaihtui. Siirry WoWiin ja käynnistä F8:lla.'))
        self.ready=False
        self.audio_commands.put(('only',bool(self.only_wow.get())))

    def volume_allows(self,level):
        return not self.nearby.get() or 20*np.log10(max(level,1e-8))>=self.min_db.get()

    def select_device(self, event=None):
        choice = self.device_picker.current()
        if choice < 0 or choice >= len(self.device_ids):
            return
        self.pause(tr('Vaihdetaan äänilaitetta...'))
        self.ready = False
        self.audio_commands.put(('device', self.device_ids[choice]))

    def school_changed(self):
        self.pause(tr('Suodatus vaihtui. Heitä ensin itse ja jatka F8:lla.'))
        self.audio_commands.put(('school',bool(self.school.get())))

    def release(self):
        if self.down:
            try:
                if self.held_hwnd is None:
                    key(up=True)
                elif self.target_alive():
                    key(up=True, hwnd=self.held_hwnd)
            finally:
                self.down = False
                self.held_hwnd = None

    def target_alive(self):
        return bool(self.target and USER.IsWindow(self.target) and
                    window_pid(self.target) == self.target_pid)

    def can_send(self):
        if self.session_background:
            return self.target_alive()
        return USER.GetForegroundWindow() == self.target

    def mode_changed(self):
        self.pause(tr('Tila vaihtui. Heitä ensin itse ja käynnistä WoWissa F8:lla.'))

    def arm_babysit(self,now):
        self.break_plan=[]
        self.break_count=0
        self.break_number=0
        self.break_due=None
        if self.babysit.get():
            self.break_count=random.randint(1,2)
            self.break_plan=sorted(now+random.uniform(52*60,109*60) for _ in range(self.break_count))
            self.break_due=self.break_plan.pop(0)

    def schedule_after_break(self,now):
        if not self.babysit.get():
            self.break_plan=[]
            self.break_due=None
        elif self.break_plan:
            # Keep the second slot in the same time window, even if already due.
            # The recast/cooldown state machine guarantees a cast between breaks.
            self.break_due=self.break_plan.pop(0)
        else:
            self.arm_babysit(now)

    def babysit_changed(self):
        if self.babysit.get():
            if self.active:self.arm_babysit(time.monotonic())
        else:
            self.break_due=None
            self.break_plan=[]
            self.break_count=0
            self.break_number=0
            if self.phase=='babysit_break':
                self.pause(tr('Babysit poistettiin tauolla. Heitä itse ja jatka F8:lla.'))

    def break_is_due(self,now):
        return self.babysit.get() and self.break_due is not None and now>=self.break_due

    def start_break(self,now):
        self.release()
        self.phase='babysit_break'
        self.cast_expiry=None
        self.break_due=None
        self.break_number+=1
        self.break_until=now+random.uniform(62,258)
        self.status.set(tr('Babysit-tauko {v0}/{v1}. Jatketaan automaattisesti uudella heitolla.', v0=self.break_number, v1=self.break_count))
        logging.info('Babysit break %.1f seconds',self.break_until-now)

    @staticmethod
    def duration_text(seconds):
        seconds=max(0,int(seconds+.999))
        return f'{seconds//60}:{seconds%60:02d}'

    def update_babysit_text(self,now):
        if self.active and self.phase=='babysit_break':
            self.baby_text.set(tr('Babysit-tauko {v0}/{v1}: jäljellä ', v0=self.break_number, v1=self.break_count)+self.duration_text(self.break_until-now))
        elif self.active and self.break_due is not None:
            if now>=self.break_due:self.baby_text.set(tr('Babysit-tauko alkaa tämän heiton päätyttyä.'))
            else:self.baby_text.set(tr('Babysit-tauko {v0}/{v1} noin ',v0=self.break_number+1,v1=self.break_count)+self.duration_text(self.break_due-now)+tr(' kuluttua'))
        elif self.babysit.get():self.baby_text.set(tr('Babysit valittu. Ajastus alkaa F8-käynnistyksestä.'))
        else:self.baby_text.set(tr('Babysit pois päältä'))

    def pause(self, reason=tr('Tauolla. F8 jatkaa.')):
        self.active = False
        self.phase = 'paused'
        self.cast_expiry = None
        self.break_due = None
        self.break_until = None
        self.break_plan = []
        self.break_count = 0
        self.break_number = 0
        self.release()
        self.status.set(reason)

    def toggle(self):
        if self.active:
            self.pause()
            return
        if not self.ready and not self.only_wow.get():
            self.status.set(tr('Äänikuuntelu ei ole valmis. Katso virhe tai odota hetki.'))
            return
        hwnd, name = foreground()
        if not (name.startswith('wow') and name.endswith('.exe')):
            self.status.set(tr('Vaihda WoW-ikkunaan ja paina siellä F8. Tunnistettu: ') + (name or '?'))
            return
        self.target = hwnd
        self.target_pid = window_pid(hwnd)
        if self.only_wow.get():
            self.audio_commands.put(('process',self.target_pid))
        self.session_background = bool(self.background.get())
        self.active = True
        self.phase = 'cooldown'
        now = time.monotonic()
        self.deadline = now + 2.0
        # The first cast is manual; F8 is its timer reference.
        self.cast_expiry = now + random.uniform(32.0, 35.0)
        self.started = self.deadline
        self.arm_babysit(now)
        mode = tr('tausta, kokeellinen') if self.session_background else tr('normaali')
        self.status.set(tr('Käynnissä ({v0}). Odotetaan molskahdusta...', v0=mode))

    def press(self, now, phase):
        if not self.can_send():
            self.pause(tr('WoW-kohde ei ole käytettävissä. Heitä uudelleen ja jatka F8:lla.'))
            return
        self.held_hwnd = self.target if self.session_background else None
        if self.held_hwnd is None:
            key()
        else:
            key(hwnd=self.held_hwnd)
        self.down = True
        self.phase = phase
        if phase == 'lift_down':
            self.cast_expiry = None
            self.recast_at = now + random.uniform(1.0, 1.6)
        elif phase == 'cast_down':
            self.cast_expiry = now + random.uniform(32.0, 35.0)
        self.deadline = now + random.uniform(.055, .13)

    def step(self, now):
        if not self.active:
            return
        if self.phase=='babysit_break':
            if now>=self.break_until:
                self.press(now,'cast_down')
                if self.active and self.phase=='cast_down':
                    self.break_until=None
                    self.schedule_after_break(now)
                    self.started=now+3.0
                    self.status.set(tr('Babysit-tauko päättyi. Uusi heittopainallus lähetetty.'))
            return
        if (self.phase == 'listening' and self.cast_expiry is not None and
                now >= self.cast_expiry):
            if self.break_is_due(now):
                self.start_break(now)
                return
            # Channel has timed out: one new cast, never a lift/recast pair.
            self.press(now, 'cast_down')
            if self.active and self.phase == 'cast_down':
                self.recoveries += 1
                self.status.set(tr('Ei tunnistettua nostoa 32-35 s: uusi heitto. Varoheitot {v0}.', v0=self.recoveries))
                logging.info('Watchdog recast count=%d', self.recoveries)
            return
        if self.phase == 'reaction' and now >= self.deadline:
            self.press(now, 'lift_down')
        elif self.phase == 'lift_down' and now >= self.deadline:
            self.release()
            self.phase = 'recast_wait'
            self.deadline = self.recast_at
        elif self.phase == 'recast_wait' and now >= self.deadline:
            if self.break_is_due(now):self.start_break(now)
            else:self.press(now, 'cast_down')
        elif self.phase == 'cast_down' and now >= self.deadline:
            self.release()
            self.counter += 1
            self.phase = 'cooldown'
            self.deadline = now + 3.0
            self.status.set(tr('Heittopainallus lähetetty. Syklejä: {v0}. Odotetaan...', v0=self.counter))
        elif self.phase == 'cooldown' and now >= self.deadline:
            self.phase = 'listening'

    def tick(self):
        if self.stop.is_set():
            return
        try:
            for vk in self.previous:
                pressed = bool(USER.GetAsyncKeyState(vk) & 0x8000)
                if pressed and not self.previous[vk]:
                    if vk == 0x78:
                        self.close()
                        return
                    self.toggle()
                self.previous[vk] = pressed
            now = time.monotonic()
            if self.active and not self.can_send():
                self.pause(tr('Ikkuna vaihtui tai WoW sulkeutui. Heitä uudelleen ja jatka F8:lla.'))
            while True:
                try:
                    event = self.events.get_nowait()
                except queue.Empty:
                    break
                if event[0] == 'devices':
                    self.device_ids = [d[0] for d in event[1]]
                    self.device_picker['values'] = [d[1] for d in event[1]]
                    self.device_picker.current(self.device_ids.index(event[2]))
                elif event[0] == 'ready':
                    self.ready = True
                    self.device.set(tr('Äänilaite: ') + event[1])
                    if not self.active:self.status.set(tr('Valmis. Heitä ensin itse ja paina WoWissa F8.'))
                elif event[0] == 'error':
                    self.ready = False
                    self.pause(tr('Äänivirhe: ') + event[1])
                else:
                    _, stamp, score, rms, *extra = event
                    raw_score = extra[0] if extra else score
                    event_level = extra[1] if len(extra)>1 else rms
                    if score>=self.threshold.get():
                        db=20*np.log10(max(event_level,1e-8))
                        verdict=tr('hyväksytty') if self.volume_allows(event_level) else tr('liian hiljainen')
                        self.volume_text.set(tr('Viimeisin osuma {v0:.1f} dBFS: {v1} | Raja {v2:.1f} dBFS', v0=db, v1=verdict, v2=self.min_db.get()))
                    if now - self.peak_at > 5:
                        self.peak = 0.0
                    if score >= self.peak:
                        self.peak, self.peak_at = score, now
                    self.meter.set(tr('Piikki {v0:.2f}x | Hyväksytty {v1:.2f}x | Raja {v2:.2f}x | Ääni {v3:.5f}', v0=raw_score, v1=self.peak, v2=self.threshold.get(), v3=rms))
                    self.level['value'] = min(100, max(0, 20*np.log10(max(rms, 1e-8)) + 100))
                    if rms < .0001:
                        self.diagnostic.set(tr('Äänivirta on hiljainen. Jos peli soi, valitse toinen äänilaite yllä.'))
                    elif self.school.get() and self.peak < self.threshold.get():
                        self.diagnostic.set(tr('Suodatus odottaa sopivan rakenteista molskahdusta. Pelkkä voimakas piikki ei riitä nostoon.'))
                    elif self.peak < self.threshold.get():
                        self.diagnostic.set(tr('Ääntä tulee. Jos molskahdus jää rajan alle, laske kerrointa hieman.'))
                    else:
                        self.diagnostic.set(tr('Äänipiikki ylitti rajan. Käynnistä F8:lla. Taustatilan pelituki täytyy kokeilla.'))
                    if (self.active and self.phase == 'listening' and
                            stamp >= self.started and 0 <= now - stamp < .25 and
                            rms > .0001 and score >= self.threshold.get() and self.volume_allows(event_level)):
                        self.phase = 'reaction'
                        self.deadline = now + random.uniform(.20, .50)
                        self.status.set(tr('Äänipiikki ({v0:.2f}x). Nostetaan...', v0=score))
                        logging.info('Detection score=%.3f rms=%.5f', score, rms)
            if self.active:
                self.step(time.monotonic())
            self.update_babysit_text(time.monotonic())
            if self.active and self.phase=='babysit_break':
                self.watchdog.set(tr('Varoheitto tauolla Babysit-tauon ajan'))
            elif self.active and self.cast_expiry is not None:
                remaining = max(0, self.cast_expiry-time.monotonic())
                self.watchdog.set(tr('Varoheitto {v0:.1f} s kuluttua ilman tunnistettua nostoa | Tehty {v1}', v0=remaining, v1=self.recoveries))
            elif self.active:
                self.watchdog.set(tr('Nostetaan / heitetään uudelleen...'))
            else:
                self.watchdog.set(tr('Varoheitto tauolla (32-35 s käynnistyksen/heiton jälkeen)'))
        except Exception as exc:
            logging.exception('Controller failed')
            self.pause(tr('Virhe: ') + exc)
        self.root.after(20, self.tick)

    def close(self):
        self.stop.set()
        try:
            self.release()
        finally:
            self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()
