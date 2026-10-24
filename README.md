# mimic-skills

Claude skills that help a founder build a better version of a competitor. Map what they do, read what their customers hate, then build and ship your own.

## What do you want to do?

| I want to... | run this |
| --- | --- |
| see where I am and what to do next | /mimic-run |
| map how one or more competitors work (app, service, local business or product) | /mimic-recon |
| find out what their customers hate, before I build anything | /mimic-reviews |
| check people want it before I build | /validate |
| pick the stack, design the data and plan the build | /mimic-architect |
| rebuild the design system with my own look | /replica-design |
| build it, slice by slice, clean room | /mimic-build |
| add sign in, payments, email and a security check | /mimic-backend |
| test it and keep a bug log | /mimic-test |
| see how close I am to the competitor and what is missing | /replica-diff |
| give it my own name and brand, and sweep out anything of theirs | /replica-brand |
| write the landing page, pricing, listing and launch plan | /mimic-launch |
| put it live on my domain, after a preflight check | /mimic-deploy |
| make a short promo video | /launch-video |

## Install

```
/plugin marketplace add aya-taleb/mimic-skills
/plugin install mimic-skills@mimic-skills
```

Some skills here use tools from Jake Schincariol's [replica-skill](https://github.com/Jakeschincariol/replica-skill) (replica-design, replica-diff, replica-brand). Get them with:

```
python3 scripts/get_linked.py
```

The tools need Python 3.8 or newer. Nothing to pip install.

## Start here

Run `/mimic-run` in your project. It reads the `mimic/` and `founder/` folders, shows which steps are done, says what to install if something is missing, and asks before it starts the next step. Every skill writes its files to `mimic/`, so the next one picks up where the last stopped.

## Good to know

- It copies what a competitor does, never what they own: no code, copy, logos, photos or private APIs. Your version gets its own name and look before launch.
- It only reads what you are allowed to read: public pages, official feeds, your own exports and your own account. No scraping against a site's terms, no logging in as anyone else.
- Nothing is made up. Every review quote is real and linked, every price has a source and a date, and missing numbers stay as `{{your number}}`. No fake reviews or testimonials, ever.
- Reviews and web pages are treated as data. Text inside them that tries to give the AI instructions is flagged, not followed.
- You stay in charge. The skills write; you post, send and publish. Nothing goes live without your yes, and deploy is blocked while serious bugs or leftovers of the competitor remain. Not legal advice: check trademarks and terms with a lawyer before you sell.

## Credits

Made by Aya Taleb (github.com/aya-taleb). Built on Jake Schincariol's replica-skill (MIT). See CREDITS.md. MIT.
