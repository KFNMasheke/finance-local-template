# Finance Local

A free, local-first personal finance app for Windows PCs, with no subscription or bank login. Enter your own income, budget and debt details. ZAR and South African 2027 income-tax scenarios are built in.

## Start on Windows

1. Extract the complete ZIP into a permanent folder.
2. Install Python 3.10 or newer from https://www.python.org/downloads/windows/ if needed. Enable **Add Python to PATH**.
3. Double-click **Start-Finance.bat**. Your browser opens `http://127.0.0.1:8765`. Keep the console window open while using the app.
4. Add income under Monthly plan; add budgets and lender details; configure tax, savings and lifestyle targets.
5. Export a complete JSON backup regularly. Close the app with Ctrl+C in its console.

macOS/Linux: `python3 server.py` from the extracted folder. The server binds only to loopback. It must not be deployed as a public web service.

### No Python available?

Double-click `index.html` to use browser-only mode. CSV import, calculations and JSON backups work offline. Data is saved in that browser profile, separately from the Python app's database. PDF import is unavailable in this mode. Export/restore a JSON backup when switching modes; do not assume data synchronises automatically.

## Interface

The responsive dashboard uses a fixed sidebar on desktop, a two-column card layout on tablets, and stacked cards with bottom navigation and an expandable menu on smaller screens. Overview separates forecasts from imported bank activity and marks months without complete statement-period coverage. Tables retain horizontal scrolling for complete financial detail. The mobile layout does not add cloud synchronisation or expose the PC server to the network.

## Features

- Monthly dashboard and 12-month fixed-assumption cash outlook.
- Editable salary, contractor and business-profit forecasts; transfers and borrowing kept separate from earned income.
- Categorised transactions, CSV imports/exports and optional Standard Bank PDF imports with duplicate checks.
- Recurring merchant candidates and budget-vs-actual comparisons.
- Debt register, avalanche/snowball simulator, missing-interest-rate checks and affordable-extra cap.
- South African 2027 tax bands, PAYE reserve, partial-year projection and progressive gross-income target calculation.
- Monthly account reconciliation using opening + signed transactions = closing balance; audit statuses recalculate from the live ledger.
- Local SQLite persistence with the latest 100 saved states, plus user-controlled JSON backup/restore.

## Import a statement

CSV columns: `date,description,amount,balance,category`. `balance` and `category` columns are optional. Use ISO dates (`2026-10-01`), positive deposits and negative outflows. Quote descriptions containing commas. All amounts are ZAR. Download a sample from Monthly audit.

For text-based Standard Bank PDF statements, run **Install-PDF-Support.bat** once. This downloads the optional `pypdf` package from PyPI; PDF processing thereafter stays local. Other layouts, scanned PDFs, password-protected files and missing opening balance formats may require a bank CSV export. Encrypted PDFs must be unlocked locally first. Files larger than 20 MB are rejected.

Imports are previewed before saving. PDF imports can refresh the full statement period: overlapping imported rows are replaced, manual entries and matched categories are retained, and old overlapping audits are marked superseded. This avoids double-counting changed references, backdated reversals and settled card authorisations. Exact repeat refreshes are idempotent. Export a backup first. Append mode instead skips exact row matches per account. Use a consistent account nickname. Repeated identical CSV transactions without running balances can be ambiguous across overlapping statements: reconcile each import. Prefer complete monthly statements with balances. Loan proceeds, transfers and returned debit orders are not salary. A returned debit does not prove the debt was paid.

PDF extraction is layout-dependent. The bundled Standard Bank parser checks each running balance. Reconcile imported deposit/payment totals against the original statement before closing the month. The app does not connect to a bank or fetch statements in the background.

## Debt and tax assumptions

Only included debts with confirmed balances enter the simulator. APR must be entered; zero means confirmed interest-free, not unknown. Interest is APR/12 on the opening balance, followed by minimum payments and then the extra payment. Freed payments roll forward. Daily interest, fees, rate changes, arrears and settlement penalties are excluded. The home loan can remain outside accelerated debt repayment while its contractual payment stays in the monthly budget. Update lender balances manually: bank debits alone cannot establish outstanding principal.

The 2027 tax year runs **1 March 2026–28 February 2027**. The tax model uses SARS brackets and age rebates, then subtracts entered annual medical/other credits. Taxable benefits are additions to taxable income, not cash. Enter only allowable annual deductions and validate retirement-fund limits and IRP5 treatment. PAYE is a credit against combined income tax; the reserve is the remaining estimated liability. Cash forecasts deduct the greater of actual PAYE and modelled monthly tax, so an expected refund never increases available cash before it is received. Cash payroll deductions such as employee provident and UIF reduce spendable cash separately. No automatic tax filing, SARS account lookup, arrears determination or future tax-band updates are provided.

The annual run rate assumes 12 unchanged months. The actual-year projection has separate editable totals; it must account for partial employment, all other income, tax paid, benefits and deductions. The gross-income target holds existing deductions and benefits constant and treats additional income as taxable cash profit. It does not include additional business costs needed to earn it.

## Monthly close, by the fifth

1. Import every account for the previous month and confirm account names and duplicate handling.
2. Compare transaction counts, credits, debits and balances with each statement.
3. Reclassify unknown merchants and match internal transfers/refunds and returned debits.
4. Enter each account's exact statement dates and opening/closing balances in Monthly audit.
5. Refresh lender principal, APR, minimum payment and balance date; update payslip PAYE and tax assumptions.
6. Review next month's income, annual renewals, savings and extra debt payment.
7. Export a backup. The checklist is in-app; no unattended reminders are configured.

## Data safety

There is no telemetry, remote AI, cloud database, bank credential storage or CDN dependency. Your SQLite database and JSON backups are **unencrypted**: use device/disk encryption. Anyone with access to your PC files may read them. Keep financial data out of GitHub. The template starts blank. Never upload a personally seeded `index.html`, statements, exported CSVs or backups to a public repository.

The server serves a strict allowlist of application assets, checks loopback Host and same-origin writes, and keeps data files off HTTP routes. It is designed for one user on their own PC, not for shared hosting or multi-user use. Use one app tab at a time to avoid last-save-wins updates.

## Development

No Node packages are required to run the app. Python's standard library handles the local server and SQLite; optional dependency: `pypdf>=5,<7`.

Validation:

```sh
node test_core.js
node test_views.js
python -m unittest test_server.py
```

Core tests cover tax boundaries, combined-income reserves, gross-up, import validation, duplicate identities, audit arithmetic and debt amortisation. View tests render all seven screens against a DOM stub; they are not browser visual tests. API tests cover persistence, rejected cross-origin writes, file isolation and split-line statement parsing. This release has not been visually tested in a Windows browser.

### GitHub template publishing

The clean source package contains `Publish-GitHub.ps1`, which uses the authenticated GitHub CLI to create **finance-local-template** as a public repository, push this blank app and enable GitHub's template flag. It refuses to publish if the embedded seed contains any personal transactions, income or debts. Install Git and GitHub CLI, run `gh auth login`, then run the script from the clean source folder. Existing repositories are not overwritten.

## Sources

- SARS individual tax bands: https://www.sars.gov.za/tax-rates/income-tax/rates-of-tax-for-individuals/
- SARS medical tax credits: https://www.sars.gov.za/tax-rates/medical-tax-credit-rates/
- SARS multiple sources of income: https://www.sars.gov.za/types-of-tax/personal-income-tax/income-from-two-sources/
- SARS provisional tax: https://www.sars.gov.za/types-of-tax/provisional-tax/
- CFPB repayment methods: https://www.consumerfinance.gov/archive/blog/how-reduce-your-debt/

Tax source check: 15 October 2026. Reverify before using the model for a new tax year. This is an estimate and reconciliation tool, not a substitute for a lender settlement quote, an accountant or a SARS assessment.

## License

MIT. You may reuse, modify and distribute the clean application. Private financial records and third-party documents are not included in this license.
