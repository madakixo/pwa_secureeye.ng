import requests
import os

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "sk_test_mock")

def initialize_payment(email: str, amount: int):
    # Paystack amount is in kobo (100 kobo = 1 Naira)
    # 2500 Naira = 250000 kobo
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "amount": 250000,
        "callback_url": os.getenv("PAYMENT_CALLBACK_URL", "http://localhost:8000/api/payment/callback")
    }

    if PAYSTACK_SECRET_KEY == "sk_test_mock":
        return {
            "status": True,
            "data": {
                "authorization_url": f"http://localhost:8000/mock-payment?email={email}",
                "reference": "mock_ref_" + email
            }
        }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

def verify_payment(reference: str):
    if reference.startswith("mock_ref_"):
        return {"status": True, "data": {"status": "success", "customer": {"email": reference.replace("mock_ref_", "")}}}

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }
    response = requests.get(url, headers=headers)
    return response.json()
