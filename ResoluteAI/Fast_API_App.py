from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from jose import jwt, JWTError
from passlib.hash import bcrypt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize FastAPI, MongoDB, and logging
app = FastAPI()
client = MongoClient("mongodb+srv://sammjsagar:sam123@cluster0.djbdb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["mydatabase"]
users_collection = db["users"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Pydantic Models
class User(BaseModel):
    username: str
    email: EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Routes
@app.post("/signup", status_code=201)
def signup(user: UserCreate):
    # Check if user already exists
    if users_collection.find_one({"email": user.email}):
        logging.error(f"User with email {user.email} already exists")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password and insert new user
    hashed_password = bcrypt.hash(user.password)
    new_user = {"username": user.username, "email": user.email, "hashed_password": hashed_password}
    users_collection.insert_one(new_user)
    logging.info(f"User {user.username} created successfully")
    return {"msg": "User created successfully"}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Check if user exists
    user = users_collection.find_one({"email": form_data.username})
    if not user or not bcrypt.verify(form_data.password, user["hashed_password"]):
        logging.error(f"Failed login attempt for user {form_data.username}")
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Create JWT token
    token_data = {"sub": user["email"], "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    logging.info(f"User {form_data.username} logged in successfully")
    return {"access_token": token, "token_type": "bearer"}

@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    # TODO: Implement logout functionality (e.g., token revocation or blacklisting)
    logging.info(f"User logged out successfully")
    return {"msg": "Logged out successfully"}

@app.get("/users/me", response_model=User)
def read_users_me(token: str = Depends(oauth2_scheme)):
    # Decode JWT token
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        if not email:
            logging.error("Invalid token: no email found in payload")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        logging.error("Invalid token: unable to decode")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Retrieve user info
    user = users_collection.find_one({"email": email})
    if not user:
        logging.error(f"User with email {email} not found")
        raise HTTPException(status_code=404, detail="User not found")
    logging.info(f"User {user['username']} retrieved successfully")
    return {"username": user["username"], "email": user["email"]}

@app.post("/users", response_model=User, status_code=201)
def create_user(user: UserCreate, token: str = Depends(oauth2_scheme)):
    # Decode JWT token and check if user is admin
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        if not email or users_collection.find_one({"email": email})["role"] != "admin":
            logging.error("Unauthorized attempt to create user")
            raise HTTPException(status_code=403, detail="Forbidden")
    except JWTError:
        logging.error("Invalid token: unable to decode")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check if user already exists
    if users_collection.find_one({"email": user.email}):
        logging.error(f"User with email {user.email} already exists")
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password and insert new user
    hashed_password = bcrypt.hash(user.password)
    new_user = {"username": user.username, "email": user.email, "hashed_password": hashed_password, "role": "user"}
    users_collection.insert_one(new_user)
    logging.info(f"User {user.username} created successfully")
    return {"username": user.username, "email": user.email}

# Script to create an initial admin user (optional)
def create_initial_admin_user():
    initial_user = {"username": "admin", "email": "admin@example.com", "password": "password123", "role": "admin"}
    if not users_collection.find_one({"email": initial_user["email"]}):
        signup(UserCreate(**initial_user))
        logging.info("Admin user created with email: admin@example.com and password: password123")

# Run script if this is the main module
if __name__ == "__main__":
    import uvicorn
    create_initial_admin_user()
    uvicorn.run(app, host="0.0.0.0", port=8000)
    