# Backend: Tidyslot

## Security checklist
| item | result | how checked or why not |
| --- | --- | --- |
| access checks on every record | pass | e2e test: user A requests user B's booking id, gets 404 |
| webhook signatures verified | pass | replayed a tampered event, rejected |
| secrets only in env | pass | searched the repo for sk_ and key= |
| rate limits on booking and SMS routes | pass | 20 requests a minute per IP, tested with a loop |
| backups restore tried | not checked | Supabase daily backups on, no restore tried yet |
