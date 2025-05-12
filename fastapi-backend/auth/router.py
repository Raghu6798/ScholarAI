# auth/router.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta
from .middleware import SupabaseAuthBearer, create_client
from supabase import Client
import os
from dotenv import load_dotenv

load_dotenv()

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserResponse(BaseModel):
    id: str
    email: str
    role: str

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

@auth_router.post("/token", response_model=TokenResponse)
async def login_with_email(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer",
            "expires_in": auth_response.session.expires_in
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

@auth_router.post("/signup")
async def sign_up_with_email(email: str, password: str):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return {"status": "success", "user_id": response.user.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@auth_router.post("/oauth")
async def handle_oauth_callback(provider: str, token: str):
    try:
        # For OAuth flows initiated in frontend
        # Just validate the token that frontend already obtained
        user = supabase.auth.get_user(token)
        if not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid OAuth token"
            )
            
        return {
            "access_token": token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@auth_router.get("/me", response_model=UserResponse, dependencies=[Depends(SupabaseAuthBearer())])
async def get_current_user(request: Request):
    user = request.state.user
    return {
        "id": user["id"],
        "email": user["email"],
        "role": user["role"]
    }