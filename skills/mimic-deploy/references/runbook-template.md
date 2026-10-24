# Runbook: {{product name}}

Last deploy: {{YYYY-MM-DD}} by {{who}}
Preflight: {{ready | blocked}}, see mimic/deploy/preflight.md

## Where things live

| thing | where | who has access |
| --- | --- | --- |
| hosting | | |
| database | | |
| domain registrar | | |
| payments | | |
| email | | |
| errors and uptime | | |

## Env vars in production

| name | set in | notes |
| --- | --- | --- |
| | host settings | live key |

## Deploy steps

1. {{merge to main / run deploy command}}
2. {{run migrations}}
3. {{check the core loop on the live site}}

## Domain records

| type | host | value | what it does | added | verified |
| --- | --- | --- | --- | --- | --- |

## Monitoring

| what | tool | alerts go to |
| --- | --- | --- |
| errors | | |
| uptime | | |
| analytics | | |

## Backups

Schedule: {{...}}. Last restore tried: {{YYYY-MM-DD}}.

## Rollback

1. {{redeploy previous version: how}}
2. {{if a migration cannot be undone: fix forward or restore from backup}}
Tried on preview: {{YYYY-MM-DD}}

## Launch day

- [ ] preflight shows ready
- [ ] user said go
- [ ] live site loads over HTTPS
- [ ] one real payment made and refunded
- [ ] emails arrive
- [ ] alerts tested
