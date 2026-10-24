# Architecture: {{product name or working name}}

Date: {{YYYY-MM-DD}}
Type: {{app | service | local business | physical product}}
Demand test: {{passed | failed | not run}}, from founder/validate.md

## Constraints

| | answer |
| --- | --- |
| who builds it | |
| platform | |
| budget per month at launch | |
| deadline | |
| sensitive data | |
| scale in six months | |

## Stack or tools

| layer | pick | why it fits | runner-up |
| --- | --- | --- | --- |
| frontend | | | |
| backend | | | |
| database | | | |
| auth | | | |
| payments | | | |
| email | | | |
| hosting | | | |
| jobs | | | |
| errors and analytics | | | |

## Data

```
{{Entity}}
  {{field}}  {{type}}  {{rule}}
  from: {{screen or step IDs}}   confidence: {{high | medium | guess}}
```

Key constraint for the core loop: {{e.g. unique (host_id, start_at) where status = confirmed}}

Fields added for fixes:
- {{field}}: for {{fix from fixes.md}}

Access rules: {{who reads and writes what}}

## Routes or pages

| method and path | does | who | flow |
| --- | --- | --- | --- |

## Outside services

| service | used for | official API or SDK | webhooks | account the user creates |
| --- | --- | --- | --- | --- |

## Background jobs

| job | when | does |
| --- | --- | --- |

## Build order

```
Slice 1  {{name}}
         builds: {{screens or steps, tables}}
         done when: {{a check a person can run}}
```

## Monthly cost at launch

| service | plan | cost | source and date |
| --- | --- | --- | --- |
| | | {{check pricing page}} | |

## Risks

| risk | why | how to test it early |
| --- | --- | --- |
