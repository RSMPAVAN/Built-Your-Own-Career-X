import sys; sys.path.insert(0,"v2")
import kit_v2 as K
from kit_v2 import *
import shutil
HERO=Image.open("v2/kit/H0_hero_two_shot.jpg"); K.refs["hero"]=jpg(HERO,1280)
EMPTY_INTRO=("Image 1 is the approved empty Navura Media podcast studio and image 2 is the approved two-shot in the same studio. Keep the room, walnut table, black office chairs, NM desk microphones on short stands on the table, NM mugs, acoustic panels, amber and teal lights and the big window with the sunset, cable-stayed bridge and river exactly consistent with them. ")
PEOPLE_INTRO=K.INTRO
EMPTY={
 "A01_front_left_3q":"Create a three-quarter view of the EMPTY studio from low in the left front corner of the room, looking toward the right chair and the window; no people.",
 "A02_front_right_3q":"Create a three-quarter view of the EMPTY studio from low in the right front corner, looking toward the left chair and the window; no people.",
 "A03_high_wide":"Create a high-angle wide view of the EMPTY studio from near the ceiling in the front, looking down at the table with both chairs, both desk microphones and both mugs, the window ahead; no people.",
 "A04_table_level_to_window":"Create a low table-level view of the EMPTY studio looking along the surface of the walnut table toward the window, a desk microphone and an NM mug sharp in the foreground, sunset bridge softly blurred; no people.",
 "A05_side_profile":"Create a straight side-on wide view of the EMPTY studio, camera at the long side of the table at chair height, both chairs and both desk microphones visible facing each other, the acoustic panels and window beyond; no people.",
 "A06_behind_chairs":"Create a view of the EMPTY studio from behind the two chairs, looking over the backs of the empty chairs, the table and both desk microphones toward the big window at sunset; no people.",
 "A07_panel_detail":"Create a close detail of the acoustic panels with the glowing amber and teal edge lighting in the corner of the EMPTY studio, softly out of focus window in the background; no people.",
 "A08_window_reflection":"Create a medium view of the big window glass in the EMPTY studio at sunset with the bridge and river, a soft reflection of the room's amber lights on the glass; no people."}
PEOPLE={
 "B01_two_shot_low_left":"Create a two-shot from a lower camera on the left side of the room: Nithya in the left chair in sharp focus, Gandhi in the right chair behind-right, both talking naturally across the table with their desk microphones in front of them.",
 "B02_two_shot_high":"Create a two-shot from a higher camera angle looking slightly down at Nithya in the left chair and Gandhi in the right chair, both with their desk microphones in front of them, relaxed conversation.",
 "B03_side_profile_two_shot":"Create a straight side-on two-shot from the long side of the table: Nithya on the left and Gandhi on the right in profile facing each other, desk microphones between and in front of them, window behind.",
 "B04_tight_two_shot":"Create a tight two-shot cropped at chest level of both: Nithya on the left, Gandhi on the right, leaning slightly toward each other in friendly conversation, desk microphones low in the frame, window softly blurred behind."}
def run(name,brief,empty):
    K.INTRO=EMPTY_INTRO if empty else PEOPLE_INTRO
    imgs=[K.refs["plate"],K.refs["hero"]] if empty else [K.refs["plate"],K.refs["n_face"],K.refs["n_saree"],K.refs["gandhi"],K.refs["hero"]]
    qr=[K.refs["plate"]] if empty else [K.refs["plate"],K.refs["n_face"],K.refs["gandhi"]]
    ok_=produce(name,brief+(" No people anywhere in the frame." if empty else " Image 5 is the approved two-shot: match its look and mic style exactly."),imgs,qr)
    if os.path.exists(f"v2/kit/{name}.jpg"): shutil.move(f"v2/kit/{name}.jpg",f"v2/angles/{name}.jpg")
    return name,ok_
import os
jobs=[(k,v,True) for k,v in EMPTY.items()]+[(k,v,False) for k,v in PEOPLE.items()]
if __name__=="__main__":
    # people shots share module state (INTRO), so run sequentially in one worker; keep it simple and safe
    for j in jobs: print(run(*j),flush=True)
