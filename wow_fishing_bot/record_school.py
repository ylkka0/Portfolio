from ui_text import tr, set_language
"""User-started 45-second WAV capture for comparing small and real splashes."""
from datetime import datetime
from pathlib import Path
import time
import wave
import numpy as np
import pyaudiowpatch as pa

BASE = Path(__file__).resolve().parent


def main():
    set_language("ENG")
    print(tr('Sulje botti. Tallennetaan valitun laitteen KAIKKI toistoäänet 45 sekunnilta.'))
    print(tr('Hiljennä muut sovellukset. Kalasta itse kalaparvessa tallennuksen aikana.'))
    print(tr('Tarvitaan pienet molskahdukset ja oikea nostomolskahdus samaan tallenteeseen.'))
    with pa.PyAudio() as p:
        devices = list(p.get_loopback_device_info_generator())
        if not devices:
            raise RuntimeError(tr('Toistoäänilaitteita ei löytynyt.'))
        default = int(p.get_default_wasapi_loopback()['index'])
        chosen = next((i for i,d in enumerate(devices) if int(d['index']) == default), 0)
        for i,d in enumerate(devices):
            print(f'{i}: {d["name"]}' + (tr(' (oletus)') if i == chosen else ''))
        value = input(tr('Valitse laitteen numero, tai Enter = oletus: ')).strip()
        if value:
            chosen = int(value)
        if chosen < 0 or chosen >= len(devices):
            raise ValueError(tr('Virheellinen laitenumero.'))
        d = devices[chosen]
        rate = int(d['defaultSampleRate'])
        channels = int(d['maxInputChannels'])
        path = BASE / ('school_sample_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.wav')
        input(tr('Paina Enter aloittaaksesi. Siirry sitten WoWiin ja heitä itse: '))
        for i in range(3, 0, -1):
            print(i, flush=True)
            time.sleep(1)
        frames = int(round(rate*.1))
        print(tr('TALLENNUS KÄYNNISSA (45 s). Ohjelma ei paina mitään näppäinta.'), flush=True)
        with p.open(format=pa.paFloat32, channels=channels, rate=rate, input=True,
                    input_device_index=d['index'], frames_per_buffer=frames) as stream:
            with wave.open(str(path), 'wb') as output:
                output.setnchannels(channels)
                output.setsampwidth(2)
                output.setframerate(rate)
                remaining = 45 * rate
                while remaining > 0:
                    n = min(frames, remaining)
                    raw = stream.read(n, exception_on_overflow=True)
                    audio = np.frombuffer(raw, dtype=np.float32)
                    output.writeframesraw((np.clip(audio, -1, 1)*32767).astype('<i2').tobytes())
                    remaining -= n
        print(tr('Valmis! Lähetä tämä WAV-tiedosto keskusteluun:\n') + str(path))
        print(tr('Kerro, missä kohdassa kuului oikea nostomolskahdus, jos tiedat.'))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(tr('Tallennus epäonnistui:'), exc)
        raise SystemExit(1)
