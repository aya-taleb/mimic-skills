# Where market numbers come from

Use free, public, checkable sources first. Every number in `founder/market.md` names the
source and the year of the data, with a link. Facts here were checked on 2026-10-23;
check the links again before relying on them.

## Counting buyers (for bottom-up)

| buyer | source | what it gives | watch out |
| --- | --- | --- | --- |
| Businesses with staff, by industry and place | US Census County Business Patterns, [FAQ](https://www.census.gov/programs-surveys/cbp/about/faqs.html), tables on data.census.gov, also an API | Number of establishments, employment and payroll by NAICS industry, for nation, state, county, metro and ZIP. Also counts by employee size class. | Published 14 to 18 months after the reference year. Leaves out government, farms, private households and some others. Counts locations, not companies. |
| One-person businesses | US Census Nonemployer Statistics (on data.census.gov) | Businesses with no paid staff, by industry and place, with receipts | Mostly sole owners. Good for freelancers and trades. |
| Households and what they spend | BLS Consumer Expenditure Survey, [overview](https://www.bls.gov/opub/hom/cex/pdf/cex.pdf), tables at bls.gov/cex | Average yearly spend per "consumer unit" (roughly a household) by category, for the nation, regions and some metro areas | Averages hide spread. Use as a sanity check on price, not as proof people will pay you. |
| People by age, income, place | US Census American Community Survey (data.census.gov) | Population and households by age, income and more, down to small areas | Survey estimates have margins of error. Note them. |
| App users or online buyers | The company's own published numbers, public filings, app store pages | Install counts and ratings, user counts stated by the company | A company's claims are claims. Say whose number it is. |

Outside the US, use the national statistics office (Statistics Canada, ONS in the UK,
Eurostat for the EU, DOS in Jordan) and say which one.

## Top-down figures (for a sanity check)

- Industry association reports and government reports are the best free top-down sources.
- Paid analyst reports (and the press releases quoting them) often state a market size.
  Quote the figure, the firm, the year and the link to the page you read. Don't round up.
  These figures vary a lot between firms. If two disagree, show both.
- Never use a figure you can't link to. If the only source is "a report says", it goes in
  as `{{number, source needed}}`.

## Prices

- Competitors' public price pages, menus, quotes the founder has received.
- Say the date you read the page. Prices change.

## Trends

- Search for news and reports from the last 12 to 24 months, and say the date of each.
- Google Trends (trends.google.com) shows relative search interest over time. It is an
  index from 0 to 100, not a count of people. Say so if you cite it.
- Job posts, funding news and new competitors are signals, not proof of demand.

## When you can't browse

Say so. Write the method and the inputs needed, with `{{number}}` placeholders and the
exact source to look up for each one. A sizing with honest blanks is more useful than one
with made-up numbers that look finished.
