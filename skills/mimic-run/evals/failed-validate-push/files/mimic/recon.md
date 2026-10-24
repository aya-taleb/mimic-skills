# Recon map: Tidyslot vs Slotbook, MeetMate

Type: app or website
Scope: booking links for small teams: availability, event types, public booking page, reminders, team scheduling, payments
For: small service teams of 2 to 10 people (clinics, studios, agencies)
Date: 2026-10-20

## Sources

| # | competitor | source | URL | date read |
| --- | --- | --- | --- | --- |
| 1 | Slotbook | help center | https://slotbook.example/help | 2026-10-20 |
| 2 | Slotbook | pricing | https://slotbook.example/pricing | 2026-10-20 |
| 3 | MeetMate | pricing | https://meetmate.example/pricing | 2026-10-20 |
| 4 | MeetMate | features | https://meetmate.example/features | 2026-10-20 |

## Core loop

A guest opens a host's booking link, picks a free time, and the meeting lands in both calendars.

## Side by side

| | Slotbook | MeetMate |
| --- | --- | --- |
| price for a team of 4 | $48/month billed yearly, Pro (#2) | $40/month, Starter (#3) |
| SMS reminders | Teams plan only (#1) | Business plan only (#3) |
| free plan | yes, 1 event type (#2) | no, 14 day trial (#3) |
| cancel | contact support (#2) | {{not public}} |

## Screens

| ID | screen | route | purpose | states seen | competitor |
| --- | --- | --- | --- | --- | --- |
| S01 | sign up | /signup | create account | empty, error | both |
| S02 | connect calendar | /onboarding/calendar | read busy times | empty, connected, error | both |
| S03 | availability | /availability | weekly hours, overrides | empty, filled | both |
| S04 | event types | /events | list event types | empty, filled | both |
| S05 | event type editor | /events/:id | name, length, location, buffers, questions | filled, error | both |
| S06 | bookings list | /bookings | upcoming and past | empty, filled | both |
| S07 | public booking page | /:user/:event | pick a day | no slots, filled, mobile | both |
| S08 | pick a time | /:user/:event?date= | slots in guest time zone | filled, slot taken | both |
| S09 | guest details | /:user/:event/details | name, email, questions | filled, error | both |
| S10 | confirmed | /:user/:event/confirmed | summary, add to calendar | filled | both |
| S11 | reschedule or cancel | /b/:token | guest changes booking | filled, too late | both |
| S12 | team settings | /team | members, round-robin | empty, filled | both |
| S13 | billing | /settings/billing | plan, seats, invoices | filled | both |

## Flows

```
F01 Guest books a meeting
    S07 -> S08 -> S09 -> S10
    happy path clicks: 4
    edge: no slots this week, guest in another time zone, slot taken while filling the form, double submit
F02 Host sets up
    S01 -> S02 -> S03 -> S05
    happy path clicks: 11
    edge: calendar connect denied, no hours set
F03 Guest reschedules or cancels
    email link -> S11 -> S08 -> S10
    edge: link expired, inside cancel window
F04 Team round-robin
    S12 -> S05 -> S07
    edge: member has no hours, all members busy
F05 Host pays and cancels plan
    S13
    edge: seat added mid-cycle, cancel
```

## Inferred data model

```
User         id, email, name, time_zone, team_id          evidence: S01, S03   confidence: high
Team         id, name, plan                               evidence: S12, #2    confidence: high
Calendar     id, user_id, provider, token                 evidence: S02        confidence: high
Availability id, user_id, weekday, start, end; overrides  evidence: S03, #1    confidence: high
EventType    id, owner_id, name, minutes, location, buffer_before, buffer_after, questions (json)   evidence: S05, #1   confidence: high
Booking      id, event_type_id, host_id, start_at, end_at, guest_name, guest_email, guest_time_zone, status, answers (json)   evidence: S09, S10   confidence: high
Reminder     id, booking_id, channel (email | sms), send_at, sent_at   evidence: #1   confidence: medium
```

## Out of scope

- Slotbook's app marketplace of 40+ partner apps: their partner network.

## What the rebrand must avoid

Slotbook, slotbook.example, MeetMate, meetmate.example.

## Size

Screens 13, flows 5, entities 7. Hard parts: two-way calendar sync, time zones, SMS delivery. Size: M.
