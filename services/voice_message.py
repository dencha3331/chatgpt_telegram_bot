from __future__ import annotations

from logs import logger
from io import BytesIO
import soundfile as sf
import json
import vosk

"""Надо сделать через FSM чтоб пока не будет верного текста не отправлять в chatgpt_answer"""


async def process_voice_message(voice: bytes) -> str | None:
    """
    Function translate voice to text and call func chatgpt_answer with received data
    """
    try:
        model = vosk.Model("soft/vosk-model-small-ru-0.22")
        data, samplerate = sf.read(BytesIO(voice))
        with BytesIO() as output:
            sf.write(output, data, samplerate, format='wav')
            wav_data_bytesio = output.getvalue()
        recognizer = vosk.KaldiRecognizer(model, samplerate)
        recognizer.AcceptWaveform(wav_data_bytesio)
        result = recognizer.FinalResult()
        result_str = json.loads(result)['text']
        logger.info(f"vosk_text: {result_str}")
        return result_str

    except Exception as e:
        logger.error(f"error in process_voice_message: {e}")
        logger.error(f"type_error: {type(e)}")
        return
