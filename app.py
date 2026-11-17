from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, request, send_file
from repository.database import db
from models.payment import Payment
from payments.pix import Pix
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'SECRET_KEY'

db.init_app(app)
ws = SocketIO(app)

@app.route('/payments/pix', methods=['POST'])
def create_payment_pix():
	data = request.get_json()

	if 'value' not in data:
		return jsonify({'message': 'invalid value'}), 400

	expiration_date = datetime.now() + timedelta(minutes=30)

	new_payment = Payment(
		value=data['value'],
		expiration_date=expiration_date
	)

	pix = Pix()
	pix_data = pix.create_payment()

	new_payment.bank_payment_id = pix_data['bank_payment_id']
	new_payment.qr_code = pix_data['qr_code_path']

	db.session.add(new_payment)
	db.session.commit()

	return jsonify({
		'message': 'The payment has been created',
		'payment': new_payment.to_dict(),
	}), 201

@app.route('/payments/pix/qr_code/<file_name>', methods=['GET'])
def get_image(file_name: str):
    return send_file(f'static/img/{file_name}.png', mimetype='image/png')

@app.route('/payments/pix/confirmation', methods=['POST'])
def confirmation_pix():
	data = request.get_json()

	# validations
	if 'bank_payment_id' not in data and 'value' not in data:
		return jsonify({'message': 'Invalid payment data'}), 400

	bank_payment_id = data.get('bank_payment_id')
	# payment
	payment = Payment.query.filter_by(bank_payment_id=bank_payment_id).first()

	if not payment or payment.paid == True:
		return jsonify({'message':'Payment not found'}), 404

	value = data.get('value')

	if value != payment.value:
		return jsonify({'message': 'Invalid payment data'}), 400

	# database
	payment.paid = True
	db.session.commit()

	ws.emit(f'payment-confirmed-{payment.id}')
	return jsonify({'message': 'The payment has been confirmed'})

@app.route('/payments/pix/<int:payment_id>', methods=['GET'])
def payment_pix_page(payment_id: int):
	payment = Payment.query.get(payment_id)

	if not payment:
		return render_template('404.html')

	if payment.paid:
		return render_template(
			'confirmed_payment.html',
			payment_id = payment.id,
			value = payment.value
		)

	return render_template(
		'payment.html',
		payment_id=payment.id,
		value=payment.value,
		host="http://127.0.0.1:5000",
		qr_code=payment.qr_code,
	)

# WebSockets
@ws.on('connect')
def handle_connect():
	print('Client connected to the server!')

@ws.on('disconnect')
def handle_disconnect():
	print('Client has disconnected to the server!')

if __name__ == '__main__':
  ws.run(app, debug=True)
