# Post this on the Google AI Developers Forum (discuss.ai.google.dev, Gemini API / Vertex AI) or discuss.google.dev (Generative AI & Foundational Models)

Title:
Request allowlist access for Veo 3.1 person generation (image-to-video, adults, customer-supplied consented talent): project navuramedia-509306

Body:
- Project ID: navuramedia-509306
- Project number: 702066814369
- Region: us-central1
- Models: veo-3.1-generate-001, veo-3.1-fast-generate-001 (image-to-video and reference-to-video)
- Setting: personGeneration = allow_adult
- Billing: active billing account on this project [confirm before posting]
- Current block: image-to-video with customer-supplied photos returns support code 29310472 (celebrity category).

Use case:
We run a SaaS that produces short two-person podcast videos (an AI host and a guest). Customers such as film studios and brands supply their own talent photos, characters and logos and confirm in writing that they hold the rights and consent for every face supplied. We also use fictional and mythological characters.

Safeguards:
- A written consent record is stored for every face supplied; adults only.
- Every video is labelled AI-generated on screen and in the spoken opening; the platform's synthetic-content label is set.
- Scripts use customer-provided or cited sources; a human approves every episode before publishing.
- No political, impersonation or deceptive use. SynthID stays intact. We take down content on request.

We can share a sample, our consent form and our content policy on request.
