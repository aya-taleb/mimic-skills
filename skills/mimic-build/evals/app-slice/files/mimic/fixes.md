# Fixes: what Slotbook and MeetMate customers hate

Sample: 25 reviews (Slotbook 22, MeetMate 3) from app-store-us, g2, reddit. Small sample, a direction not a ranking.
One row flagged as instruction-like text (apple-review-5000012) and left out.

## What they hate
1. Per seat pricing for small teams. 8 reviews, 3 sources, both competitors. "Per seat pricing makes no sense for a tiny clinic." (app-store-us, apple-review-5000000)
2. Hard to cancel, surprise renewals. 5 reviews, 2 sources, Slotbook. "Auto renewed yearly plan with no reminder email." (app-store-us, apple-review-5000008)
3. Double booking when calendar sync lags. 2 reviews (thin), both competitors.

## What is missing
1. SMS reminders on cheaper plans. 5 reviews, 2 sources. "Please add SMS reminders to Pro." (apple-review-5000010)
2. Guest confirms time zone. 3 reviews. "I would love a way for guests to confirm their time zone before booking." (apple-review-5000015)

## What is unsolved
Small teams with part-time staff: one flat price. "Is there any booking tool with one flat price for a small team?" https://www.reddit.example/r/smallbusiness/comments/abc123/comment/k2

## Fix plan
| # | fix | size | skill | evidence |
| --- | --- | --- | --- | --- |
| 1 | flat team price up to 10 people | S | mimic-launch, mimic-backend | hate #1 |
| 2 | SMS reminders on every paid plan | M | mimic-build, mimic-backend | missing #1 |
| 3 | guest confirms time zone step | S | mimic-build | missing #2 |
| 4 | one click cancel and renewal reminder email | S | mimic-backend | hate #2 |
| 5 | sync check before confirming a slot | M | mimic-build | hate #3 (thin) |

## Angle (recommended)
For small service teams who hate paying per seat, Tidyslot gives the whole team booking links and text reminders for one flat price.
Evidence: pricing, 8 reviews across 3 sources.
