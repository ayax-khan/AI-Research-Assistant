from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.otp import OTP
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.schemas.otp import OTPRequest, OTPVerify, OTPResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user
from app.services.otp_service import otp_service
from app.services.email_service import email_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    existing = result.scalar_one_or_none()
    if existing:
        if existing.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        existing.name = payload.name
        existing.hashed_password = hash_password(payload.password)
        await db.flush()
        await db.refresh(existing)
        user = existing
    else:
        user = User(
            name=payload.name,
            email=payload.email,
            hashed_password=hash_password(payload.password),
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

    otp = await otp_service.create_otp(user.id, db)
    sent = await email_service.send_otp_email(user.email, otp.code)
    if not sent:
        await db.delete(otp)
        await db.delete(user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email. Check SMTP configuration.",
        )

    return {"message": "OTP sent to email. Verify to activate account.", "email": user.email}


@router.post("/verify-otp", response_model=Token)
async def verify_otp(payload: OTPVerify, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_active:
        raise HTTPException(status_code=400, detail="Account already verified")

    valid = await otp_service.verify_otp(user.id, payload.code, db)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user.is_active = True
    await db.flush()
    token = create_access_token(data={"sub": user.id})
    return Token(access_token=token)


@router.post("/resend-otp", response_model=OTPResponse)
async def resend_otp(payload: OTPRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_active:
        raise HTTPException(status_code=400, detail="Account already verified")

    await otp_service.invalidate_user_otps(user.id, db)
    otp = await otp_service.create_otp(user.id, db)
    sent = await email_service.send_otp_email(user.email, otp.code)
    if not sent:
        raise HTTPException(
            status_code=500, detail="Failed to send OTP email. Check SMTP configuration."
        )

    return OTPResponse(message="New OTP sent to your email", success=True)


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not verified. Please verify OTP first.",
        )
    token = create_access_token(data={"sub": user.id})
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
