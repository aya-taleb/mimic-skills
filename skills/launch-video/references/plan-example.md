# launch-video: a full plan example

A 37 second vertical promo for a made-up app called Tally. Every figure comes from the
business file, and it says so.

```json
{
  "title": "Tally launch",
  "format": "vertical",
  "brand": {"bg": "#1B2433", "ink": "#FFFFFF", "accent": "#E8664F", "font": "Inter"},
  "voice": "founder",
  "cta": "Try Tally free at tallyapp.io",
  "claims": [{"text": "212 teams", "source": "founder/context.md, Stage line"}],
  "scenes": [
    {"id": "hook", "seconds": 4,
     "vo": "Your standup runs long because nobody says they're stuck.",
     "on_screen": "Nobody says they're stuck",
     "visual": "screen: Tally board with a red stuck tag",
     "asset": "media/launch/assets/board.png", "motion": "slow push in"},
    {"id": "problem", "seconds": 6,
     "vo": "So the meeting turns into a status read-out, and the real blocker waits a day.",
     "on_screen": "Blockers wait a day",
     "visual": "founder to camera, desk, daylight"},
    {"id": "product", "seconds": 8,
     "vo": "Tally puts one question first: where are you stuck? The answer goes on a board everyone sees.",
     "on_screen": "Ask: where are you stuck?",
     "visual": "screen recording of adding a stuck tag",
     "asset": "media/launch/assets/board.png", "motion": "slow push in"},
    {"id": "proof", "seconds": 6,
     "vo": "212 teams have used it in our beta.",
     "on_screen": "212 teams in beta",
     "visual": "plain stat card, no client names"},
    {"id": "how", "seconds": 8,
     "vo": "Set it up in five minutes, invite your team, and run your next standup from the board.",
     "on_screen": "Set up in minutes",
     "visual": "three quick screen cuts: sign up, invite, board"},
    {"id": "cta", "seconds": 5,
     "vo": "Try Tally free at tallyapp dot io.",
     "on_screen": "tallyapp.io",
     "visual": "logo end card"}
  ]
}
```

Notes on the choices:

- "Five minutes" in the `how` scene is a spoken number. The check catches digits; spelled-out
  numbers are on you. If the founder has not timed the setup, write "a few minutes" instead.
- The proof scene uses the one real figure the business file allows. Revenue and client names
  are off-limits there, so they stay out.
- Voiceover pace: the longest line is 17 words over 8 seconds, about 2.1 words a second.
  Comfortable.

## Formats

| format | size | for |
| --- | --- | --- |
| vertical | 1080 x 1920 | Reels, Shorts, TikTok, Stories |
| wide | 1920 x 1080 | YouTube, website hero, LinkedIn video |
| square | 1080 x 1080 | feed posts |

## HyperFrames facts this skill relies on

Checked against HyperFrames 0.8.191 and its README on 2026-10-23
(github.com/heygen-com/hyperframes, Apache 2.0):

- Install: `npm install -g hyperframes`, or run any command with `npx hyperframes`. Needs
  Node.js 22 or newer and FFmpeg. `npx hyperframes doctor` checks the machine.
- `npx hyperframes lint` validates the HTML. `npx hyperframes preview` opens a live preview.
  `npx hyperframes render -o launch.mp4` renders to MP4 locally.
- A project is an `index.html` whose root has `data-composition-id`, `data-start`,
  `data-duration`, `data-width` and `data-height`. Scenes are separate files mounted with
  `data-composition-src`, each wrapped in `<template>`, with matching host id, scene id and
  timeline key. Animation uses a paused GSAP timeline registered on `window.__timelines`.
- Local rendering is free. Hosted features (cloud render, HeyGen voices and avatars) may cost
  money.

The generated project from the example above passed `hyperframes lint` with 0 errors and
0 warnings, and rendered to a 37 second 1080 x 1920 MP4, during this repo's build.
