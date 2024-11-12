### Directory Contents
- `main.py`: The main FastAPI application file.
- `.env`: Environment file (created by you with MongoDB URI and JWT secret).
- `README.md`: Instructions on setting up the application.

---

1. **Install Dependencies**

   You need Python 3.7+ and MongoDB installed on your system. First, install `pip` dependencies:

   ```bash
   pip install fastapi pymongo[snappy,gssapi] "python-dotenv" "passlib[bcrypt]" pyjwt uvicorn
   ```

2. **Environment Variables**

   Create a `.env` file in the project directory with your MongoDB URI and JWT secret key.

  
   MONGO_URI="mongodb+srv://username:password@cluster0.mongodb.net/<database>?retryWrites=true&w=majority"
   JWT_SECRET="your_jwt_secret_key"


   Replace `<username>`, `<password>`, and `<database>` with your MongoDB Atlas credentials.

4. **Run the App**

   To start the application, run:


   uvicorn main:app


   The server will start at `http://127.0.0.1:8000`.

Explanation of Key Features

1. **User Signup** (`/signup`): Registers a new user by hashing their password and saving it to MongoDB.

2. **User Login** (`/login`): Authenticates a user by validating the password and generates a JWT token.

3. **Protected Endpoints** (`/users/me`, `/users`): Endpoints that require a valid JWT token to access user information or create new users (admin only).

4. **JWT Authentication**: Ensures secure access with JSON Web Tokens for all protected endpoints.

5. **Logging**: Logs significant actions such as successful login attempts, user creation, and failed login attempts for easy debugging and monitoring.

6. **Admin Creation Script**: Creates an initial admin user on the first run. Admin can manage other users.
