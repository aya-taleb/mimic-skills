# Architecture: Tidyslot

Date: 2026-10-21
Type: app or website
Demand test: passed (founder/validate.md)

## Constraints
| | answer |
| --- | --- |
| who builds it | the founder, TypeScript and React, one Next.js app shipped |
| platform | web first |
| budget per month at launch | about $50 |
| deadline | {{not set}} |
| sensitive data | guest names and emails, phone numbers for SMS |
| scale in six months | 50 teams |

## Stack
| layer | pick | why it fits | runner-up |
| --- | --- | --- | --- |
| frontend and backend | Next.js (App Router) | founder knows it | Remix |
| database | Postgres on Supabase | managed, row level security | Neon |
| auth | Supabase Auth | same project as the database | Auth.js |
| payments | Stripe Checkout and Customer Portal | hosted, flat price | Paddle |
| email | Resend | small, clear API | Postmark |
| SMS | Twilio | official API, US numbers | Vonage |
| hosting | Vercel | Next.js host | Render |
| jobs | Vercel Cron calling a route | reminders every 5 minutes | Inngest |

## Data
Booking: unique (host_id, start_at) where status = 'confirmed'. Reminders: channel email or sms, send_at, sent_at. Team: one Stripe subscription per team.

## Build order
Slice 1 Core loop: guest books a slot (S07 to S10). done when: a booking on the public page shows on the host's list, and a second booking for the same slot is refused.
Slice 2 Host setup (S01 to S05). Slice 3 Reschedule and cancel (S11). Slice 4 Reminders, email and SMS (fix 2). Slice 5 Team and flat billing (S12, S13, fixes 1 and 4).

## Outside services
| service | used for | webhooks |
| --- | --- | --- |
| Google Calendar API, Microsoft Graph | busy times, add events | push notifications |
| Stripe | flat team plan | checkout.session.completed, customer.subscription.updated, customer.subscription.deleted, invoice.upcoming |
| Resend | email | |
| Twilio | SMS | status callback |
