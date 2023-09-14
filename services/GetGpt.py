import os
import requests
import json
import uuid
from Crypto.Cipher import AES

url = 'https://chat.getgpt.world/'
supports_stream = True
needs_auth = False


def _create_completion(messages: list, **kwargs):
    def encrypt(e):
        t = os.urandom(8).hex().encode('utf-8')
        n = os.urandom(8).hex().encode('utf-8')
        r = e.encode('utf-8')
        cipher = AES.new(t, AES.MODE_CBC, n)
        ciphertext = cipher.encrypt(pad_data(r))
        return ciphertext.hex() + t.decode('utf-8') + n.decode('utf-8')

    def pad_data(data: bytes) -> bytes:
        block_size = AES.block_size
        padding_size = block_size - len(data) % block_size
        padding = bytes([padding_size] * padding_size)
        return data + padding

    headers = {
        'Content-Type': 'application/json',
        'Referer': 'https://chat.getgpt.world/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

    data = json.dumps({
        'messages': messages,
        'frequency_penalty': kwargs.get('frequency_penalty', 0),
        'max_tokens': kwargs.get('max_tokens', 4000),
        'model': 'gpt-3.5-turbo',
        'presence_penalty': kwargs.get('presence_penalty', 0),
        'temperature': kwargs.get('temperature', 1),
        'top_p': kwargs.get('top_p', 1),
        'stream': True,
        'uuid': str(uuid.uuid4())
    })

    res = requests.post('https://chat.getgpt.world/api/chat/stream',
                        headers=headers, json={'signature': encrypt(data)}, stream=True)

    for line in res.iter_lines():
        print(line)
        if b'content' in line:
            line_json = json.loads(line.decode('utf-8').split('data: ')[1])
            print(line_json)
            yield (line_json['choices'][0]['delta']['content'])


sd = _create_completion([{'role': 'user', 'content': "Кто ты воин"}])
for el in sd:
    print(el)
