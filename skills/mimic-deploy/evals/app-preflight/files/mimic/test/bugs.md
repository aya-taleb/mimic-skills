# Bugs: Tidyslot

| id | title | severity | status | flow | found | steps |
| --- | --- | --- | --- | --- | --- | --- |
| B001 | Second booking for a taken slot went through | S1 | verified | F01 | 2026-10-22 | 1. Open the booking page in two tabs 2. Pick 10:00 in both 3. Submit both |
| B002 | SMS reminder sent twice | S2 | verified | F01 | 2026-10-23 | 1. Book for tomorrow 2. Wait for the cron run 3. Two texts arrive |
| B003 | Day picker skips a row on small phones | S4 | open | F01 | 2026-10-23 | 1. Open the booking page at 360px wide |
