import logging
from aiogram import Router, F
from aiogram.types import Message
from io import BytesIO
import soundfile as sf
import json
import vosk

from config_data.config import bot
from handlers.user_handlers import chatgpt_answer
from lexicons import LEXICON_RU

lexicon = LEXICON_RU['voice_handlers']

voice_router: Router = Router()


@voice_router.message(F.voice)
async def process_voice_message(message: Message):
    """
    Function translate voice to text and call func chatgpt_answer with received data
    """
    try:
        file_id = message.voice.file_id
        file_path = await bot.get_file(file_id)
        file_data = await bot.download_file(file_path.file_path)
        model = vosk.Model("soft/vosk-model-small-ru-0.22")
        data, samplerate = sf.read(BytesIO(file_data.read()))
        with BytesIO() as output:
            sf.write(output, data, samplerate, format='wav')
            wav_data_bytesio = output.getvalue()
        recognizer = vosk.KaldiRecognizer(model, samplerate)
        recognizer.AcceptWaveform(wav_data_bytesio)
        result = recognizer.FinalResult()
        result_str = json.loads(result)['text']
        logging.info(f"vosk_text: {result_str}")
        updated_message = Message(
            message_id=message.message_id,
            chat=message.chat,
            from_user=message.from_user,
            date=message.date,
            text=result_str,
            voice=None
        )
        if result_str:
            await message.reply(result_str)
            await chatgpt_answer(updated_message)
        else:
            raise Exception
    except Exception as e:
        logging.error(e)
        logging.error(f"type_error: {type(e)}")
        await message.answer(lexicon["something_wrong"])
