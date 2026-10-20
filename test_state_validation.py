import copy
import unittest
from state_validation import validate_state


def state():
    return dict(version=1, transactions=[], income=[], budgets=[], debts=[], audits=[], settings={})


class StateValidationTests(unittest.TestCase):
    def test_valid_negative_bank_balance_and_unknown_apr(self):
        s = state()
        s['settings']['lifestyleBase'] = None
        s['transactions'] = [dict(id='a', date='2026-10-20', description='Example',
                                  category='Other / review', amount=-10, balance=-50)]
        s['debts'] = [dict(balance=100, minimum=10, apr=None)]
        self.assertIs(validate_state(s), s)

    def test_invalid_numeric_and_record_data(self):
        for value in (-1, float('nan'), float('inf'), True, '100'):
            s = state()
            s['debts'] = [dict(balance=value, minimum=10, apr=None)]
            with self.assertRaises(ValueError):
                validate_state(s)
        s = state()
        s['settings']['projection'] = {'bad': float('nan')}
        with self.assertRaises(ValueError):
            validate_state(s)
        for row in (None, [], 'bad'):
            s = state()
            s['income'] = [row]
            with self.assertRaises(ValueError):
                validate_state(s)

    def test_duplicate_ids_and_impossible_dates(self):
        row = dict(id='a', date='2026-02-30', description='Example', category='Other', amount=1)
        s = state()
        s['transactions'] = [row]
        with self.assertRaises(ValueError):
            validate_state(s)
        row['date'] = '2026-02-28'
        s['transactions'].append(copy.copy(row))
        with self.assertRaises(ValueError):
            validate_state(s)
