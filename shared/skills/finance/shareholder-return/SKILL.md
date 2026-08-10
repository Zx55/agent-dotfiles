---
name: shareholder-return
description: Use Dayu as the mandatory system of record to research and calculate listed-company shareholder-return table rows and portfolio totals, including annual-report EPS, cash dividends, cancelled or retired buybacks, net share-count change, tax-adjusted dividend yield, comprehensive return, and current-position equivalents. Use when the user asks to analyze, fill, update, or audit this shareholder-return table for one or more public stocks. Always invoke the sibling dayu skill for company evidence before calculating.
---

# Shareholder Return

Build an auditable shareholder-return table from Dayu research and deterministic calculations. Keep company evidence, user-specific holdings, calculation logic, and spreadsheet presentation separate.

## Mandatory Dayu Boundary

Treat Dayu as the only research path for listed-company facts.

- Read and follow `../dayu/SKILL.md` and `../dayu/references/routing.md` completely before invoking Dayu.
- Invoke `dayu-cli prompt --base ~/.dayu/workspace --ticker --label --output` for every company.
- Ask Dayu to obtain annual reports, exchange filings, dividend announcements, buyback details, share counts, tax evidence, and official exchange rates.
- Do not run a parallel host-side financial search or replace missing filing data with an aggregator.
- Ask a narrower Dayu follow-up under the same label when evidence or a required field is missing.
- Mark a field `N/A` when Dayu cannot support it. Do not guess.

Use the host only to collect the user's cost basis, holding quantity, holding channel, and requested output format, then validate arithmetic from Dayu-supported inputs.

## Required References

Read:

- `references/methodology.md` for definitions, formulas, strict buyback rules, tax handling, and portfolio aggregation.
- `references/dayu-prompt.md` before preparing a Dayu request or extracting its machine-readable calculation block.

## Workflow

### 1. Establish the row identity

Resolve:

- company name, ticker, exchange, and share class;
- target fiscal year, defaulting to the latest complete annual report requested by the user;
- current RMB cost per share and current holding quantity, when portfolio calculations are requested;
- holding channel and investor type, because dividend taxation depends on both.

Ask only when a missing choice materially changes the result. Continue with `N/A` for optional holding fields.

### 2. Run Dayu research

List existing labels first:

```bash
dayu-cli conv --base ~/.dayu/workspace list
```

Reuse a label only for the same company and shareholder-return thread. Use a stable label such as `<ticker>-shareholder-return` and a unique persistent output file for every prompt.

Prepare the request from `references/dayu-prompt.md`, then run:

```bash
dayu-cli prompt \
  --base ~/.dayu/workspace \
  --ticker <TICKER> \
  --label <LABEL> \
  --output "<OUTPUT_MD>" \
  "<PREPARED_REQUEST>"
```

For multiple companies, keep one label and one evidence artifact per ticker. Do not combine unrelated companies into one Dayu conversation.

### 3. Audit the Dayu artifact

Wait for `Markdown 已保存: <path>`, then read the complete artifact. Require evidence for:

- annual-report basic EPS;
- cash dividends paid during the target fiscal year;
- strict cancelled or retired buyback amounts for the target year and two preceding years;
- year-end outstanding common shares for those years;
- prior-year and current-year ending shares for net share-count change;
- official target-year-end FX rates;
- company domicile, holding channel, and dividend withholding treatment.

Require Dayu to distinguish direct disclosures from estimates. Reject authorization amounts, employee-plan repurchases, and year-end treasury stock from strict cancelled-buyback value.

If any required distinction is unresolved, prompt Dayu again under the same label. Do not resolve it by host-side web research.

### 4. Run deterministic calculation

Extract the JSON calculation block defined in `references/dayu-prompt.md` into a local input file. Run:

```bash
python3 scripts/calculate_row.py --input <INPUT_JSON> --output <OUTPUT_JSON>
```

Prefer the project Python when present. On the user's local Mac without a project environment, use `~/.local/share/agent-dotfiles/python/bin/python`.

Compare the script result with Dayu's human-readable row. Treat any material mismatch as an unresolved discrepancy. Correct the structured inputs or ask Dayu a follow-up rather than changing a result silently.

### 5. Present or write the table

Return:

- the completed table row or rows;
- three to five concise, evidence-grounded takeaways;
- the Dayu Markdown artifact link for each company;
- explicit `≈`, `N/A`, tax scenarios, or source limitations where applicable.

If the user provides a spreadsheet, invoke the appropriate spreadsheet skill only after the row values have passed this workflow. Preserve the user's layout and formulas unless asked to redesign them.

## Non-Negotiable Calculation Rules

- Use annual-report basic EPS, not TTM, unless the user explicitly requests another period.
- Keep gross dividend per share as the company fact. Apply the dividend coefficient only to actual cash and after-tax return fields.
- Use target-year actual strict cancelled buyback in actual comprehensive return.
- Use the three-year average only as a stability indicator or explicitly labeled smoothed estimate.
- Do not tax-discount buyback value.
- Use cost-weighted aggregation: `SUM(position return) / SUM(position cost)`. Never average security return percentages directly.
- Describe buyback return as an economic allocation, not cash received by the investor.
- Preserve the actual RMB historical cost basis. Do not retranslate it at year-end FX.

## Tax Uncertainty

Never hard-code one dividend coefficient for all Hong Kong, US, or Stock Connect securities. Require Dayu to research the legal domicile, share class, holding chain, investor type, treaty eligibility, withholding base, and practical settlement evidence.

When the official withholding base or practical treatment is unresolved:

1. provide a recommended working coefficient supported by Dayu;
2. provide a conservative scenario;
3. tell the user how to validate the coefficient from the broker dividend statement;
4. keep the uncertainty visible in the output.

## Failure Handling

- If Dayu is unavailable or unconfigured, stop and use the `dayu-installation` skill. Do not substitute another research workflow.
- If a filing is unavailable, report the missing evidence and leave affected values `N/A`.
- If strict buyback cost must be estimated, retain the approximation marker in every downstream result.
- If the user's cost currency is unclear, calculate company metrics but do not finalize cost-based return rates.
