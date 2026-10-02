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

## Next
1. Run the five quick tests: multi-angle still, Gandhi still from public-domain photos, two-speaker voice clip, Gandhi voice clone, 10-second lip-sync clip. Report each result.
2. Check reference-photo network hosts (wikimedia, gandhiheritageportal).
3. Build pipeline v0 for Gandhi.
