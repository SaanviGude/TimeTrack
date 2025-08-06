from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from ..crud.auth import get_user_by_id, get_user_by_email, create_user, authenticate_user, request_password_reset, reset_user_password
from ..schemas.auth import UserSignup, Token, ForgotPasswordRequest, ResetPasswordRequest, ForgotPasswordResponse
from ..schemas.user import UserResponse
from ..utils import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, verify_token, create_reset_token, verify_reset_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = verify_token(token)
    if user_id is None:
        raise credentials_exception

    # Convert string UUID back to UUID object
    try:
        import uuid
        user_uuid = uuid.UUID(user_id)
        user = get_user_by_id(db, user_id=user_uuid)
    except (ValueError, TypeError):
        raise credentials_exception

    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=UserResponse)
def register_user(user: UserSignup, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create new user
    return create_user(db=db, user=user)


@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """Request password reset for user account"""
    
    # Check if user exists (but don't reveal this information)
    user_exists = request_password_reset(db, request.email)
    
    if user_exists:
        # Generate reset token
        reset_token = create_reset_token(request.email)
        
        # In production, you would:
        # 1. Store this token in database with expiration
        # 2. Send email with reset link containing the token
        # 3. NOT return the token in the response
        
        # For development/testing, returning the token
        return ForgotPasswordResponse(
            message="If the email exists, a password reset link has been sent.",
            reset_token=reset_token  # Remove this in production
        )
    else:
        # Always return the same message for security
        # Don't reveal whether the email exists or not
        return ForgotPasswordResponse(
            message="If the email exists, a password reset link has been sent.",
            reset_token=""  # No token for non-existent users
        )


@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset password using reset token"""
    
    # Verify the reset token
    email = verify_reset_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Reset the password
    success = reset_user_password(db, email, request.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to reset password. User may not exist or be inactive."
        )
    
    return {"message": "Password has been reset successfully"}
