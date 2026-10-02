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

## Open issues
- Network: add commons.wikimedia.org, upload.wikimedia.org, gandhiheritageportal.org, mkgandhi.org to Network access (403 from proxy now).
- Enable texttospeech.googleapis.com (optional: Chirp 3 HD voices; custom voice cloning needs the voice owner's consent and an allowlist, so not for Gandhi). Command: gcloud services enable texttospeech.googleapis.com --project=navuramedia-509306
- GPU quota could not be read (service account lacks quota view). Check in console: Quotas, filter Cloud Run L4.

## Next
1. Lip-sync and voice-clone spike on a GPU (needs GPU quota).
2. Gandhi reference-photo test once hosts are allowed.
3. Build pipeline v0 for Gandhi.
