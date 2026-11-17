import sys
import os

# add the root project to sys.path in a absolute and dynamic form
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from payments.pix import Pix

def test_pix_create_payment():
	pix_instance = Pix()

	# create a payment
	payment_info = pix_instance.create_payment()

	assert 'bank_payment_id' in payment_info
	assert 'qr_code_path' in payment_info
	assert os.path.isfile(f'static/img/{payment_info['qr_code_path']}')
