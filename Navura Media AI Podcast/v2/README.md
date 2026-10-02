# Navura Media AI Podcast: v2

Everything for the second build lives in this folder.

- studio/: the new empty studio. Overhead boom-arm mics removed; one NM desk microphone on a short stand on the table in front of each seat.
- assets/kit/: Nithya and Gandhi look in the new studio: hero two-shot (H0), 9 shots (S01-S09) and the empty studio (S10). All passed an automatic check (face match, style, mic on the table, no overhead arm, no text).
- tools/: plate.py (studio), kit_v2.py and shots_v2.py (assets with QA), clips_v2.py (video clips).
- episodes/ep30_v2/: the 30-second episode.

Notes
- Google refuses edits that ask to remove its star watermark, so the studio plate was rebuilt from the clean empty API-made shot. API images carry no visible star.
- Image model: gemini-3.1-flash-image (location global, 2K). Run two at a time; it returns 429 when pushed.
