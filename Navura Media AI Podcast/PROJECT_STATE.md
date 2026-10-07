# Navura Media AI Podcasting System: project state

Plan page (live, private): https://claude.ai/artifact/VnPHq43DYUs1hDyjZNksdv

## Decisions so far
- Host: Nithya (AI-imagined, no real-person resemblance). Studio: Navura studio image.
- Episode 1: Gandhi, Salt March (Dandi, 1930), 2 minutes, English. Gandhi-only pipeline first.
- Six stages: facts, script, voices, visuals, assembly, review/publish. Web dashboard on Cloud Run.
- Script written by OpenAI GPT, checked against sources by Gemini. Images: test OpenAI GPT Image vs Gemini image, keep the steadier one.
- Video: stills, Veo 3.1 Lite animation, GPU lip-sync, FFmpeg edit. Price check: Lite about $0.05/s, Standard about $0.40/s (third-party figures, verify).
- Every episode carries an on-screen and spoken AI disclosure. Human approval before publish.
- Ignore duplicate images w11.png (= w5.png) and w10.png (= w8.png).
- Images carry a Gemini sparkle in the bottom-right corner; crop or repaint before use.

## Google Cloud
- Project ID: navuramedia-509306, region us-central1.
- Service account: navura-pipeline@navuramedia-509306.iam.gserviceaccount.com
- Org policy iam.disableServiceAccountKeyCreation was switched off for this project so a key could be created.
- Delete the key once the app runs on Cloud Run (keyless).

## Credentials (API credentials in environment settings; never in git or chat)
- The environment uses the API credentials system. Keys are injected into requests to allowed hosts and are NOT visible as environment variables in the sandbox. Do not check env vars; test with direct HTTPS calls.
- Google Vertex: type "GCP access token (with Service Account...)", allowed website *.googleapis.com, scope https://www.googleapis.com/auth/cloud-platform.
- OpenAI: type Bearer, allowed website api.openai.com, header Authorization.
- Still allow in Network access: commons.wikimedia.org, upload.wikimedia.org, gandhiheritageportal.org, mkgandhi.org.
- SDKs that insist on local credentials need a placeholder key or plain REST calls.
- Loads in new sessions only.

## Verified 2 Oct 2026 (new session)
- Google credential works: authenticated calls to project navuramedia-509306 succeed. APIs enabled: Vertex AI, Cloud Run, Cloud Build, Artifact Registry, Firestore, Storage, Secret Manager, Scheduler, Tasks.
- Vertex models seen: gemini-3.8-flash, gemini-3.7-flash, gemini-3.1-pro-preview, gemini-3.1-flash-image, gemini-3-pro-image, gemini-2.5-flash-tts, gemini-2.5-pro-tts. Veo in catalog: veo-3.1-generate-001, veo-3.1-fast-generate-001, veo-3.1-lite-generate-001, veo-3.0 and veo-2.0 variants. (Catalog presence, not yet a test generation.)
- OpenAI credential works (133 models): gpt-5.1, gpt-5, gpt-image-2, gpt-image-1.5, gpt-4o-transcribe, gpt-4o-mini-tts, sora-2, sora-2-pro.
- Not yet verified: GPU quota (L4), real-person image/video policy, voice clone tools.

## Quick test results (2 Oct 2026; outputs in tests/2026-10-02/)
1. Multi-angle still from studio + Nithya refs: PASS on both. Gemini (gemini-3.1-flash-image, location global only) keeps the studio layout. OpenAI gpt-image-2 edit (quality low, 1536x1024, 13 s) gives a more cinematic frame. Face and saree held in both.
2. Gandhi still (text prompt only, no reference photo): Gemini flash-image and pro-image both generate it. OpenAI gpt-image-2 REJECTS it (safety system, HTTP 400). Use Gemini for Gandhi. Reference-photo version untested (Wikimedia hosts blocked by network policy in that session).
3. Two-speaker voice: PASS. gemini-2.5-flash-tts, 2.5-pro-tts, 3.1-flash-tts-preview (global) work with two named speakers. gemini-3.8-flash-tts reads the style instruction aloud, so it needs a different prompt format. OpenAI gpt-4o-transcribe-diarize matched the script and split the two speakers, so the transcript QA step works. Voice quality (does Gandhi sound right) needs a human listen.
4. Gandhi voice clone: NOT TESTED. No GPU here, archive hosts blocked. OpenAI has no custom-voices endpoint on this key (404). Google instant custom voice needs the Text-to-Speech API enabled (not in the enabled list) and is allowlist-gated. Plan: open-weight cloning on a GPU job, or designed voice.
5. Animation: PASS for the animation half. veo-3.1-lite-generate-001 image-to-video, 4 s, 720p, no audio, ~43 s, face and studio stable, natural gestures. Lip-sync half NOT TESTED (needs a GPU and a lip-sync model).

6. Animated styles (Gemini flash-image, two-shot of Nithya and Gandhi in the studio): PASS in all three: flat 2D, 3D feature-film look, ink and watercolor. OpenAI refuses the stylized Gandhi too (HTTP 400), so animation does not get around OpenAI. Style choice pending user decision. Samples 6a, 6b, 6c.

7. User liked 6b (3D) but found it too anime; wants simpler and more realistic. Tried semi-realistic variants (7a painting, 7b realistic render, 7c simple clean). 7a and 7b are good; 7c reads more illustrated. Leaning 7a. Style choice pending user decision.

8. User chose 7b (realistic render), asked for clearer and neater. Result: 8_two_shot_clean_2K.png (gemini-3.1-flash-image, global, imageSize 2K gives 2752x1536). Method: pass 7b as the look reference plus studio and Nithya refs with a "sharper, neater, fix mic arms" prompt, then a second targeted edit to remove window light streaks. Gemini 3 pro-image ignored the 2K size (1376x768) and rebuilt the studio layout, so flash-image is the better base. This look is close to photoreal: AI disclosure is essential. Style status: locked to this look unless the user objects.

9. Gandhi shot set DONE (assets/gandhi_kit, 10 shots, 2752x1536 JPEG) plus hero shot 8. Generator and QA in tools/shot_kit (kit.py, common.py). Look guide in assets/look_guide.json. Nithya wardrobe available: teal saree (w1, w2), rust salwar (w3, w4), maroon saree (w5), maroon embroidered kurta (w7), grey blazer (w8, w9). Image quota: 429 when 4 parallel; use 2 with backoff. All 10 pass auto QA; S03 needed a tighter-framing prompt.

10. 10-second pilot DONE (episodes/pilot_10s/pilot_10s.mp4). Nithya 4 s on veo-3.1-fast, Gandhi 6 s on veo-3.1-generate (Standard), both with native speech from the dialogue in the prompt, joined and loudness-normalized with a burned-in AI tag. Transcripts match the script exactly. Veo Fast blocked the Gandhi clip (filter), Standard allowed it, Lite had a load error. Veo native speech costs about $0.40 per second on Standard, so a 2-minute episode this way is about $40 to $50: the cost plan still needs the Lite plus lip-sync route. Gandhi quote primary source still to confirm.

11. 30-second episode, in progress (episodes/ep30_salt_march, tools/episode30). User direction: OpenAI (gpt-5.1) writes the script and Veo-format prompts using the shot images as references; Gemini/Veo makes the video. Facts and the two verified guest quotes are fed in; guest lines must be verbatim; code derives clip lengths (4/6/8 s) from word counts and checks totals. gpt-5.1 cannot count words: needed a validate-and-reprompt loop and still overshot the word budget; script_openai_v3.json is the best draft (75 words, 38 clip seconds). Earlier hand-written draft (tools/episode30/script.py) had richer facts. Test clips from the hand-written draft cost about $4 (about 42 Veo Fast seconds at about $0.10/s; blocked clips are free). Veo observations: Gandhi clip filtered on both Fast and Standard in the second run although Standard passed in the pilot (flaky), 'Dandi' was spoken as 'Bandi' once, Veo speech pace about 2.4 to 2.6 words per second. NO video spend until user approves the script. CPU lip-sync route chosen over GPU for now (user decision); not yet tested.

12. 30-second cut v1 DONE (episodes/ep30_salt_march/ep30_v1.mp4, about 40 s). Script chosen by a two-vendor tournament (tools/episode30/tournament.py): OpenAI and Gemini 3.8 Flash write, both fact-check, blind judges from both vendors; winner google:hook. OpenAI writes Veo prompts with stills attached. Nithya clips from Veo 3.1 Fast (about $2.8 including the Dandi retry), all transcript-verified. Veo (Fast, Standard, Lite) filtered every Gandhi clip (support code 29310472), so Gandhi is an AI voice (Gemini 2.5 Pro TTS, Charon, retried until exact words) over stills with push-ins and Nithya reaction shots, labelled on screen. Dandi pronunciation hint 'DAHN-dee' fixed one retry; one transcriber still hears 'Dundee'. Estimated total Veo spend today about $7 to $8 (check Billing).

13. v2 rebuild (folder v2/): table-mic studio (no overhead boom arms), new two-shot and 9 shots, extra angles (assets/angles), OpenAI-written Veo prompts, clips. Nithya's four lines generated and verified (about $2.20). Gandhi's two lines blocked 12 of 12 by the Vertex usage filter (support code 29310472), retried with unmodified inputs only. Google also refuses prompts that ask to remove its star watermark. Options for Gandhi on camera: (a) open-weight image-to-video plus audio-driven lip-sync on a GPU (needs L4 quota; no platform guardrails, user's responsibility, label stays), (b) ask Google via the feedback link in the block message, (c) archival footage and stills with Nithya on camera. Decision pending with user.

14. fal.ai test (2 Oct 2026): credential 'fal' works (Authorization: Key; hosts fal.run, queue.fal.run, fal.media). Endpoint fal-ai/wan/v2.2-14b/speech-to-video (required: prompt, image_url, audio_url; num_frames multiple of 4 and at most 120; fps at most 60; resolution 480p/580p/720p; steps at most 40; guidance at most 10). Gandhi 6 s clip at 720p, 40 steps, 120 frames at 20 fps COMPLETED (took roughly 25 minutes). Request id 01a0fcff-9c6e-7c62-b235-d7729702f808, result URL https://v3b.fal.media/files/b/0aacc6cf/aB00rE1pYDYFTB_WCENSY_eWdaI3dO.mp4 (1.0 MB). The sandbox could not download it: proxy 403 for v3b.fal.media. NEXT SESSION: add *.fal.media to Network access and to the fal credential's allowed websites, then GET the response_url and run tools/ten_assemble.py (expects v2/ten/gandhi_raw.mp4 and v2/ten/nithya.mp4; Nithya clip was Veo Standard 4 s, saved only in the old session scratch, regenerate if missing, about $1.60). Safety checker left on. Two empty probe requests accidentally queued earlier failed validation, no charge.

15. Product direction (7 Oct 2026): SaaS with two pipelines on one engine: Calendar (brand visibility, our own channel) and Intake (revenue, customer brief and files and consented talent). Podcast format fixed: AI host Nithya plus a guest, both on camera, speech and lips together. Guest classes: A customer talent, B fictional or owned characters, C mythological or religious, D deceased historical, E living without consent (not supported). Veo allowlist route for person generation found on Google developer forums; forum post drafted in v2/docs/3_veo_allowlist_forum_post.md (project number 702066814369). Tests on Veo 3.1 Fast (about $0.40 each, transcripts exact): Goddess Parvati guest PASS (assets/typec), Nehru guest PASS (assets/nehru_test; the face is generic, recognisable by costume, not a close likeness). Gandhi still blocked (celebrity filter, code 29310472). fal: Kling avatar laggy, Seedance/Wan/Kling native audio acceptable individually, lip-sync combination judged poor by user; fal not used further. Budget: INR 2000 to 3000 for tests. Pipeline code in v2/pipeline (fal-based, now deprioritised); Veo-based router still to build.

16. PARKED by user (7 Oct 2026). Last result: Children's Day episode, Nithya plus Nehru, 19 s, both speaking on Veo (v2/episodes/nehru_childrens_day). Nehru's first quote line blocked 8 of 8 tries; second line passed on Standard only. Spend that episode about $4.20. TO RESUME: (1) user posts the Veo allowlist request (v2/docs/3_veo_allowlist_forum_post.md) and decides budget; (2) build the cloud service: calendar pipeline plus intake pipeline on one engine, provider router (Veo first, fal fallback, archival hybrid), progress page, one approval step, cost cap; (3) Dussehra goddess episode as the next real production. Nothing is running or spending. fal balance about 3 USD; Google credit separate.

## Open issues
- Network: add commons.wikimedia.org, upload.wikimedia.org, gandhiheritageportal.org, mkgandhi.org to Network access (403 from proxy now).
- Enable texttospeech.googleapis.com (optional: Chirp 3 HD voices; custom voice cloning needs the voice owner's consent and an allowlist, so not for Gandhi). Command: gcloud services enable texttospeech.googleapis.com --project=navuramedia-509306
- GPU quota: PROBED 2 Oct 2026. Creating a Cloud Run L4 service fails in us-central1 with and without zonal redundancy: "You do not have quota for using GPUs". Compute Engine API is also not enabled. User must request quota (g.co/cloudrun/gpu-quota): Quotas page, filter Cloud Run Admin API L4, us-central1, request 1. Account may also need to be upgraded from free trial. Until then no GPU lip-sync.

## Next
1. Lip-sync and voice-clone spike on a GPU (needs GPU quota).
2. Gandhi reference-photo test once hosts are allowed.
3. Build pipeline v0 for Gandhi.
