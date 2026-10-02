import sys; sys.path.insert(0,"v2")
from kit_v2 import *
HERO=Image.open("v2/kit/H0_hero_two_shot.jpg")
G=HERO.crop((1900,430,2650,1150)).resize((700,672))
refs["gandhi"]=jpg(G,700); refs["hero"]=jpg(HERO,1280)
IMGS=[refs["plate"],refs["n_face"],refs["n_saree"],refs["gandhi"],refs["hero"]]
ANCH=" Image 5 is the approved two-shot: match its look, lighting and the mic style exactly. "
SHOTS={
 "S01_nithya_medium":"Create a medium shot of Nithya seated in the left chair, from across the table, slightly angled; she is mid-conversation, mouth slightly open as if speaking, one hand gesturing gently; her desk microphone is in front of her on the table, to the side of her face; sunset window behind. Only Nithya in frame.",
 "S02_nithya_close":"Create a close-up of Nithya from the chest up, facing slightly to her left toward her guest, warm attentive expression, soft smile; her desk microphone is visible low in the frame in front of her, below her chin, not covering her mouth; sunset window softly blurred behind. Only Nithya in frame.",
 "S03_gandhi_medium":"Create a tight medium shot of Gandhi seated in the right chair: framed from the waist up, he fills the center-right of the frame, camera at eye level across the table, so the empty left side of the table and Nithya are NOT in frame; he wears his round wire-rimmed glasses, gentle smile, hands resting on the table; his desk microphone is in front of him on the table, to the side of his face; sunset window softly blurred behind. Only Gandhi in frame.",
 "S04_gandhi_close":"Create a close-up of Gandhi from the chest up, facing slightly to his right toward Nithya, round wire-rimmed glasses, calm attentive expression, soft smile; his desk microphone is visible low in the frame in front of him, below his chin, not covering his mouth; sunset window softly blurred behind. Only Gandhi in frame.",
 "S05_ots_to_gandhi":"Create an over-the-shoulder shot from behind Nithya: the back of her head, dark hair and shoulder in the soft-focus left foreground, her desk microphone slightly visible, Gandhi facing the camera in sharp focus with his desk microphone in front of him, listening with a gentle smile, window behind him.",
 "S06_ots_to_nithya":"Create an over-the-shoulder shot from behind Gandhi: the back of his bald head and white shawl in the soft-focus right foreground, Nithya facing the camera in sharp focus with her desk microphone in front of her, speaking warmly, window behind her.",
 "S07_insert_mug":"Create a close-up insert of an NM logo mug on the polished wooden table, a desk microphone stand softly blurred beside it, shallow depth of field, sunset window blurred behind. No people.",
 "S08_insert_mic":"Create a close-up insert of an NM logo microphone on its short desk stand standing on the walnut table, shallow depth of field, sunset window with the bridge softly blurred behind. No people.",
 "S09_cutaway_window":"Create a wide cutaway of the studio window showing the sunset sky, the cable-stayed bridge and the river, with the edge of the wooden table, one desk microphone and the top of a chair in the foreground. No people."}
def one(k):
    return k,produce(k,SHOTS[k]+ANCH,IMGS,[refs["plate"],refs["n_face"],refs["gandhi"]])
if __name__=="__main__":
    keys=sys.argv[1:] or list(SHOTS)
    with cf.ThreadPoolExecutor(2) as ex:
        for f in [ex.submit(one,k) for k in keys]: print(f.result())
