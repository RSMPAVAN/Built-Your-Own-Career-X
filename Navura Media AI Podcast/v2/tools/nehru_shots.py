import sys,os,shutil; sys.path.insert(0,"v2")
import kit_v2 as K
from kit_v2 import *
NG=Image.open("v2/nehru/nehru_guest.png").convert("RGB")
K.refs["gandhi"]=jpg(NG.crop((1600,120,2300,820)).resize((700,700)),700)   # the guest reference slot now holds the Nehru face
K.INTRO=("Image 1 is the approved empty Navura Media podcast studio (match its room, table, chairs, desk microphones, mugs and window exactly). Image 2 is a frontal face reference of the host Nithya, image 3 shows Nithya in her teal and gold saree. Image 4 is a reference of the AI-reimagined guest Jawaharlal Nehru in a white achkan with a red rose and a white cap. "
 "Keep both faces identical to the references: Nithya in the teal and gold saree, the guest in his white achkan, red rose and white cap, and the room consistent with image 1. ")
IM=[K.refs["plate"],K.refs["n_face"],K.refs["n_saree"],K.refs["gandhi"]]; QR=[K.refs["plate"],K.refs["n_face"],K.refs["gandhi"]]
SH={"N1_two_shot":"Create the wide two-shot: Nithya in the left chair and the guest in the right chair, facing each other across the walnut table, relaxed and engaged, hands resting on the table, same camera angle and composition as the studio image, desk microphones in front of each.",
    "N2_guest_medium":"Create a tight medium shot of the guest seated in the right chair, framed from the waist up, facing slightly left toward the host, kindly attentive expression, hands resting on the table, his desk microphone beside his face; Nithya and the left side of the table are NOT in frame; sunset window softly blurred behind.",
    "N3_ots_to_guest":"Create an over-the-shoulder shot from behind Nithya: the back of her head, dark hair and shoulder in the soft-focus left foreground, her desk microphone slightly visible, the guest facing the camera in sharp focus with his desk microphone in front of him, listening with a gentle smile, window behind him.",
    "N4_ots_to_nithya":"Create an over-the-shoulder shot from behind the guest: the back of his white cap and white achkan shoulder in the soft-focus right foreground, Nithya facing the camera in sharp focus with her desk microphone in front of her, speaking warmly, window behind her."}
for k,b in SH.items():
    r=produce(k,b,IM,QR,tries=3)
    if os.path.exists(f"v2/kit/{k}.jpg"): shutil.move(f"v2/kit/{k}.jpg",f"v2/nehru_kit/{k}.jpg")
    print(k,r,flush=True)
