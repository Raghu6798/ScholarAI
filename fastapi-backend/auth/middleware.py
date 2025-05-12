# auth/middleware.py
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime
from typing import Optional
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

client = Client(
    url=os.getenv("SUPABASE_URL"),
    key=os.getenv("SUPABASE_KEY"),
)
print(client)
# class SupabaseAuthBearer(HTTPBearer):
#     def __init__(self, auto_error: bool = True):
#         super().__init__(auto_error=auto_error)
#         # Initialize Supabase client
#         self.supabase: Client = create_client(
#             os.getenv("SUPABASE_URL"),
#             os.getenv("SUPABASE_KEY")
#         )
#         self.jwt_secret = os.getenv("SUPABASE_JWT_SECRET")

#     async def __call__(self, request: Request) -> str:
#         credentials: HTTPAuthorizationCredentials = await super().__call__(request)
#         if not credentials:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Authorization header missing"
#             )

#         if credentials.scheme.lower() != "bearer":
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Invalid authentication scheme"
#             )

#         token = credentials.credentials
#         user = await self.verify_supabase_token(token)
        
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Invalid or expired token"
#             )
            
#         # Store user info in request state
#         request.state.user = user
#         return token

#     async def verify_supabase_token(self, token: str) -> Optional[dict]:
#         """Verify Supabase JWT token and return user info"""
#         try:
#             # First verify the token locally for performance
#             payload = jwt.decode(
#                 token,
#                 self.jwt_secret,
#                 algorithms=["HS256"],
#                 audience="authenticated",
#                 issuer=self.supabase.supabase_url or "supabase"
#             )
            
#             # Then get fresh user data from Supabase
#             user_data = self.supabase.auth.get_user(token)
#             if not user_data.user:
#                 return None
                
#             return {
#                 "id": user_data.user.id,
#                 "email": user_data.user.email,
#                 "role": payload.get("role"),
#                 "raw_user_metadata": user_data.user.user_metadata
#             }
            
#         except (JWTError, Exception) as e:
#             print(f"Authentication failed: {str(e)}")
#             return None