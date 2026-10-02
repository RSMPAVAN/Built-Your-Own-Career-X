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

## Secrets (environment variables, never in git or chat)
- GOOGLE_SERVICE_ACCOUNT_JSON
- OPENAI_API_KEY
- Added to the environment settings on 2 Oct 2026. Loads in new sessions only.

## Next
1. In a new session, confirm both variables exist and the network allows googleapis.com and api.openai.com.
2. Run the five quick tests: multi-angle still, Gandhi still from public-domain photos, two-speaker voice clip, Gandhi voice clone, 10-second lip-sync clip. Report each result.
3. Build pipeline v0 for Gandhi.
