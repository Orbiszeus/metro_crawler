import os
import random
import time
import urllib.request
import pydub
import speech_recognition
from selenium.webdriver.common.keys import Keys
from seleniumbase import BaseCase
from seleniumbase import SB

class RecaptchaSolver():
     
    def __init__(self, driver:SB):
        super().__init__() 
        self.driver = driver

    def solveCaptcha(self):
        try :   
          with SB() as sb: 
            self.driver.wait_for_element_present("@title=reCAPTCHA", timeout=3)
            iframe_inner = sb.get_element("@title=reCAPTCHA")
            sb.click(".rc-anchor-content")
            sb.wait_for_element_present("xpath://iframe[contains(@title, 'recaptcha')]", timeout=3)
            
            # Sometimes just clicking on the recaptcha is enough to solve it
            if self.isSolved():
                return
            
            # Get the new iframe
            iframe = sb.get_element("xpath://iframe[contains(@title, 'recaptcha')]")
            
            # Click on the audio button
            sb.click("#recaptcha-audio-button")
            time.sleep(0.3)
            
            # Get the audio source
            src = sb.get_attribute("#audio-source", "src")
            
            # Download the audio to the temp folder
            path_to_mp3 = os.path.normpath(os.path.join((os.getenv("TEMP") if os.name=="nt" else "/tmp/") + str(random.randrange(1,1000)) + ".mp3"))
            path_to_wav = os.path.normpath(os.path.join((os.getenv("TEMP") if os.name=="nt" else "/tmp/") + str(random.randrange(1,1000)) + ".wav"))
            
            urllib.request.urlretrieve(src, path_to_mp3)
            
            # Convert mp3 to wav
            sound = pydub.AudioSegment.from_mp3(path_to_mp3)
            sound.export(path_to_wav, format="wav")
            sample_audio = speech_recognition.AudioFile(path_to_wav)
            r = speech_recognition.Recognizer()
            with sample_audio as source:
                audio = r.record(source)
            
            # Recognize the audio
            key = r.recognize_google(audio)
            
            # Input the key
            sb.update_text("#audio-response", key.lower())
            time.sleep(0.1)
            
            # Submit the key
            sb.type("#audio-response", Keys.ENTER)
            time.sleep(0.4)
            
        except Exception as e:
                print(f"RECAPTCHA problem: {e}")
            # Check if the captcha is solved
                if self.isSolved():
                    return
                else:
                    raise Exception("Failed to solve the captcha")
    
    def isSolved(self):
        try:
            with SB() as sb:
                return "style" in sb.get_attribute(".recaptcha-checkbox-checkmark", "style")
        except:
            return False
