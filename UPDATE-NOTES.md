# Income and debt focus update

## Keep your latest edits

1. In the running app, export a complete backup from Details & backups.
2. Stop the old server with Ctrl+C. Close old Finance Local tabs.
3. Extract this update directly into your existing app folder, replacing application files. Keep your existing `data` folder. No database or personal seed is included in the update.
4. Run Start-Finance.bat. It prepares a private Python environment and installs PDF support once. The first setup requires internet. Subsequent starts use installed dependencies.
5. Refresh the browser tab. Check Monthly plan and Debt freedom.

Your existing database takes priority over bundled starting data. Do not restore an older starting backup over your latest edits. Browser-only users should export a backup before this update, then restore that exported backup if the updated app opens blank. Browser-only editions can have different storage identities. Changing to the Python app also requires export and restore.

## What changes on first load

Income stays as entered. Debt instalments now come from each debt-register record, including mortgage and vehicle finance, independently of the acceleration checkbox. The old aggregate debt budgets are retained in backups but no longer counted, preventing duplication.

Historical non-debt budgets keep their amounts and sources but are excluded. Add, edit and tick optional living costs yourself. This migration runs once; later selections remain yours. Overdraft interest labelled as an expense proxy is excluded from contractual minimums. Set its actual repayment type and amount when confirmed by the bank. Zero placeholders do not mean there is no liability.

The dashboard separates remaining after debt from the final balance after selected living costs and savings. Missing living allowances can overstate what is available for extra debt repayments. Lender figures are dated until you confirm them. A complete debt payoff forecast still requires current balances and APRs.

## New pages and feedback

- **Monthly plan:** included amounts, sources, evidence statuses and change history. Previous edits have no invented timestamps.
- **Trends:** historical income categories, other deposits, debt outflows and optional spending by month. These do not become automatic fixed budgets.
- **What-if cash flow:** extra net income for a chosen number of months; proposed loan repayment, term and optional cash received. Live scenario calculations leave the real budget unchanged. Borrowing is separate from earned income.
- **Save feedback:** save status on desktop/mobile, success toast after persistence, failure notice and Save now retry. Budget inputs update the live total as you type and save after a short pause.
- **Standard Bank PDFs:** original text-based PDFs, both supplied layouts, including Standard Bank files with an empty opening password. Files requiring a real password need an unlocked local copy. The importer verifies every running balance, printed deposits/payments, account ending and date range before preview. Refresh replaces the overlapping period and retains manual records and matched categories. CSV remains optional.
- **Local assistant:** automatic rule-based suggestions. Ask local AI is optional and requires Ollama with a downloaded local model. Enter the exact name from `ollama list`. Cloud model tags are blocked; no model is installed automatically. AI explanations cannot edit records. AI responses may be wrong and must be checked.

## Validation and limits

Automated calculation, migration, scenario, save acknowledgement, view-render and HTTP API checks are included. Both original statement PDFs were checked against printed totals. Browser visual QA and a live Ollama model session were not available in the build environment. Windows launcher execution must still be checked on your PC. This is a local budgeting application under active development, not a complete accounting package, bank connection or automatic tax filing service.
