# Credits

## Jake Schincariol's replica-skill (MIT)

https://github.com/Jakeschincariol/replica-skill, commit 77c9436fb3d18c3d58169efb8caf4fe906b0dc51.

**Reworked here (text and code copied, then changed):**

| our skill | from | what we copied and changed |
| --- | --- | --- |
| mimic-recon | replica-recon | SKILL.md, recon-map.md, features.csv. Changed: several competitors at once, a path for services, local businesses and physical products, mimic/ folder |
| mimic-reviews | replica-entrepreneur | SKILL.md, reviews.py, themes.json. Changed: runs before the build, collect.py for official feeds and exports, reviews treated as untrusted data, a competitor column, pain-points.csv for lead-gen, themes-local.json |
| mimic-launch | replica-launch | SKILL.md, listing.py, listing.example.json. Changed: handoffs to biz-boost and the social plans, a local business path, Google Business Profile checks, a proof check |

**Linked, not copied:** replica-design, replica-diff and replica-brand. `scripts/get_linked.py` installs them from Jake's repo at the commit above. They stay his, under his license.

**Rewritten, ideas only:** mimic-architect, mimic-build, mimic-backend, mimic-test and mimic-deploy replace Jake's replica-architect, replica-build, replica-backend, replica-test and replica-deploy. They were written from our own job specs (in each skill's `references/job-spec.md`). Thank you, Jake, for the chain these follow and for the clean-room and no-fake-proof rules the whole pack keeps.

Jake's license, which covers the copied parts:

```
MIT License

Copyright (c) 2026 Jake Schincariol

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Thank-you lines (ideas only, nothing copied)

- The security checklist in mimic-backend follows the risk areas of the OWASP Top 10 (https://owasp.org/www-project-top-ten/).
- The no-fake-reviews rule points to the US FTC's rule on consumer reviews and testimonials (16 CFR Part 465).

## Synced skills

market-research and validate (entrepreneur-skills), competitors (biz-ready-skills) and launch-video (multimedia-skills) are Aya Taleb's own skills, copied in from their home repos. Their credits live in those repos.

## This repo

Everything else: Copyright (c) 2026 Aya Taleb, MIT. See LICENSE.
