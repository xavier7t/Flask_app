import unittest
from app import app, db, Transaction, fetch_usd_rate
from unittest.mock import patch

class TransactionAppTests(unittest.TestCase):
    def setUp(self):
        # Setup for tests, initializing the test client and setting up a fresh database.
        self.app = app.test_client()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # Cleanup after tests
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_fetch_usd_rate(self):
        # Test the fetch_usd_rate function with valid and invalid currency codes.
        with patch('requests.get') as mock_get:
            # Simulate a successful API response
            mock_get.return_value.json.return_value = {
                "result": "success",
                "rates": {"USD": 1.2, "EUR": 1.0}
            }
            self.assertEqual(fetch_usd_rate("EUR"), 1.2)

            # Simulate an unsuccessful API response
            mock_get.return_value.json.return_value = {"result": "failure"}
            self.assertEqual(fetch_usd_rate("GBP"), 1.0)  # Fallback to 1.0

            # Handle exceptions
            mock_get.side_effect = Exception("Network issue")
            self.assertEqual(fetch_usd_rate("JPY"), 1.0)  # Fallback to 1.0

    def test_form_submission(self):
        # Test the form submission functionality
        response = self.app.post('/', data={
            'description': 'Lunch',
            'amount': '30.00',
            'currency': 'EUR',
            'account': '123456'
        })
        self.assertEqual(response.status_code, 200)

        # Additionally, you can submit and check the database for the transaction
        response = self.app.post('/echo_user_input', data={
            'description': 'Dinner',
            'amount': '20.00',
            'currency': 'USD',
            'account': '123456'
        })
        self.assertIn(b'Transaction Recorded', response.data)

        # Verify if the transaction was saved in the database
        with self.app.app_context():
            transaction = Transaction.query.first()
            assert transaction.description == 'Dinner'
            assert transaction.amount == 20.00

    def test_total_expenses(self):
        # Test if total expenses calculation works
        with self.app.app_context():
            # Adding transaction directly to the database for testing
            transaction1 = Transaction(
                description='Test Transaction 1',
                amount=30.00,
                currency='EUR',
                usd_rate=1.2,
                usd_amount=36.00,
                account='123456'
            )
            transaction2 = Transaction(
                description='Test Transaction 2',
                amount=20.00,
                currency='USD',
                usd_rate=1.0,
                usd_amount=20.00,
                account='123456'
            )
            db.session.add(transaction1)
            db.session.add(transaction2)
            db.session.commit()

            # Calculate total USD across all transactions
            total_usd = db.session.query(db.func.sum(Transaction.usd_amount)).scalar() or 0
            self.assertEqual(total_usd, 56.00)

if __name__ == '__main__':
    unittest.main()

