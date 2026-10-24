---
name: mimic-launch
description: >-
  Writes the launch for the better version you built: a landing page on the angle from the
  reviews, pricing set against competitors' public prices and their customers' billing
  complaints, the store or Google Business Profile listing checked against the rules and
  copycat limits, a launch plan, and handoff briefs for biz-boost (leads, cold emails,
  local outreach) and the LinkedIn and Instagram plans. No fake proof, ever. Use when the
  user says "landing page", "launch copy", "how much should I charge", "pricing page",
  "App Store listing", "Google Business Profile", "launch plan", "Product Hunt", "how do
  I get my first customers for this", or after /replica-brand.
---

> Based on replica-launch by Jake Schincariol (MIT). Changed by Aya Taleb: handoffs to biz-boost and the social plans, a local business path, and a proof check in the listing tool.

# mimic-launch

The fix is the reason this product exists. The launch says that fix plainly, to the
people who complained about it, without borrowing anything from the competitors.

## Reads and writes

Reads:

- `mimic/fixes.md` (the angle and the evidence) and `mimic/pain-points.csv`
- `mimic/brand.md` and `mimic/brand.json` (from replica-brand: name, voice, `avoid` list)
- `mimic/features.csv` (what is built), `mimic/recon.md` (competitor prices and sources)
- `founder/validate.md` (the demand test and its result)
- the business context (founder-context): who it serves, tone, proof the founder can use

Writes `mimic/launch/`: `landing.md`, `pricing.md`, `listing.json`, `plan.md`,
`handoff.md`.

Tool:

```bash
python3 scripts/listing.py mimic/launch/listing.json --proof mimic/launch/landing.md
```

Start `listing.json` from `references/listing.example.json`.

## The rules

- **No fake proof.** No invented testimonials, user counts, star ratings, press logos or
  "trusted by" rows. An empty proof section is better than a fake one. Real beta users or
  waitlist numbers, with permission and a source, are fine. Use only the proof listed in
  the business context or given by the user in this session. Anything else becomes
  `{{your number}}` or `{{real quote with permission}}`.
- **No reviewer quotes as testimonials.** Competitors' reviews are research. Paraphrase
  the pain; never quote a reviewer on the user's page or in an ad.
- **Competitors' names stay out** of the product name, listing, keywords and ads. Apple's
  guidelines (4.1 Copycats, 2.3.7 metadata) reject apps that copy another app's name or
  UI or stuff metadata with other apps' names, and it invites a takedown. A factual
  comparison page is a legal question for a lawyer in the user's country.
- **Drafts only.** This skill writes. The user posts, sends and publishes. Nothing is
  scheduled, posted or emailed for them.
- **Every price has a source.** Competitor prices carry the URL and the date read. Prices
  change, so the date matters. A price you could not see is `{{not public}}`.
- **Your own choices are marked as choices.** A price, trial length, tier or target you
  propose (not from the business context) is labelled "suggested" so the user decides.

## Step 0: check the inputs

If `mimic/brand.json` is missing, replica-brand has not run. It is a linked skill: if it
is not installed, tell the user to run `python3 scripts/get_linked.py` from the
mimic-skills folder. Launch copy under a placeholder name is wasted work, so ask before
going on without it.

If `founder/validate.md` exists, read its result. A failed test is worth saying out loud
before writing a launch.

## Step 1: landing page

`landing.md`, section by section, in the brand voice:

1. **Hero**: the angle as a headline (what it does, for whom), one line under it, one
   button. A screenshot or photo of the real product, not a mockup of the competitor's.
2. **The problem**: the top two "hate" themes from `fixes.md`, in plain words.
   Paraphrase. Say how it feels, not who said it.
3. **How it works**: three steps from the core flow.
4. **What is different**: each point tied to a fix in `fixes.md`. Lead with the fixes,
   not the parity features. Parity is the price of entry. Check `features.csv`: a fix
   whose `clone` is not `yes` is not built yet. Write it as planned, or mark the line
   `{{confirm this is built before launch}}`. Copy that promises a feature that does not
   exist is fake proof too.
5. **Pricing**: the table from step 2.
6. **Proof**: only real proof from the business context. Otherwise leave the section out
   and write "Add when you have it: first customer quotes with permission."
7. **FAQ**: the real objections, from reviews and the demand test.
8. **Final call to action.**

For a local business, add where and when (area served, hours, how to order) and a
founding offer if the business context has one.

Run the draft through the humanize skill if it is installed, and fix what it flags. If it
is not installed, check by hand: no em dashes, no stock AI phrases, short sentences.

## Step 2: pricing

`pricing.md`:

- Competitors' public prices and 2 or 3 alternatives in one table, with URL and date read.
- What reviewers said about price and billing, from `feedback.md`, with counts.
- The model: free plan or trial, per seat or flat, monthly and annual. For a local or
  service business: per order, bundle, subscription, minimum order, delivery fee.
- Three tiers at most. Name them by who they are for.
- Fix the billing complaints in the product: one-click cancel, clear renewal notice, no
  surprise per-seat jumps. Hand those to mimic-backend if they are not built.
- The products and prices to create in the payment provider. The user creates them.
- If the business context or the user already fixed a price or offer, keep it and say so.

Not financial advice. For tax on subscriptions or sales tax on food, say who to ask.

## Step 3: listing

Fill `listing.json` with the listings that apply: `app_store`, `google_play`,
`google_business` (any business with a place or a service area). Put every competitor's
name and company in `avoid`. Then:

```bash
python3 scripts/listing.py mimic/launch/listing.json --proof mimic/launch/landing.md
```

It checks App Store limits (name 30, subtitle 30, promotional text 170, keywords 100,
description 4000), Google Play's (title 30, short description 80, full 4000), and the
Google Business Profile description (750, no links, no promotions). It flags ranking and
price claims in short fields, emoji, wasted keyword characters, any name in `avoid`, and
proof claims in the listing and the landing page. Exit 1 on an error. Fix every error, and
for every proof warning either cut it or confirm it is real.

For apps also prepare: screenshots at the current required sizes (check App Store
Connect and Play Console at upload), privacy labels and data safety form, privacy policy
and support URLs, and review notes with a demo account.

## Step 4: launch plan

`plan.md`, dated, starting from what validate learned:

- **Before launch**: the waitlist or pre-orders from the demand test, analytics and error
  tracking live (mimic-deploy sets these up), the first 10 people to talk to by hand.
- **Launch week**: where the competitors' unhappy customers talk (the threads and
  communities from the review research, with links), a Product Hunt or Hacker News post
  that leads with the fix, for apps. For local: a soft opening, nearby offices or groups,
  the Google Business Profile live.
- **First 30 days**: one number to watch each week and the line that means it works.

## Step 5: handoffs

`handoff.md` gives each next skill what it needs, so the user does not retype it. Use
`references/handoff.md` as the template.

- **biz-boost-skills**: lead-gen reads `mimic/pain-points.csv` to shape the ideal customer
  (themes and counts, never reviewer names); lead-email for cold email drafts (CAN-SPAM:
  physical address and opt-out); local-outreach for local businesses; reach-plan for
  weekly volume.
- **linkedin-boost-skills** and **instagram-boost-skills**: linkedin-plan and
  instagram-plan get the angle, three post ideas from the top fixes, and the launch date.
- **launch-video** (multimedia): a 30 to 60 second brief from the hero and the three steps.

Say which of these are installed. Do not run them from here. Name them as the next step.

## Writing

Every file and reply is read by a busy founder. Plain words, sentences under 25 words, no
em dashes, no hype. Skip these words in everything you write:
delve, leverage, seamless, streamline, comprehensive, journey, unlock, elevate, empower, foster, robust, crucial, utilize, simple. <!-- allow-words -->
If the humanize skill is installed, run copy that a person will publish or send through it.

## Output

`mimic/launch/` complete, `listing.py` passing with no errors, then a short summary: the
headline, the price, which proof is real and which is a placeholder, and the next steps:
`/mimic-deploy` to go live, then the handoffs in `handoff.md`.
