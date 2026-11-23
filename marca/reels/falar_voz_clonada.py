import sys, os, warnings; warnings.filterwarnings("ignore")
os.environ["COQUI_TOS_AGREED"]="1"
from TTS.api import TTS
m=os.path.expanduser("~/.local/share/tts/tts_models--multilingual--multi-dataset--your_tts")
tts=TTS(model_path=m+"/model_file.pth", config_path=m+"/config.json")
frases=[l.strip() for l in open("frases.txt") if l.strip()]
for i,f in enumerate(frases,1):
    tts.tts_to_file(text=f, speaker_wav="ref.wav", language="pt-br", file_path=f"f{i}.wav")
    print("ok",i)
