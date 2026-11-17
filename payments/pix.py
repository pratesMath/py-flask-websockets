import os
import uuid
import qrcode

class Pix:
	def __init__(self) -> None:
		pass

	def create_payment(self):
		# create the payment on the bank (payment/financial organization)
		bank_payment_id = str(uuid.uuid4())

		# qr code
		hash_payment = f'hash_payment_{bank_payment_id}'
		img = qrcode.make(hash_payment)

		output_dir = 'static/img'
		os.makedirs(output_dir, exist_ok=True)

		file_name = f'qr_code_payment_{bank_payment_id}.png'
		file_path = os.path.join(output_dir, file_name)

		img.save(file_path)

		return {
			'bank_payment_id': bank_payment_id,
			'qr_code_path': file_name,
		}
