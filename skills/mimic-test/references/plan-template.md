# Test plan: {{product name}}

Date: {{YYYY-MM-DD}}
Run where: {{local, staging URL}}
Services in test mode: {{payments, email, ...}}

## Summary

| | count |
| --- | --- |
| checks planned | |
| passed | |
| failed | |
| not run | |

Gate: {{passes | blocked by B00x}} (from `bugs.py --gate`)

## F01 {{flow name}}

Happy path:
1. {{step}}
2. {{step}}
   expect: {{what the user sees}}

| check | type | test | result |
| --- | --- | --- | --- |
| happy path | e2e | tests/e2e/f01.spec.ts "..." | not run |
| {{edge case}} | e2e or manual | | not run |

## Fixes

| fix (from fixes.md) | check that proves it | test | result |
| --- | --- | --- | --- |
| fix 1: {{name}} | | | not run |

## Money and trust

| check | test | result |
| --- | --- | --- |
| checkout with test card | | not run |
| webhook replay handled once | | not run |
| cancel from settings | | not run |
| emails arrive, links work | | not run |
| user A cannot read user B's records | | not run |

## How to run

```bash
{{commands}}
```
