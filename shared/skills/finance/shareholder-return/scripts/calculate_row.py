#!/usr/bin/env python3
"""Calculate one shareholder-return table row from Dayu-supported JSON inputs."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


class InputError(ValueError):
    """Raised when an input cannot support the standardized calculation."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate a standardized shareholder-return table row."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input JSON path, or '-' to read from stdin.",
    )
    parser.add_argument(
        "--output",
        help="Optional output JSON path. Defaults to stdout.",
    )
    return parser.parse_args()


def read_payload(path_value: str) -> dict[str, Any]:
    if path_value == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(path_value).read_text(encoding="utf-8")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise InputError("top-level JSON value must be an object")
    return value


def require_mapping(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise InputError(f"{key} must be an object")
    return value


def require_number(
    parent: dict[str, Any],
    key: str,
    *,
    positive: bool = False,
    nonnegative: bool = False,
) -> float:
    value = parent.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{key} must be a number")
    number = float(value)
    if not math.isfinite(number):
        raise InputError(f"{key} must be finite")
    if positive and number <= 0:
        raise InputError(f"{key} must be greater than zero")
    if nonnegative and number < 0:
        raise InputError(f"{key} must be nonnegative")
    return number


def optional_number(
    parent: dict[str, Any], key: str, *, positive: bool = False
) -> float | None:
    if parent.get(key) is None:
        return None
    return require_number(parent, key, positive=positive)


def require_integer(parent: dict[str, Any], key: str) -> int:
    value = parent.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise InputError(f"{key} must be an integer")
    return value


def rounded(value: float | None, digits: int = 6) -> float | None:
    return None if value is None else round(value, digits)


def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    security = payload.get("security")
    if not isinstance(security, str) or not security.strip():
        raise InputError("security must be a non-empty string")

    primary_year = require_integer(payload, "primary_year")
    required_years = [primary_year - 2, primary_year - 1, primary_year]
    cost = optional_number(payload, "cost_per_share_cny", positive=True)
    holding_shares = optional_number(payload, "holding_shares", positive=True)

    eps = require_mapping(payload, "basic_eps")
    eps_value = require_number(eps, "value")
    eps_fx = require_number(eps, "fx_to_cny", positive=True)
    eps_rmb = eps_value * eps_fx

    dividend = require_mapping(payload, "dividend_per_share")
    dividend_value = require_number(dividend, "value", nonnegative=True)
    dividend_fx = require_number(dividend, "fx_to_cny", positive=True)
    coefficient = require_number(dividend, "coefficient", nonnegative=True)
    if coefficient > 1:
        raise InputError("dividend_per_share.coefficient must not exceed 1")
    dividend_rmb = dividend_value * dividend_fx
    after_tax_dividend_rmb = dividend_rmb * coefficient

    buybacks_value = payload.get("buybacks")
    if not isinstance(buybacks_value, list):
        raise InputError("buybacks must be an array")

    buybacks_by_year: dict[int, dict[str, Any]] = {}
    warnings: list[str] = []
    for index, item in enumerate(buybacks_value):
        if not isinstance(item, dict):
            raise InputError(f"buybacks[{index}] must be an object")
        year = require_integer(item, "year")
        if year in buybacks_by_year:
            raise InputError(f"duplicate buyback year: {year}")
        amount = require_number(item, "retired_amount", nonnegative=True)
        shares = require_number(item, "year_end_shares", positive=True)
        fx = require_number(item, "fx_to_cny", positive=True)
        estimated = item.get("estimated")
        if not isinstance(estimated, bool):
            raise InputError(f"buybacks[{index}].estimated must be boolean")
        buyback_per_share_rmb = amount / shares * fx
        buybacks_by_year[year] = {
            "year": year,
            "retired_amount": amount,
            "year_end_shares": shares,
            "fx_to_cny": fx,
            "estimated": estimated,
            "buyback_per_share_rmb": buyback_per_share_rmb,
        }
        if estimated:
            warnings.append(f"{year} strict retired-buyback amount is estimated")

    missing_years = [year for year in required_years if year not in buybacks_by_year]
    if missing_years:
        raise InputError(f"missing required buyback years: {missing_years}")

    annual_buyback_rows = [buybacks_by_year[year] for year in required_years]
    target_buyback_rmb = buybacks_by_year[primary_year]["buyback_per_share_rmb"]
    average_buyback_rmb = sum(
        row["buyback_per_share_rmb"] for row in annual_buyback_rows
    ) / len(annual_buyback_rows)

    prior_shares = buybacks_by_year[primary_year - 1]["year_end_shares"]
    current_shares = buybacks_by_year[primary_year]["year_end_shares"]
    net_share_change_rate = (current_shares - prior_shares) / prior_shares

    dividend_yield_rate: float | None = None
    comprehensive_return_rate: float | None = None
    total_cost_rmb: float | None = None
    position_cash_dividend_rmb: float | None = None
    position_equivalent_return_rmb: float | None = None

    if cost is not None:
        dividend_yield_rate = after_tax_dividend_rmb / cost
        comprehensive_return_rate = (
            after_tax_dividend_rmb + target_buyback_rmb
        ) / cost

    if holding_shares is not None:
        position_cash_dividend_rmb = after_tax_dividend_rmb * holding_shares
        position_equivalent_return_rmb = (
            after_tax_dividend_rmb + target_buyback_rmb
        ) * holding_shares
        if cost is not None:
            total_cost_rmb = cost * holding_shares

    annual_output = [
        {
            "year": row["year"],
            "buyback_per_share_rmb": rounded(row["buyback_per_share_rmb"]),
            "estimated": row["estimated"],
        }
        for row in annual_buyback_rows
    ]

    return {
        "security": security,
        "primary_year": primary_year,
        "row": {
            "cost_per_share_cny": rounded(cost),
            "basic_eps_cny": rounded(eps_rmb),
            "gross_dividend_per_share_cny": rounded(dividend_rmb),
            "dividend_coefficient": rounded(coefficient),
            "after_tax_dividend_per_share_cny": rounded(after_tax_dividend_rmb),
            "buyback_per_share_cny": rounded(target_buyback_rmb),
            "buyback_per_share_3y_average_cny": rounded(average_buyback_rmb),
            "net_share_change_rate": rounded(net_share_change_rate),
            "net_share_change_pct": rounded(net_share_change_rate * 100),
            "after_tax_dividend_yield_rate": rounded(dividend_yield_rate),
            "after_tax_dividend_yield_pct": rounded(
                None if dividend_yield_rate is None else dividend_yield_rate * 100
            ),
            "actual_comprehensive_return_rate": rounded(comprehensive_return_rate),
            "actual_comprehensive_return_pct": rounded(
                None
                if comprehensive_return_rate is None
                else comprehensive_return_rate * 100
            ),
            "holding_shares": rounded(holding_shares),
            "total_cost_cny": rounded(total_cost_rmb),
            "position_cash_dividend_cny": rounded(position_cash_dividend_rmb),
            "position_equivalent_return_cny": rounded(
                position_equivalent_return_rmb
            ),
        },
        "annual_buybacks": annual_output,
        "warnings": warnings,
    }


def write_result(result: dict[str, Any], output_path: str | None) -> None:
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if output_path is None:
        sys.stdout.write(rendered)
        return
    Path(output_path).write_text(rendered, encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        payload = read_payload(args.input)
        result = calculate(payload)
        write_result(result, args.output)
    except (InputError, json.JSONDecodeError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
