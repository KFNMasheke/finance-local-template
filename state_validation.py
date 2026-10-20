"""Validate persisted local finance records independently of the browser."""
import math
from datetime import date


def number(value, label, minimum=0, nullable=False):
    if value is None and nullable:
        return
    if type(value) not in (int, float) or not math.isfinite(value) or value < minimum:
        raise ValueError('Invalid ' + label)


def validate_state(state):
    sections = ('transactions', 'income', 'budgets', 'debts', 'audits')
    if (not isinstance(state, dict) or type(state.get('version')) is not int
            or state['version'] != 1 or not isinstance(state.get('settings'), dict)
            or any(not isinstance(state.get(k), list) for k in sections)):
        raise ValueError('Invalid finance data')
    for key in sections:
        if len(state[key]) > 100000 or any(not isinstance(row, dict) for row in state[key]):
            raise ValueError('Invalid ' + key)
    ids = set()
    for row in state['transactions']:
        identity = row.get('id')
        if not isinstance(identity, str) or not identity or identity in ids:
            raise ValueError('Invalid or duplicate transaction ID')
        ids.add(identity)
        try:
            if date.fromisoformat(row['date']).isoformat() != row['date']:
                raise ValueError()
        except (KeyError, TypeError, ValueError):
            raise ValueError('Invalid transaction date') from None
        if not isinstance(row.get('description'), str) or not isinstance(row.get('category'), str):
            raise ValueError('Invalid transaction fields')
        number(row.get('amount'), 'transaction amount', -math.inf)
        number(row.get('balance'), 'transaction balance', -math.inf, nullable=True)
    for key in ('income', 'budgets'):
        for row in state[key]:
            number(row.get('amount'), key + ' amount')
    for row in state['debts']:
        for key in ('balance', 'minimum'):
            number(row.get(key), 'debt ' + key)
        number(row.get('apr'), 'debt APR', nullable=True)
        if row.get('apr') is not None and row['apr'] > 1000:
            raise ValueError('Invalid debt APR')
    def finite(value, depth=0):
        if depth > 50:
            raise ValueError('Finance data is nested too deeply')
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('Non-finite finance value')
        if isinstance(value, dict):
            for item in value.values():
                finite(item, depth + 1)
        elif isinstance(value, list):
            for item in value:
                finite(item, depth + 1)
    finite(state)
    for key in ('age', 'taxableBenefits', 'deductions', 'taxCredits', 'otherDeductions',
                'savings', 'extraDebt', 'comfort', 'lifestyleBase', 'payeMonthly'):
        if key in state['settings']:
            number(state['settings'][key], 'settings ' + key, nullable=key in ('payeMonthly', 'lifestyleBase'))
    return state
