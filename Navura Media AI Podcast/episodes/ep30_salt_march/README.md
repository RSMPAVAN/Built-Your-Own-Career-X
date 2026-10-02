# Episode 30-second cut: The Salt March (v1)

File: ep30_v1.mp4 (1280x720, 24 fps, about 40 s). AI-reimagined conversation; Gandhi's image and voice are AI-generated.

## Process used (tools/episode30)
1. tournament.py: OpenAI (gpt-5.1) and Google (gemini-3.8-flash) each write host-line candidates in four angles (info, hook, plain, arc). Gandhi's two lines are fixed verbatim quotes inserted by code.
   Hard rules in code (word caps per line, no digits, 'AI-reimagined' disclosure, at least two concrete facts). Both vendors fact-check every candidate; hard fail only if both flag a line, otherwise a penalty. Two judges (one per vendor) score blind and shuffled; final = mean minus flag penalty.
   Winner: google:hook (script_selection.json has the ranking, scores and notes).
2. final_script.py: assigns reference stills and derives clip lengths from word counts.
3. vprompts.py: OpenAI (gpt-5.1, with the reference stills attached) writes Veo-format prompts; code checks the exact line is quoted.
4. clips2.py: Veo 3.1 Fast generates each Nithya line with speech; every clip is transcribed and must match the script. Cost-capped.
5. Gandhi lines: Veo (Fast, Standard, Lite) filtered every Gandhi clip (Vertex usage-guideline filter, support code 29310472), so Gandhi speaks with an AI voice (Gemini TTS, Charon) over his still with a slow push-in and a reaction shot of Nithya, labelled on screen.
6. build_final.py: FFmpeg edit with captions, source lower-thirds, AI tag, intro and outro cards, loudness normalization.

## Sources
- Facts: Salt March, 12 March 1930 to 6 April 1930, 78 volunteers, 240 miles, 24 days; Salt Act 1882. https://en.wikipedia.org/wiki/Salt_March , https://www.britannica.com/event/Salt-March
- Quote 2: Gandhi, letter to Lord Irwin, 2 March 1930 (CWMG vol. 43).
- Quote 1: attributed to Gandhi, Salt March period; primary citation still to confirm.

## Known issues
- 'Dandi' is spoken by Veo; two transcribers heard 'Dandi', one heard 'Dundee'. Listen and confirm.
- Gandhi has no lip movement (voice over still). Needs the lip-sync step.
- Length is about 40 s with title and end cards; speech alone is about 33 s.
- Nithya's and Gandhi's voices are different systems (Veo vs Gemini TTS).
