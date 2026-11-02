# Captioned project walkthrough

This is a screen recording of the browser companion, with on-screen explanation and no spoken narration.

## Project scope
180,519 order-item shipment lines. Public / synthetic educational case; no real company performance claim.

## How it was built
Python loads and validates the CSV, derives actual-minus-scheduled gaps, and exports privacy-minimized aggregates for this browser companion.

## Explore the reporting population
Changing the shipping mode recomputes every KPI. First Class has a 100% positive-gap rate in this supplied dataset.

## Check the existing risk flag
The dataset risk flag and the calculated delay classification use different definitions. Canceled lines explain the documented disagreements.

## Compare modes and reporting bases
Mode tables show volume alongside rates. Excluding canceled lines is a sensitivity view, not evidence of completed-delivery outcomes.

## Review regions with context
Regional comparisons are descriptive. There is no date column for trends and no order key for distinct-order rates.

## Reproduce and review
Source code, methods and a technical report accompany the demo. Delayed-sales exposure is not confirmed loss or measured savings.
