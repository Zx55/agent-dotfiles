# Dayu request contract

## Contents

1. Prepared request template
2. Required evidence
3. Calculation JSON schema
4. Follow-up rules

## 1. Prepared request template

Adapt this template without adding unsupported company facts:

```text
Research <COMPANY> (<TICKER>) for the shareholder-return table for fiscal year <YEAR>.

Use annual reports and primary exchange or company disclosures. Produce an auditable Markdown report and a final machine-readable JSON block matching the supplied schema exactly.

Required conventions:
1. Use annual-report basic EPS, with diluted EPS as a note.
2. Sum ordinary cash dividends actually paid during the fiscal year.
3. For each of <YEAR-2>, <YEAR-1>, and <YEAR>, identify only open-market repurchases attributable to shares actually cancelled or retired. Exclude unused authorizations, year-end treasury stock, employee plans, RSUs, options, restricted-stock awards, and employee tax withholding.
4. Give each year's strict cancelled-buyback amount and year-end outstanding common shares. Mark reconstructed amounts as estimates and explain the reconciliation.
5. Calculate net share-count change from prior-year-end to current-year-end outstanding shares, excluding treasury stock.
6. Use the official <YEAR>-end CNY midpoint for each source currency. Use the same <YEAR>-end rate for all three buyback years.
7. Research the dividend cash-receipt coefficient for <INVESTOR_TYPE> holding through <HOLDING_CHANNEL>. Distinguish company domicile, share class, source withholding, treaty access, mainland withholding, tax-credit mechanics, and actual custodian practice. If the withholding base is not confirmed, provide recommended and conservative coefficients.
8. Do not treat buyback value as investor cash or apply dividend tax to it.
9. Cite every material raw input and distinguish direct disclosures from inference.

User inputs:
- Current RMB cost per share: <COST_OR_NULL>
- Current holding shares: <HOLDING_SHARES_OR_NULL>

Return the human-readable row and this JSON block as the final section.
```

## 2. Required evidence

Require the report to identify:

- exact annual-report or filing source and period;
- basic and diluted EPS;
- dividend dates and full-year paid total;
- repurchase amount, share count, retirement or cancellation status, and treasury treatment;
- employee-award and share-issuance effects;
- year-end outstanding shares;
- official FX source and date;
- tax authority, company, exchange, clearing, or custodian evidence;
- every estimate and unresolved uncertainty.

## 3. Calculation JSON schema

Require one fenced `json` block with this shape:

```json
{
  "security": "Company name (TICKER)",
  "primary_year": 2025,
  "cost_per_share_cny": 100.0,
  "holding_shares": 1000,
  "basic_eps": {
    "value": 2.5,
    "fx_to_cny": 7.0
  },
  "dividend_per_share": {
    "value": 1.0,
    "fx_to_cny": 7.0,
    "coefficient": 0.8
  },
  "buybacks": [
    {
      "year": 2023,
      "retired_amount": 100000000.0,
      "year_end_shares": 400000000.0,
      "fx_to_cny": 7.0,
      "estimated": false
    },
    {
      "year": 2024,
      "retired_amount": 120000000.0,
      "year_end_shares": 390000000.0,
      "fx_to_cny": 7.0,
      "estimated": false
    },
    {
      "year": 2025,
      "retired_amount": 150000000.0,
      "year_end_shares": 375000000.0,
      "fx_to_cny": 7.0,
      "estimated": true
    }
  ]
}
```

Rules:

- Use `null` for unavailable `cost_per_share_cny` or `holding_shares`.
- Do not use `null` for research fields required by the calculation. Follow up or return `N/A` outside the JSON when those fields cannot be supported.
- Keep all monetary inputs in their disclosed source currency and attach the target-year-end `fx_to_cny` conversion.
- Supply zero `retired_amount` when reliable evidence shows no strict cancelled buyback for a required year.
- Set `estimated` to `true` for reconstructed retired amounts.

## 4. Follow-up rules

Use the same Dayu label and a new output file when:

- the JSON block is absent or invalid;
- treasury and retired shares are not separated;
- employee-plan shares may be included;
- the target-year-end exchange rate is missing;
- tax treatment lacks practical holding-channel evidence;
- the human-readable row and JSON inputs conflict.

Ask only for the missing or conflicting fields. Do not restart research in a host-side path.
