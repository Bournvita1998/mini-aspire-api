import unittest
from flask import Flask
from flask_testing import TestCase

from app import app, Loan

class MiniAspireAPITests(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        self.loan = Loan(amount=10000, term=3)

    def tearDown(self):
        # Clean up the loan after each test
        self.loan = None

    def test_create_loan(self):
        response = self.client.post('/loans', json={'amount': 10000, 'term': 3})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.app.loans), 1)

    def test_approve_loan(self):
        response = self.client.put(f'/loans/{self.loan.id}/approve')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.loan.state, 'APPROVED')

    def test_get_loan(self):
        response = self.client.get(f'/loans/{self.loan.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['loan']['id'], self.loan.id)

    def test_add_repayment(self):
        response = self.client.post(f'/loans/{self.loan.id}/repayments', json={'amount': 3333.33})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.app.repayments), 1)
        self.assertEqual(self.app.repayments[0].state, 'PAID')

if __name__ == '__main__':
    unittest.main()
