
import base64
import os
import requests
import time
from xml.etree import ElementTree
from datetime import datetime
import vlc
#import gtk, glib
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class tts_tool():
    def __init__(self, name):
        self.key = os.environ['TTS_KEY']
        self.name = name
        self.token_url = 'https://francecentral.api.cognitive.microsoft.com/sts/v1.0/issuetoken'
        self.api_url =  'https://francecentral.tts.speech.microsoft.com/cognitiveservices/v1'
        self._token = None
        self._token_time = None
        
    def get_token(self):
        if self._token_time is None or  time.time() - self._token_time > 9*60:
            print("new tkoen")
            headers = {
                'Ocp-Apim-Subscription-Key': self.key
            }
            response = requests.post(self.token_url, headers=headers)
            if response.status_code == 200:
                self._token = str(response.text)
                self._token_time = time.time()
            else:
                print(response)
        return self._token
    
    def call_api(self, text):
        bearer =  "Bearer "+ str(self.get_token())
        headers = {
            'Authorization': bearer,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': self.name

        }
        xml_body = ElementTree.Element('speak', version='1.0')
        xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
        voice = ElementTree.SubElement(xml_body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
        voice.set('name', 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)')
        voice.text = text
        body = ElementTree.tostring(xml_body)

        response = requests.post(self.api_url, headers=headers, data=body)
        if response.status_code == 200:
            sound_file = 'sample-' + ''.join(e for e in text[0:10] if e.isalnum()) + '.wav'
            with open(sound_file, 'wb') as audio:
                audio.write(response.content)
                print("\nStatus code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")
            return sound_file 
        else:
            print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")

def play_sound(file_name):
    p = vlc.MediaPlayer(file_name)
    p.play()
    

     
tts = tts_tool('tts_tool')
clipboard = Gtk.Clipboard()
txt = ""
while True:
    new_txt = clipboard.wait_for_text()
    if new_txt != txt:
        txt = new_txt
        sound = tts.call_api(txt)
        play_sound(sound)
        print(txt)
    time.sleep(0.1)