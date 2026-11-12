from ui_text import tr
"""Streaming spectral template matching; no microphone or screen processing."""
import numpy as np
from collections import deque

RATE = 16000
HOP = 320
FFT = 512
EDGES = np.unique(np.geomspace(4, FFT // 2, 33).astype(int))
WINDOW = np.hanning(FFT).astype(np.float32)


def features(audio):
    x = np.asarray(audio, dtype=np.float32).reshape(-1)
    if len(x) < FFT:
        return np.empty((0, len(EDGES) - 1), dtype=np.float32)
    frames = np.lib.stride_tricks.sliding_window_view(x, FFT)[::HOP]
    power = np.abs(np.fft.rfft(frames * WINDOW, axis=1)) ** 2
    bands = np.stack([power[:, a:b].mean(axis=1)
                      for a, b in zip(EDGES[:-1], EDGES[1:])], axis=1)
    # Relative log power makes the comparison independent of playback volume.
    floor = np.maximum(bands.max(axis=1, keepdims=True) * 1e-4, 1e-12)
    bands = np.log(np.maximum(bands, floor))
    bands -= bands.mean(axis=1, keepdims=True)
    bands /= np.maximum(np.linalg.norm(bands, axis=1, keepdims=True), 1e-9)
    return bands.astype(np.float32)


def make_template(audio):
    x = np.asarray(audio, dtype=np.float32)
    if len(x) < int(.15 * RATE) or np.max(np.abs(x)) < 1e-6:
        raise ValueError(tr('Aan nayte on liian lyhyt tai ääneton.'))
    # Use a short, energetic section, so detection need not wait for the tail.
    n = min(len(x), int(.38 * RATE))
    cumulative = np.concatenate(([0.0], np.cumsum(x.astype(np.float64) ** 2)))
    energy = (cumulative[n:] - cumulative[:-n]) / n
    start = int(np.argmax(energy))
    return features(x[start:start + n])


class Detector:
    def __init__(self, template):
        self.template = np.asarray(template)
        self.samples = np.empty(0, dtype=np.float32)
        self.last = np.empty((0, template.shape[1]), dtype=np.float32)

    def reset(self):
        self.samples = np.empty(0, dtype=np.float32)
        self.last = self.last[:0]

    def feed(self, chunk):
        self.samples = np.concatenate((self.samples, np.asarray(chunk, dtype=np.float32)))
        if len(self.samples) < FFT:
            return 0.0, 0.0
        count = (len(self.samples) - FFT) // HOP + 1
        consumed = count * HOP
        fresh = features(self.samples[:(count - 1) * HOP + FFT])
        rms = float(np.sqrt(np.mean(self.samples[:consumed] ** 2)))
        self.samples = self.samples[consumed:]
        both = np.concatenate((self.last, fresh))
        n = len(self.template)
        score = 0.0
        for end in range(n, len(both) + 1):
            score = max(score, float(np.sum(both[end - n:end] * self.template) / n))
        self.last = both[-(n - 1):] if n > 1 else both[:0]
        return score, rms


class BurstDetector:
    """Detect an abrupt increase over recent audio, regardless of sound identity.

    This is a transient detector, not a splash classifier. Other loud effects
    can trigger it. Windows loopback is supplied as 40 ms chunks at 16 kHz.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.history = deque(maxlen=25)

    def feed(self, chunk):
        x = np.asarray(chunk, dtype=np.float32)
        if len(x) < 8:
            return 0.0, 0.0
        rms = float(np.sqrt(np.mean(x*x)))
        # Exclude bass rumble while keeping the broad splash frequency range.
        window = np.hanning(len(x))
        spectrum = np.abs(np.fft.rfft((x-x.mean())*window))**2
        frequencies = np.fft.rfftfreq(len(x), 1/RATE)
        mask = (frequencies >= 300) & (frequencies <= 7500)
        level = float(np.sqrt(2*spectrum[mask].sum() /
                              max(len(x)**2 * np.mean(window**2), 1)))
        score = 0.0
        if len(self.history) == self.history.maxlen and level > .0002:
            long_background = float(np.median(self.history))
            short_background = float(np.mean(list(self.history)[-3:]))
            background = max(long_background, short_background, .00005)
            score = level / background
        self.history.append(level)
        return score, rms


class SchoolDetector:
    """Confirm a transient's spectrum and persistence over 480 ms.

    Based on two labelled catches and four non-catch events in one recording.
    This is a heuristic, not proof of a bite; expose the plain detector as fallback.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.burst = BurstDetector()
        self.samples = np.empty(0, dtype=np.float32)
        self.pending = []
        self.frame = 0
        self.next_candidate = 0
        self.refractory_until = 0
        self.last_ratio = 0.0
        self.last_peak = 0.0

    def feed(self, chunk, threshold=2.0):
        chunk = np.asarray(chunk, dtype=np.float32)
        rms = float(np.sqrt(np.mean(chunk*chunk))) if len(chunk) else 0.0
        self.samples = np.concatenate((self.samples,chunk))
        accepted = 0.0
        self.last_peak = 0.0
        while len(self.samples) >= 640:
            x = self.samples[:640]
            self.samples = self.samples[640:]
            ratio, _ = self.burst.feed(x)
            self.last_ratio = ratio
            p = np.abs(np.fft.rfft((x-x.mean())*np.hanning(640)))**2
            f = np.fft.rfftfreq(640,1/RATE)
            total = float(p[(f>=150)&(f<=7500)].sum())
            low = float(p[(f>=150)&(f<1200)].sum())
            if (ratio >= threshold and self.frame >= self.next_candidate and
                    self.frame >= self.refractory_until):
                self.pending.append({'ratio':ratio,'energy':[],'low':[],'rms':[]})
                self.next_candidate = self.frame + 6
            keep = []
            for candidate in self.pending:
                candidate['energy'].append(total)
                candidate['low'].append(low)
                candidate['rms'].append(float(np.sqrt(np.mean(x*x))))
                if len(candidate['energy']) < 12:
                    keep.append(candidate)
                    continue
                energy = np.asarray(candidate['energy'])
                bass_fraction = sum(candidate['low']) / max(float(energy.sum()),1e-20)
                tail_ratio = float(energy[6:].mean())/max(float(energy[:6].mean()),1e-20)
                persistence = float(np.median(np.sqrt(energy)))/max(float(np.sqrt(energy.max())),1e-20)
                if (.30 < bass_fraction < .90 and tail_ratio > .30 and
                        persistence > .20 and self.frame >= self.refractory_until):
                    accepted = max(accepted,candidate['ratio'])
                    self.last_peak = max(self.last_peak,max(candidate['rms']))
                    self.refractory_until = self.frame + 38
            self.pending = [] if accepted else keep
            self.frame += 1
        return accepted,rms


class StereoSchoolDetector:
    """Analyse channels independently, without switching mono channel per frame."""
    def __init__(self,channels):
        self.channels=channels
        self.reset()

    def reset(self):
        self.detectors=[SchoolDetector() for _ in range(self.channels)]
        self.hit_times=np.full(self.channels,-np.inf)
        self.hit_scores=np.zeros(self.channels)
        self.hit_levels=np.zeros(self.channels)
        self.levels=np.zeros(self.channels)
        self.position=0.0
        self.accepted_at=-np.inf
        self.last_ratio=0.0
        self.last_peak=0.0

    def feed(self,audio,threshold=2.0):
        audio=np.asarray(audio,dtype=np.float32)
        if audio.ndim==1:
            audio=audio[:,None]
        if audio.shape[1]!=self.channels:
            raise ValueError(tr('Äänikanavien maara vaihtui.'))
        self.position+=len(audio)/RATE
        self.last_peak=0.0
        rms=np.sqrt(np.mean(audio*audio,axis=0))
        self.levels=np.maximum(self.levels*.98,rms)
        for i,detector in enumerate(self.detectors):
            score,_=detector.feed(audio[:,i],threshold)
            if score:
                self.hit_times[i]=self.position
                self.hit_scores[i]=score
                self.hit_levels[i]=detector.last_peak
        self.last_ratio=max(d.last_ratio for d in self.detectors)
        # Entirely silent channels are ignored (e.g. mono routed into stereo).
        active=self.levels>max(1e-6,float(self.levels.max())*.01)
        score=0.0
        if (active.any() and self.position-self.accepted_at>1.5 and
                np.all(self.position-self.hit_times[active]<=.28)):
            score=float(self.hit_scores[active].min())
            self.last_peak=float(self.hit_levels[active].max())
            self.accepted_at=self.position
            self.hit_times[:]=-np.inf
        return score,float(rms.max())
