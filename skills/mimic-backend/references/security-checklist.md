# Security checklist

Mark each item `pass` (and how you checked), `fail` (and the fix), or `not checked`
(and why). Based on the common web risks in the OWASP Top 10
(https://owasp.org/www-project-top-ten/). Not a security audit. For health, finance or
kids' data, get a professional review before launch.

## Access

- [ ] Every route that reads or writes a record checks that the signed-in user may do so
- [ ] Tested on purpose: user A cannot read or change user B's records by changing an id
- [ ] Admin pages need an admin role, checked on the server, not just hidden in the UI
- [ ] Two-factor sign-in on every admin account of every service (host, database,
      payments, email, domain registrar)

## Sign in and sessions

- [ ] Auth comes from a provider or a well known library
- [ ] Passwords hashed with argon2id or bcrypt (if the stack stores them)
- [ ] Session cookies are http-only, secure and same-site
- [ ] Password reset links expire and work once
- [ ] Sign-in and reset are rate limited

## Input and output

- [ ] All input is checked on the server (types, lengths, allowed values)
- [ ] Database queries use parameters or the ORM, never string building
- [ ] User content is escaped when shown (no raw HTML from users)
- [ ] File uploads: type and size limits, stored outside the web root or in object storage
- [ ] Forms that change things are protected against cross-site requests

## Secrets

- [ ] No keys, passwords or tokens in the code or git history (search the repo)
- [ ] `.env` is in `.gitignore`; `.env.example` has names only
- [ ] Production and test keys are separate

## Payments and webhooks

- [ ] Card data never reaches our server (hosted checkout or provider fields)
- [ ] Webhook signatures are verified with the provider's SDK
- [ ] Each webhook event is handled once (event id stored)
- [ ] Access is granted by the webhook, not by the success page

## Data

- [ ] Logs do not contain passwords, tokens, card data or full personal records
- [ ] Backups are on, and one restore has been tried
- [ ] A user can export and delete their data (or there is a written way to ask)
- [ ] A privacy policy says what is collected and why (mimic-deploy checks it is live)

## Running it

- [ ] HTTPS everywhere
- [ ] Error pages do not show stack traces in production
- [ ] Dependencies checked for known issues (`npm audit` or the stack's tool)
- [ ] Rate limits on public endpoints that send email or cost money
