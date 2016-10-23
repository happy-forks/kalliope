import requests
import re
from core import FileManager
from core.TTS.TTSModule import TTSModule, FailToLoadSoundFile
import logging

logging.basicConfig()
logger = logging.getLogger("kalliope")

TTS_URL = "http://www.acapela-group.com/demo-tts/DemoHTML5Form_V2_fr.php"
TTS_CONTENT_TYPE = "audio/mpeg"
TTS_TIMEOUT_SEC = 30


class Acapela(TTSModule):
    def __init__(self, **kwargs):
        super(Acapela, self).__init__(**kwargs)

    def say(self, words):

        self.generate_and_play(words, self._generate_audio_file)

    def _generate_audio_file(self):

        # Prepare payload
        payload = self.get_payload()

        # Get the mp3 URL from the page
        url = Acapela.get_audio_link(TTS_URL, payload)

        # getting the mp3
        r = requests.get(url, params=payload, stream=True, timeout=TTS_TIMEOUT_SEC)
        content_type = r.headers['Content-Type']

        logger.debug("Acapela : Trying to get url: %s response code: %s and content-type: %s",
                     r.url,
                     r.status_code,
                     content_type)
        # Verify the response status code and the response content type
        if r.status_code != requests.codes.ok or content_type != TTS_CONTENT_TYPE:
            raise FailToLoadSoundFile("Acapela : Fail while trying to remotely access the audio file")

        # OK we get the audio we can write the sound file
        FileManager.write_in_file(self.file_path, r.content)

    def get_payload(self):
        return {
            "MyLanguages": self.language,
            "MySelectedVoice": self.voice,
            "MyTextForTTS": self.words,
            "t": "1",
            "SendToVaaS": ""
        }

    @staticmethod
    def get_audio_link(url, payload, timeout_expected=TTS_TIMEOUT_SEC):
        r = requests.post(url, payload, timeout=timeout_expected)
        data = r.content
        return re.search("(?P<url>https?://[^\s]+).mp3", data).group(0)
