from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import User, Camera, get_db
from schemas import UserCreate, PaymentVerify
from payments import initialize_payment, verify_payment
from docker_manager import start_user_camera
import os

app = FastAPI(title="SecureEye.ng v15")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def landing():
    with open("frontend/index.html") as f:
        return f.read()

@app.post("/api/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    payment = initialize_payment(user.email, user.phone)
    db_user = User(name=user.name, email=user.email, phone=user.phone, active=False)
    db.add(db_user)
    db.commit()
    return {"payment_url": payment["data"]["authorization_url"]}

@app.post("/webhook/paystack")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    if payload["event"] == "charge.success":
        email = payload["data"]["customer"]["email"]
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.active = True
            db.commit()
            start_user_camera(user.id, "0")
    return {"status": "success"}
