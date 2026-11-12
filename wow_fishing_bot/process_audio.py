from ui_text import tr
"""Read only one Windows process tree's audio, without changing playback routing."""
from pathlib import Path
import queue
import os
import struct
import subprocess
import threading
import time
import numpy as np

BASE=Path(__file__).resolve().parent


class ProcessLoopback:
    rate=48000
    channels=2

    def __init__(self,pid):
        self.pid=int(pid)
        self.queue=queue.Queue(maxsize=12)
        self.closed=threading.Event()
        self.error=None
        self.gap=False
        self.log=open(BASE/'process_audio.log','ab',buffering=0)
        try:
            self.process=subprocess.Popen([str(BASE/'ProcessAudio.exe'),str(self.pid),str(os.getpid())],
                stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=self.log,
                creationflags=subprocess.CREATE_NO_WINDOW,bufsize=0)
        except Exception:
            self.log.close()
            raise
        self.reader=threading.Thread(target=self._read,daemon=True)
        self.reader.start()

    def _exact(self,n):
        chunks=[]
        while n:
            data=self.process.stdout.read(n)
            if not data:
                raise RuntimeError(tr('WoW-äänikuuntelu pysähtyi. Katso process_audio.log.'))
            chunks.append(data);n-=len(data)
        return b''.join(chunks)

    def _read(self):
        try:
            header=self._exact(12)
            if struct.unpack('<4sII',header)!=(b'WPCM',48000,2):
                raise RuntimeError(tr('WoW-äänikuuntelun äänimuoto on virheellinen.'))
            while not self.closed.is_set():
                raw=self._exact(1920*2*2)
                item=(time.monotonic(),np.frombuffer(raw,dtype='<i2').reshape(-1,2).astype(np.float32)/32768)
                try:self.queue.put_nowait(item)
                except queue.Full:
                    self.gap=True
                    try:self.queue.get_nowait()
                    except queue.Empty:pass
                    self.queue.put_nowait(item)
        except Exception as exc:
            if not self.closed.is_set():self.error=exc

    def read(self,timeout=.1):
        try:
            stamp,audio=self.queue.get(timeout=timeout)
        except queue.Empty:
            if self.error:raise self.error
            return None
        if time.monotonic()-stamp>.25:
            self.gap=True
            return None
        gap=self.gap;self.gap=False
        return audio,gap

    def close(self):
        self.closed.set()
        if self.process.poll() is None:
            self.process.terminate()
            try:self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=2)
        self.reader.join(timeout=2)
        self.process.stdout.close()
        self.log.close()

    def __enter__(self):return self
    def __exit__(self,*args):self.close()
