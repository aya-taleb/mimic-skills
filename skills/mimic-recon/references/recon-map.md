# Recon map: {{business or app}} vs {{competitors}}

Type: {{app or website | service | local business | physical product}}
Scope: {{the slice being mapped}}
For: {{who the user's version is for}}
Date: {{YYYY-MM-DD}}

## Sources

| # | competitor | source | URL | date read | notes |
| --- | --- | --- | --- | --- | --- |
| 1 | | help center | | | |

## Core loop

{{one sentence: the thing customers pay for}}

## Side by side

| | {{competitor 1}} | {{competitor 2}} |
| --- | --- | --- |
| core loop | | |
| price of the common purchase | {{price, source #}} | |
| happy path length | {{n clicks or steps}} | |
| what it does best | | |

## Screens (apps) or customer steps (everything else)

| ID | screen or step | route, or where it happens | purpose | key parts | states or waits | competitor |
| --- | --- | --- | --- | --- | --- | --- |
| S01 or C01 | | | | | | |

## Flows

```
F01 {{goal}}
    S01 -> S02 -> S03     (or C01 -> C02 -> C03)
    happy path clicks or steps: {{n}}
    edge: {{cases}}
```

## Components (apps)

| component | variants | states | used on |
| --- | --- | --- | --- |

## Offer and operations (services, local, physical)

| item | detail | source |
| --- | --- | --- |
| tiers and prices | | |
| hours and area served | | |
| how orders come in | | |
| delivery or fulfilment | | |
| tools visible from outside | | |

## Inferred data model or records

```
{{Entity}}  {{fields}}
            evidence: {{screen or step IDs, help articles}}
            confidence: high | medium | guess
```

Relationships: {{...}}

## Feature matrix

See `features.csv`. Must: {{n}}, should: {{n}}, could: {{n}}, skip: {{n}}.

## Out of scope (cannot or should not be copied)

- {{licensed content, the network, partner deals, a location, permits...}}

## What the rebrand must avoid

Names, domains, colours, taglines and signature looks of each competitor. replica-brand
puts these in `mimic/brand.json` so the sweep can find leftovers.

## Size

Screens or steps {{n}}, flows {{n}}, entities {{n}}. Hard parts: {{list}}. Size: {{S|M|L|XL}}.
