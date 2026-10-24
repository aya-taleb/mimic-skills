# Recon map: Noon Wheels vs Lunchbox Club, Curbside Eats

Type: local business (weekly lunch plan, food truck partners)
Scope: weekly office lunch plan in downtown Denver and LoDo
For: office workers and office managers, teams of 10 to 200
Date: 2026-10-12

## Sources
| # | competitor | source | URL | date read |
| --- | --- | --- | --- | --- |
| 1 | Lunchbox Club | website | https://lunchboxclub.example | 2026-10-11 |
| 2 | Lunchbox Club | Google Maps | https://maps.google.example/lunchboxclub | 2026-10-11 |
| 3 | Curbside Eats | website | https://curbsideeats.example | 2026-10-11 |

## Core loop
An office worker picks the week's lunches and gets them at the office at lunchtime.

## Side by side
| | Lunchbox Club | Curbside Eats |
| --- | --- | --- |
| price | $13.50 a meal on 3 a week (#1) | $15 a meal, 20 meal minimum (#3) |
| order cutoff | Sunday 8pm for the week (#1) | 7 days ahead, request form (#3) |
| delivery | lobby drop 11:45 to 12:30 (#1) | truck at the building (#3) |
| cancel | email support (#1) | {{not public}} |

## Customer steps
| ID | step | where | customer does | business does | wait | competitor |
| --- | --- | --- | --- | --- | --- | --- |
| C01 | hears about it | office, word of mouth | | | | both |
| C02 | picks a plan | website or app | chooses 3, 4 or 5 a week | | | Lunchbox |
| C03 | picks meals | website or app | picks from 6 dishes a day by Sunday 8pm | locks orders | until Monday | Lunchbox |
| C04 | pays | card, weekly on Monday | | charges | | Lunchbox |
| C05 | gets lunch | office lobby | collects bag | drops all orders | 11:45 to 12:30 | Lunchbox |
| C06 | books a truck | request form | sends date and headcount | confirms in 2 business days | 2 days | Curbside |
| C07 | queues at truck | street by the building | orders at the window | cooks | 25 min for 30 people (review c3) | Curbside |
| C08 | cancels | email | emails support | replies | up to 5 days (review r8) | Lunchbox |

## Flows
```
F01 Worker gets a week of lunches (Lunchbox Club)
    C02 -> C03 -> C04 -> C05
    happy path steps: 4, wait to first meal: up to 8 days
    edge: forgot the Sunday cutoff, late delivery, wrong order, rain
F02 Office manager books a team lunch (Curbside Eats)
    C06 -> C07
    edge: team under 20, truck cancels, rain
```

## Operations seen from outside
| item | detail | source |
| --- | --- | --- |
| hours | Mon to Fri 7am to 2pm | #2 |
| area | Downtown, LoDo, RiNo | #1 |
| kitchen | Five Points (photo) | #2 |
| partner trucks | 25, exclusive downtown partners | #3 |
| margins and volumes | {{not visible from outside}} | |

## Out of scope
- Curbside Eats' exclusive truck partners: their network.

## What the rebrand must avoid
Lunchbox Club, lunchboxclub.example, Curbside Eats, curbsideeats.example.

## Size
Steps 8, flows 2. Hard parts: partner truck supply, lunchtime delivery window, food safety permits. Size: M.
