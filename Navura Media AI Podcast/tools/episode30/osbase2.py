from common import *
import base64,json,io
from PIL import Image
KIT=f"{REPO}/assets/gandhi_kit"
def b64img(name,w=768):
    im=Image.open(f"{KIT}/{name}.jpg").convert("RGB"); im=im.resize((w,int(im.height*w/im.width))); b=io.BytesIO(); im.save(b,"JPEG",quality=85); return base64.b64encode(b.getvalue()).decode()
FRAMES=["S02_nithya_close","S01_nithya_medium","S04_gandhi_close","S03_gandhi_medium"]
FACTS={
 "F1":"The Salt March began 12 March 1930 at Sabarmati Ashram, Ahmedabad. Gandhi set out with 78 volunteers and walked about 240 miles in 24 days to Dandi, on the coast.",
 "F2":"The Salt Act of 1882 gave the British a monopoly on salt and taxed it; making salt was illegal for Indians.",
 "F3":"The marchers reached Dandi on 5 April; on the morning of 6 April 1930 Gandhi picked up natural salt from the shore, breaking the law."}
QUOTES={
 "Q1":"Next to air and water, salt is perhaps the greatest necessity of life.",
 "Q2":"I regard this tax to be the most iniquitous of all from the poor man's standpoint."}
SYSTEM=("You write short podcast scripts and Veo 3.1 image-to-video prompts for 'Navura Media', an AI-reimagined history podcast. Host: Nithya (warm, curious). Guest: the historical figure, AI-reimagined and labelled as such.\n"
"HARD RULES: (1) Use ONLY the facts and quotes supplied. Invent nothing: no anecdotes, no dates, no numbers beyond the facts. (2) The guest's lines must be EXACT verbatim quotes from the QUOTES list, unchanged. (3) Total spoken words 52 to 66 so the finished video is about 30 seconds. "
"(4) Include a short spoken AI disclosure by the host in the opening. (5) Write numbers and years as words so speech is unambiguous (e.g. 'nineteen thirty', 'seventy-eight'). Phonetic hints for tricky names go in the Veo prompt only, never in the spoken text. "
"(6) Do NOT choose clip lengths; the pipeline derives them from your word counts. Keep every line at most 16 words, host lines 6 to 13 words, and make the total 52 to 66 words. (7) Each Veo prompt must follow this structure: Shot, Subject and image consistency, Action, Dialogue (exact line in quotes plus voice direction), Camera, Lighting and style, Audio, Negatives. "
"Reference the attached still by its id so the clip starts from that frame and keeps the faces identical.\n"
"Return ONLY JSON: {\"title\":str,\"lines\":[{\"id\":\"L0\",\"who\":\"Nithya|Gandhi\",\"text\":str,\"seconds\":4|6|8,\"frame\":one of the frame ids,\"source\":[ids],\"veo_prompt\":str}],\"total_words\":int,\"notes\":str}")
user=[{"type":"text","text":"FACTS:\n"+json.dumps(FACTS,indent=1)+"\n\nQUOTES (guest may say only these, verbatim):\n"+json.dumps(QUOTES,indent=1)+
 "\n\nEpisode: The Salt March, 1930. Structure: disclosure, question that sets the scene and asks why salt, guest answers with Q1, host adds the tax fact, guest answers with Q2, host closes with the march and Dandi. Frames attached in this order: "+", ".join(FRAMES)+". Use these frame ids in the 'frame' field."}]
for n in FRAMES:
    user.append({"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+b64img(n)}})
