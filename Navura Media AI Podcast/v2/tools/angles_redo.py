import sys,os,shutil; sys.path.insert(0,"v2")
import kit_v2 as K
from kit_v2 import *
HERO=Image.open("v2/kit/H0_hero_two_shot.jpg"); K.refs["hero"]=jpg(HERO,1280)
G=HERO.crop((1900,430,2650,1150)).resize((700,672)); K.refs["gandhi"]=jpg(G,700)
CLEAN=" The window glass is perfectly clean: no light streaks, no diagonal lines, no reflections of lights, no glare lines."
EMPTY_INTRO=("Image 1 is the approved empty Navura Media podcast studio. Keep the room, walnut table, black office chairs, NM desk microphones on short stands on the table, NM mugs, acoustic panels, amber and teal lights and the big window with the sunset, cable-stayed bridge and river consistent with it. ")
PEOPLE_INTRO=("Image 1 is the approved empty Navura Media podcast studio. Image 2 is a frontal face reference of the host Nithya, image 3 shows Nithya in her teal and gold saree, image 4 is a reference of the elderly guest Mahatma Gandhi. Keep both faces identical to the references, Nithya in the teal and gold saree, Gandhi in a white shawl and dhoti, and the room consistent with image 1. ")
JOBS=[
 ("A05_side_on","e",EMPTY_INTRO+"Camera placed at the middle of the LONG side of the table, at chair height, looking straight across at the opposite wall of the room: the view is exactly side-on to the table, so the table runs left to right across the whole frame and the two chairs with their desk microphones are at the far left and far right ends, facing each other. The big window is NOT behind them; instead show the acoustic panels and amber and teal strip lights along the long wall, with the window visible only at the very edge. No people."),
 ("A06_from_behind_chairs","e",EMPTY_INTRO+"Camera placed directly behind the right-hand chair, low, looking over the empty chair's back and the table toward the left chair and the big window; the back of the chair fills the right foreground, soft focus, the table and desk microphones beyond. No people."),
 ("A08_window_clean","e",EMPTY_INTRO+"Medium view of the big window at sunset with the cable-stayed bridge and river, with the table edge and one desk microphone softly out of focus in the foreground."+CLEAN+" No people."),
 ("B01_two_shot_low_left","p",PEOPLE_INTRO+"Camera low and close at the left end of the table near Nithya's chair, looking along the table: Nithya large in sharp focus in the left foreground, Gandhi smaller and farther away at the right end, both with their desk microphones in front of them, window behind. Dramatic low angle, strong perspective."),
 ("B02_two_shot_high","p",PEOPLE_INTRO+"Camera high up near the ceiling in the front corner looking steeply DOWN at the table from above and slightly to the side: Nithya and Gandhi seen from above, the walnut table surface prominent with mugs and desk microphones, the window behind them. Clear top-down perspective."),
 ("B03_side_profile","p",PEOPLE_INTRO+"Camera at the middle of the long side of the table, looking straight across: a pure side-on profile view, Nithya at the far left and Gandhi at the far right in profile facing each other across the table, desk microphones between them in front of each, acoustic panels and strip lights behind them.")]
def run(name,kind,brief):
    K.INTRO=EMPTY_INTRO if kind=="e" else PEOPLE_INTRO
    imgs=[K.refs["plate"]] if kind=="e" else [K.refs["plate"],K.refs["n_face"],K.refs["n_saree"],K.refs["gandhi"]]
    qr=[K.refs["plate"]] if kind=="e" else [K.refs["plate"],K.refs["n_face"],K.refs["gandhi"]]
    r=produce(name,brief,imgs,qr,tries=3)
    if os.path.exists(f"v2/kit/{name}.jpg"): shutil.move(f"v2/kit/{name}.jpg",f"v2/angles2/{name}.jpg")
    return name,r
if __name__=="__main__":
    for j in JOBS: print(run(*j),flush=True)
