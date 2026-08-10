# Shareholder-return methodology

## Contents

1. Measurement objective
2. Time and currency conventions
3. Table formulas
4. Strict buyback test
5. Tax treatment
6. Stability and portfolio checks
7. Source hierarchy

## 1. Measurement objective

Measure how much shareholder value a listed company returned during one complete fiscal year through cash dividends and effective share cancellation, using the investor's current RMB cost basis as the denominator.

Separate:

- cash received from dividends;
- economic allocation from cancelled buybacks;
- historical actual return from a smoothed run-rate estimate.

## 2. Time and currency conventions

- Use one complete fiscal year for EPS, paid dividends, buybacks, and share-count change.
- Use basic EPS from the audited annual report. Put diluted EPS in a note when useful.
- Count ordinary cash dividends actually paid during the fiscal year. Do not count stock dividends.
- Translate foreign company metrics with the official CNY midpoint on the last available day of the target fiscal year.
- Use the same target-year-end FX rate for all three historical buyback-per-share observations so the average is comparable.
- Keep the investor's actual historical RMB cost unchanged. If cost is supplied in another currency, prefer actual settlement cost or transaction-date conversion rather than year-end restatement.

## 3. Table formulas

Define:

- `C`: current RMB cost per share.
- `N`: current holding shares.
- `E`: annual-report basic EPS in source currency.
- `D`: gross cash dividend per share paid during the fiscal year in source currency.
- `FX_E`, `FX_D`: applicable target-year-end CNY exchange rates.
- `RB_y`: strict cancelled-buyback amount for year `y`.
- `SO_y`: common shares outstanding at year-end `y`, excluding treasury stock.
- `FX_RB_y`: target-year-end CNY exchange rate for the buyback currency.
- `k`: dividend cash-receipt coefficient from 0 to 1.

Calculate:

```text
EPS_RMB = E × FX_E
Dividend_RMB = D × FX_D
BuybackPerShare_y_RMB = RB_y ÷ SO_y × FX_RB_y
BuybackPerShare_3Y_RMB = average(BuybackPerShare_y_RMB for target year and prior two years)
NetShareChange = (SO_target − SO_prior) ÷ SO_prior
AfterTaxDividendYield = Dividend_RMB × k ÷ C
ActualComprehensiveReturn = (Dividend_RMB × k + BuybackPerShare_target_RMB) ÷ C
TotalCost = C × N
PositionCashDividend = Dividend_RMB × k × N
PositionEquivalentReturn = (Dividend_RMB × k + BuybackPerShare_target_RMB) × N
```

Map the row as follows:

| Column | Value |
|---|---|
| 标的 | Company name and ticker |
| 每股成本 | `C` |
| EPS（年报） | `EPS_RMB` |
| 每股分红 | `Dividend_RMB`, gross |
| 每股回购注销 | target-year `BuybackPerShare_RMB` |
| 每股回购注销（近三年平均） | `BuybackPerShare_3Y_RMB` |
| 净股本变动率 | `NetShareChange` |
| 股息回报率 | `AfterTaxDividendYield` when the table measures actual return |
| 综合回报率 | `ActualComprehensiveReturn` |
| 持股数 | `N` |
| 总成本 | `TotalCost` |
| 按当前持股折算派息 | `PositionCashDividend` |
| 按当前持股折算回报 | `PositionEquivalentReturn` |

The position-equivalent return is a current-position normalization. It is not proof that the investor held the same number of shares throughout the historical year.

## 4. Strict buyback test

Count a buyback only when all applicable conditions are supported:

- the company executed the purchase rather than merely authorizing it;
- it was an open-market ordinary-share repurchase;
- the shares were cancelled or retired, or a binding cancellation treatment is evidenced;
- the amount attributable to the cancelled shares is disclosed or can be reasonably estimated;
- it was not performed for an employee plan, RSU, option, restricted-stock award, or employee tax withholding.

Exclude:

- unused authorization;
- shares remaining as treasury stock at year-end;
- shares reserved or reused for employee incentives;
- old treasury shares merely reclassified or cancelled in the target year without target-year cash expenditure;
- amounts that cannot be separated reliably from excluded purposes.

Use this evidence order:

1. Direct annual-report disclosure of repurchased-and-retired amount and shares.
2. Direct retired-share count multiplied by supported actual average purchase price, marked `≈`.
3. Full treasury-stock roll-forward covering opening balance, additions, retirements, reissues, and employee transfers, marked `≈`.
4. `N/A` when the distinction cannot be supported.

Never use `total repurchase amount − ending treasury balance` without reconciling opening treasury stock and all intervening movements.

## 5. Tax treatment

Keep `Dividend_RMB` gross for company comparability. Apply `k` only to actual cash and after-tax returns.

Research `k` by:

- company legal domicile;
- listed share class and registration chain;
- investor identity;
- holding channel;
- source-country withholding;
- treaty access and documentation;
- mainland withholding and foreign-tax-credit mechanics;
- broker or custodian settlement practice.

Do not apply dividend tax to buyback value. When tax mechanics are not confirmed, output recommended, conservative, and broker-verification scenarios rather than false precision.

## 6. Stability and portfolio checks

Use target-year actual cancelled buyback for actual comprehensive return. Use the three-year average only to judge repeatability.

Optionally calculate a clearly labeled smoothed estimate:

```text
SmoothedComprehensiveReturn = (Dividend_RMB × k + BuybackPerShare_3Y_RMB) ÷ C
```

Check:

- target-year buyback versus three-year average;
- buyback amount versus net share-count change;
- dilution from employee awards, issuance, and option exercise;
- whether a large buyback left outstanding shares roughly unchanged;
- whether estimates materially affect the return ranking.

Aggregate a portfolio by cost:

```text
PortfolioDividendYield = SUM(PositionCashDividend) ÷ SUM(TotalCost)
PortfolioComprehensiveReturn = SUM(PositionEquivalentReturn) ÷ SUM(TotalCost)
```

Do not average security-level percentages directly.

## 7. Source hierarchy

Prefer:

1. audited annual report, 10-K, 20-F, and equity notes;
2. exchange buyback returns, capital-change filings, and dividend announcements;
3. official central-bank or FX authority rates;
4. broker dividend statements for actual tax and cash verification.

Use aggregators only as discovery aids. Preserve direct versus estimated status in the final table.
