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

## Next
1. In a new session, test one small REST call to Vertex (list models in navuramedia-509306, us-central1) and one to OpenAI (list models) to confirm both credentials work.
2. Run the five quick tests: multi-angle still, Gandhi still from public-domain photos, two-speaker voice clip, Gandhi voice clone, 10-second lip-sync clip. Report each result.
3. Build pipeline v0 for Gandhi.
