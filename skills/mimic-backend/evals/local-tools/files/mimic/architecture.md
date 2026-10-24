# Architecture: Noon Wheels

Type: local business. No custom code at launch.

## Tools
| layer | pick | why |
| --- | --- | --- |
| website and order page | a site builder with forms | founder has no developer |
| orders | an online ordering form that writes to a shared sheet | changes until 9am |
| payments | Stripe payment links and subscriptions | hold a spot now, charge 7 days before the first order |
| email | an email list tool with consent | weekly menu |
| partner sign-up | a form | trucks apply |

## Build order
Slice 1 The order path: weekly plan page, pick meals, change by 9am, confirmation message. done when: a test order placed Monday 8:30am for that day shows on the truck's list at 9am.
Slice 2 Partner trucks: sign-up form, weekly schedule, prep list per truck.
Slice 3 Payments: founding spot hold, charge 7 days before the first order, cancel online.
