from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
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

# Serve PWA files
if os.path.exists("../pwa"):
    app.mount("/pwa", StaticFiles(directory="../pwa"), name="pwa")
elif os.path.exists("pwa"):
    app.mount("/pwa", StaticFiles(directory="pwa"), name="pwa")

@app.get("/", response_class=HTMLResponse)
async def landing():
    path = "pwa/index.html" if os.path.exists("pwa/index.html") else "../pwa/index.html"
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return "PWA index.html not found. Please check paths."

@app.post("/api/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        db_user = User(name=user.name, email=user.email, phone=user.phone, active=False)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    payment = initialize_payment(user.email, 2500)
    return {"payment_url": payment["data"]["authorization_url"], "reference": payment["data"].get("reference")}

@app.get("/mock-payment")
async def mock_payment_page(email: str):
    return HTMLResponse(f"""
        <h1>Mock Payment for {email}</h1>
        <form action="/webhook/paystack" method="post">
            <input type="hidden" name="email" value="{email}">
            <button type="submit">Simulate Success</button>
        </form>
        <script>
            document.querySelector('form').onsubmit = async (e) => {{
                e.preventDefault();
                const res = await fetch('/webhook/paystack', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        event: 'charge.success',
                        data: {{
                            customer: {{ email: '{email}' }},
                            reference: 'mock_ref_{email}'
                        }}
                    }})
                }});
                const data = await res.json();
                if (data.status === 'success') {{
                    alert('Payment Successful!');
                    window.location.href = '/?paid=true&email={email}';
                }}
            }};
        </script>
    """)

@app.post("/webhook/paystack")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    if payload.get("event") == "charge.success":
        email = payload["data"]["customer"]["email"]
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.active = True
            db.commit()
            # Start camera if we have a URL, but initially we might not.
            # The dashboard will call another endpoint to save URL and start.
            return {"status": "success", "message": "User activated"}
    return {"status": "success"}

@app.post("/api/activate-camera")
async def activate_camera(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")
    camera_url = data.get("camera_url")
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.active:
        raise HTTPException(status_code=403, detail="User not active or not found")

    camera = db.query(Camera).filter(Camera.user_id == user.id).first()
    if not camera:
        camera = Camera(user_id=user.id, camera_url=camera_url)
        db.add(camera)
    else:
        camera.camera_url = camera_url

    db.commit()
    start_user_camera(user.id, camera_url)
    return {"status": "success", "message": "Camera activated"}

@app.get("/api/user-status")
async def user_status(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"active": False}
    return {"active": user.active, "name": user.name}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
