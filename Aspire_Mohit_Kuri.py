from flask import Flask, jsonify, request

app = Flask(__name__)

loans = []
repayments = []

class Loan:
    def __init__(self, amount, term):
        self.amount = amount
        self.term = term
        self.state = 'PENDING'
        self.id = len(loans) + 1

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'term': self.term,
            'state': self.state
        }

class Repayment:
    def __init__(self, loan_id, amount):
        self.loan_id = loan_id
        self.amount = amount
        self.state = 'PENDING'
        self.id = len(repayments) + 1

    def to_dict(self):
        return {
            'id': self.id,
            'loan_id': self.loan_id,
            'amount': self.amount,
            'state': self.state
        }

def find_loan(loan_id):
    for loan in loans:
        if loan.id == loan_id:
            return loan
    return None

@app.route('/loans', methods=['POST'])
def create_loan():
    data = request.get_json()
    amount = data.get('amount')
    term = data.get('term')

    if amount is None or term is None:
        return jsonify({'error': 'Invalid loan data'}), 400

    loan = Loan(amount, term)
    loans.append(loan)

    # Generate scheduled repayments
    repayment_amount = amount / term
    for i in range(term):
        repayments.append(Repayment(loan.id, repayment_amount))

    return jsonify({'message': 'Loan created', 'loan': loan.to_dict()}), 201

@app.route('/loans/<int:loan_id>/approve', methods=['PUT'])
def approve_loan(loan_id):
    loan = find_loan(loan_id)
    if loan is None:
        return jsonify({'error': 'Loan not found'}), 404

    # Check if the loan is already approved
    if loan.state == 'APPROVED':
        return jsonify({'message': 'Loan already approved', 'loan': loan.to_dict()})

    loan.state = 'APPROVED'
    return jsonify({'message': 'Loan approved', 'loan': loan.to_dict()})

@app.route('/loans/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    loan = find_loan(loan_id)
    if loan is None:
        return jsonify({'error': 'Loan not found'}), 404

    return jsonify({'loan': loan.to_dict()})

@app.route('/loans/<int:loan_id>/repayments', methods=['POST'])
def add_repayment(loan_id):
    loan = find_loan(loan_id)
    if loan is None:
        return jsonify({'error': 'Loan not found'}), 404

    data = request.get_json()
    amount = data.get('amount')
    if amount is None:
        return jsonify({'error': 'Invalid repayment data'}), 400

    # Find the next scheduled repayment and mark it as paid
    for repayment in repayments:
        if repayment.loan_id == loan.id and repayment.state == 'PENDING':
            if amount >= repayment.amount:
                repayment.state = 'PAID'
            return jsonify({'message': 'Repayment added', 'repayment': repayment.to_dict()})

    return jsonify({'error': 'No pending repayments found'}), 404

if __name__ == '__main__':
    app.run
