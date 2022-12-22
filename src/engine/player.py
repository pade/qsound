import logging
from multiprocessing import Process, Queue
from queue import Full, Empty
from enum import Enum
from typing import Optional, Any

from pyaudio import PyAudio
from pydub import AudioSegment
from PySide6.QtCore import QObject, QThread, Signal
from cue.volume import Volume
from cue.fade import Fade

logger = logging.getLogger(__name__)


class PlayerStates (Enum):
    NotStarted = 0
    Playing = 1
    Paused = 2
    Stopped = 3
    Ended = 4


class InvalidCommand(Exception):
    pass


class InvalidMessage(Exception):
    pass


class PlayerCommand:
    availableCommands = [
        'elapsedTime', 'state', 'quit',
        'pause', 'play', 'stop', 'volume', 'fade', 'loop',
        'setStart', 'setEnd'
    ]

    def __init__(self, command: str, value: Any | None = None) -> None:
        if command in self.availableCommands:
            self.command = command
            self.value = value
        else:
            raise InvalidCommand

    @classmethod
    def fromMessage(cls, msg: dict):
        if type(msg) is not dict:
            raise InvalidMessage
        try:
            command = msg['command']
        except KeyError:
            raise InvalidMessage
        value = msg.get('value')
        return cls(command, value)

    def toMessage(self):
        if self.value is not None:
            return {'command': self.command, 'value': self.value}
        else:
            return {'command': self.command}

    def __str__(self) -> str:
        return f'"{self.command}" ({self.value})'


class Player (QThread):

    elapsedTime = Signal(int, name='elapsedTime')
    changedState = Signal(PlayerStates, name='changedState')

    def __init__(self, audio: AudioSegment, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._audio = audio
        self._queueToProcess = Queue()
        self._queueFromProcess = Queue()

    def run(self):
        logger.debug('Starting thread')
        player = PlayerProcess(self._audio)
        
        process = Process(target=player.playerProcess, args=(self._queueToProcess, self._queueFromProcess))
        process.start()
        while not self.isInterruptionRequested():
            try:
                msg = PlayerCommand.fromMessage(self._queueFromProcess.get(block=True, timeout=0.5))
                match msg.command:
                    case 'elapsedTime':
                        logger.debug(f'Received command "elapsedTime" ({msg.value})')
                        self.elapsedTime.emit(msg.value)
                    case 'state':
                        logger.debug(f'Received command "state" ({msg.value})')
                        self.changedState.emit(msg.value)
            except (InvalidMessage):
                logger.error(f'Wrong message: "{msg}"')
            except Empty:
                # No message received, nothing to do
                pass
        self._queueToProcess.put(PlayerCommand('quit').toMessage())
        process.join()

    def pause(self):
        self._queueToProcess.put(PlayerCommand('pause').toMessage())

    def play(self):
        self._queueToProcess.put(PlayerCommand('play').toMessage())

    def stop(self):
        self._queueToProcess.put(PlayerCommand('stop').toMessage())

    def setVolume(self, volume: Volume):
        self._queueToProcess.put(PlayerCommand('volume', volume).toMessage())

    def setFade(self, fade: Fade):
        self._queueToProcess.put(PlayerCommand('fade', fade).toMessage())

    def setLoop(self, loop: int):
        self._queueToProcess.put(PlayerCommand('loop', loop).toMessage())

    def setStart(self, seconds: float):
        self._queueToProcess.put(PlayerCommand('setStart', seconds).toMessage())

    def setEnd(self, seconds: float):
        self._queueToProcess.put(PlayerCommand('setEnd', seconds).toMessage())

    def quit(self):
        if self.isRunning():
            self.requestInterruption()
            while not self.isFinished():
                # Wait end of process and thread
                pass


class PlayerProcess:

    CHUNK_SIZE = 100.0

    def __init__(self, audio: AudioSegment):
        self._audio = audio
        self._startsMs = 0.0
        self._endsMs = audio.duration_seconds * 1000.0
        self._loop = 0
        self._playerState = PlayerStates.NotStarted
        self._playerOldState = None
        self._volume = Volume()
        self.lastSentElapsedTime = 0

    def playerProcess(self, queueIn: Queue, queueOut: Queue):
        self.queueIn = queueIn
        self.queueOut = queueOut
        logger.debug('Starting player process')
        try:
            player = PyAudio()
            stream = player.open(
                format=player.get_format_from_width(self._audio.sample_width),
                channels=self._audio.channels,
                rate=self._audio.frame_rate,
                output=True,
            )
            # Copy audio to not change it
            audioToPlay = AudioSegment.empty() + self._audio
            loop = self._loop
            repeatInfiny = loop == -1
            # Set playing at start cursor
            elapsedTime = self._startsMs
            self.lastSentElapsedTime = elapsedTime
            logger.debug(f'Playing from {self._startsMs}ms to {self._endsMs}ms')
            while True:
                blocked = self._playerState != PlayerStates.Playing
                try:
                    msg = PlayerCommand.fromMessage(self.queueIn.get(block=blocked))
                    logger.debug(f'Receive message from main app.: "{msg}"')
                    match msg.command:
                        case 'play':
                            self.setPlayerState(PlayerStates.Playing)
                        case 'pause':
                            self.setPlayerState(PlayerStates.Paused)
                        case 'stop':
                            self.setPlayerState(PlayerStates.Stopped)
                        case 'volume':
                            self._volume: Volume = msg.value
                        case 'fade':
                            fade: Fade = msg.value
                            self.setPlayerState(PlayerStates.Stopped)
                            audioToPlay = self._applyFade(self._audio, fade)
                        case 'loop':
                            self._loop = msg.value
                            self.setPlayerState(PlayerStates.Stopped)
                        case 'setStart':
                            self._startsMs = msg.value * 1000.0
                            self.setPlayerState(PlayerStates.Stopped)
                        case 'setEnd':
                            self._endsMs = msg.value * 1000.0
                            self.setPlayerState(PlayerStates.Stopped)
                        case 'quit':
                            self.setPlayerState(PlayerStates.Ended)
                except InvalidMessage:
                    logger.error(f'Wrong message: "{msg}"')
                except Empty:
                    # No message received, nothing to do
                    pass

                if self.getPlayerState() == PlayerStates.Playing:
                    if elapsedTime >= self._endsMs:
                        if repeatInfiny or loop > 0:
                            loop = loop - 1
                            elapsedTime = self._startsMs
                        else:
                            self.setPlayerState(PlayerStates.Stopped)
                            # Reset reading cursor and number of loops
                            elapsedTime = self._startsMs
                            loop = self._loop
                            repeatInfiny = loop == -1
                    else:
                        segmentSize = min(self._endsMs, elapsedTime+self.CHUNK_SIZE)
                        data = self._applyVolume(audioToPlay[elapsedTime:segmentSize], self._volume)
                        self.sendElapsedTime(len(data) + elapsedTime)
                        if len(data) == 0:
                            if repeatInfiny or loop > 0:
                                loop = loop - 1
                                elapsedTime = self._startsMs
                            else:
                                self.setPlayerState(PlayerStates.Stopped)
                                # Reset reading cursor and number of loops
                                elapsedTime = self._startsMs
                                loop = self._loop
                                repeatInfiny = loop == -1
                        else:
                            self.setPlayerState(PlayerStates.Playing)
                            stream.write(data.raw_data)
                            elapsedTime += self.CHUNK_SIZE
                elif self.getPlayerState() == PlayerStates.Ended:
                    # Quit process
                    break
                elif self.getPlayerState() == PlayerStates.Stopped:
                    # Reset reading cursor and number of loops
                    elapsedTime = self._startsMs
                    loop = self._loop
                    repeatInfiny = loop == -1
                    self.sendElapsedTime(elapsedTime)
        finally:
            stream.stop_stream()
            stream.close()
            player.terminate()

    def _applyVolume(self, audio: AudioSegment, volume: Volume) -> AudioSegment:
        # Copy audio to not change it
        segment = AudioSegment.empty() + audio
        if volume.left or volume.right:
            left, right = audio.split_to_mono()
            if volume.left == Volume.MIN:
                left = left - 120.0
            else:
                left = left + volume.left
            if volume.right == Volume.MIN:
                right = right - 120
            else:
                right = right + volume.right
            segment = AudioSegment.from_mono_audiosegments(left, right)
        if volume.master:
            if volume.master == Volume.MIN:
                segment = segment - 120
            else:
                segment = segment + volume.master
        return segment

    def _applyFade(self, audio: AudioSegment, fade: Fade) -> AudioSegment:
        fadeIn = round(fade.fadeIn * 1000)
        fadeOut = round(fade.fadeOut * 1000)
        # Copy audio to not change it
        segment = AudioSegment.empty() + audio
        if fadeIn:
            start = round(self._startsMs)
            segment = segment.fade(to_gain=0, from_gain=-120, start=start, duration=fadeIn)
        if fadeOut:
            end = round(self._endsMs)
            segment = segment.fade(to_gain=-120, from_gain=0, end=end, duration=fadeOut)
        return segment

    def setPlayerState(self, state: PlayerStates) -> None:
        self._playerState = state
        if self._playerOldState != self._playerState:
            self._playerOldState = state
            try:
                self.queueOut.put_nowait({'command': 'state', 'value': self._playerState})
            except Full:
                # Impossible to send player state, quit player
                self._state = PlayerStates.Ended

    def getPlayerState(self) -> PlayerStates:
        return self._playerState

    def sendElapsedTime(self, elapsedTime: int) -> None:
        # Send elapsedTime only every 250ms
        if abs(elapsedTime - self.lastSentElapsedTime) > 250:
            try:
                self.queueOut.put_nowait({'command': 'elapsedTime', 'value': elapsedTime})
            except Full:
                # Impossible to send elapsed time
                # This is not a blocking point
                pass
            finally:
                self.lastSentElapsedTime = elapsedTime

