"""
⚽ NEXUS FOOTBALL — User Authentication System
JWT-based authentication with role-based access control
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime, timedelta
from jose import JWTError, jwt
import logging
from enum import Enum

logger = logging.getLogger(__name__)
router = APIRouter()

# ━━━━━ CONFIGURATION ━━━━━

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()

# ━━━━━ ENUMS ━━━━━

class UserRole(str, Enum):
    ADMIN = "admin"
    PREMIUM = "premium"
    FREE = "free"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

# ━━━━━ DATA MODELS ━━━━━

class UserRegister(BaseModel):
    """User registration request"""
    username: str
    email: EmailStr
    password: str
    country: Optional[str] = None

class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    """User profile response"""
    user_id: str
    username: str
    email: str
    country: str
    role: UserRole
    status: UserStatus
    total_points: int
    correct_predictions: int
    accuracy_percentage: float
    tournament_rank: int
    created_at: datetime
    updated_at: datetime

class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str

# ━━━━━ TOKEN MANAGEMENT ━━━━━

class TokenManager:
    """Manage JWT tokens"""
    
    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None):
        """Create access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict):
        """Create refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str):
        """Verify and decode token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            return payload
        
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

# ━━━━━ AUTHENTICATION MANAGER ━━━━━

class AuthenticationManager:
    """Manage user authentication"""
    
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.sessions: Dict[str, Dict] = {}
        self.token_manager = TokenManager()
    
    def register_user(self, registration: UserRegister) -> Dict:
        """Register new user"""
        logger.info(f"Registering user: {registration.email}")
        
        # Check if user exists
        if any(u['email'] == registration.email for u in self.users.values()):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_id = f"user_{len(self.users) + 1}"
        
        # In production, hash password with bcrypt
        # from passlib.context import CryptContext
        # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # hashed_password = pwd_context.hash(registration.password)
        
        user = {
            "user_id": user_id,
            "username": registration.username,
            "email": registration.email,
            "password": registration.password,  # TODO: Hash this!
            "country": registration.country,
            "role": UserRole.FREE,
            "status": UserStatus.ACTIVE,
            "total_points": 0,
            "correct_predictions": 0,
            "accuracy_percentage": 0.0,
            "tournament_rank": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        self.users[user_id] = user
        
        return {"user_id": user_id, "message": "User registered successfully"}
    
    def login_user(self, login: UserLogin) -> TokenResponse:
        """Authenticate user and return tokens"""
        logger.info(f"Login attempt: {login.email}")
        
        # Find user by email
        user = None
        for u in self.users.values():
            if u['email'] == login.email:
                user = u
                break
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # TODO: Use bcrypt to verify password
        # if not pwd_context.verify(login.password, user['password']):
        if user['password'] != login.password:  # Never do this in production!
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if user['status'] != UserStatus.ACTIVE:
            raise HTTPException(status_code=403, detail="Account inactive")
        
        # Create tokens
        access_token = self.token_manager.create_access_token(
            data={"sub": user['user_id'], "email": user['email']}
        )
        
        refresh_token = self.token_manager.create_refresh_token(
            data={"sub": user['user_id']}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token"""
        payload = self.token_manager.verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user_id = payload.get("sub")
        user = self.users.get(user_id)
        
        if not user or user['status'] != UserStatus.ACTIVE:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        new_access_token = self.token_manager.create_access_token(
            data={"sub": user['user_id'], "email": user['email']}
        )
        
        new_refresh_token = self.token_manager.create_refresh_token(
            data={"sub": user['user_id']}
        )
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def get_user(self, user_id: str) -> UserProfile:
        """Get user profile"""
        user = self.users.get(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserProfile(**user)
    
    def upgrade_user_to_premium(self, user_id: str) -> Dict:
        """Upgrade user to premium tier"""
        user = self.users.get(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user['role'] = UserRole.PREMIUM
        user['updated_at'] = datetime.utcnow()
        
        logger.info(f"User {user_id} upgraded to premium")
        
        return {"message": "User upgraded to premium", "new_role": UserRole.PREMIUM}

# ━━━━━ GLOBAL INSTANCE ━━━━━

auth_manager = AuthenticationManager()

# ━━━━━ DEPENDENCY INJECTION ━━━━━

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = TokenManager.verify_token(token)
    user_id = payload.get("sub")
    
    user = auth_manager.users.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

async def get_premium_user(user = Depends(get_current_user)):
    """Require premium user"""
    if user['role'] not in [UserRole.PREMIUM, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Premium access required")
    
    return user

async def get_admin_user(user = Depends(get_current_user)):
    """Require admin user"""
    if user['role'] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user

# ━━━━━ API ENDPOINTS ━━━━━

@router.post("/register", tags=["Authentication"])
async def register(registration: UserRegister):
    """Register new user"""
    try:
        result = auth_manager.register_user(registration)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=TokenResponse, tags=["Authentication"])
async def login(login: UserLogin):
    """Login user and get tokens"""
    try:
        return auth_manager.login_user(login)
    except HTTPException:
        raise

@router.post("/refresh", response_model=TokenResponse, tags=["Authentication"])
async def refresh(refresh_request: TokenRefresh):
    """Refresh access token"""
    try:
        return auth_manager.refresh_token(refresh_request.refresh_token)
    except HTTPException:
        raise

@router.get("/profile", response_model=UserProfile, tags=["User"])
async def get_profile(current_user = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(**current_user)

@router.get("/profile/{user_id}", response_model=UserProfile, tags=["User"])
async def get_user_profile(user_id: str):
    """Get any user profile (public)"""
    try:
        return auth_manager.get_user(user_id)
    except HTTPException:
        raise

@router.post("/upgrade-premium", tags=["User"])
async def upgrade_premium(current_user = Depends(get_current_user)):
    """Upgrade to premium"""
    if current_user['role'] == UserRole.PREMIUM:
        raise HTTPException(status_code=400, detail="Already premium")
    
    return auth_manager.upgrade_user_to_premium(current_user['user_id'])

@router.post("/logout", tags=["Authentication"])
async def logout(current_user = Depends(get_current_user)):
    """Logout user (invalidate token)"""
    # TODO: Add token to blacklist/cache
    return {"message": "Logged out successfully"}

@router.get("/me", tags=["User"])
async def get_me(current_user = Depends(get_current_user)):
    """Get current user info"""
    return current_user
