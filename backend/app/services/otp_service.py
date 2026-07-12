import random
import string
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.models.otp import OTP


class OTPService:
    @staticmethod
    def generate_code() -> str:
        return "".join(random.choices(string.digits, k=6))

    @staticmethod
    async def create_otp(user_id: int, db: AsyncSession) -> OTP:
        code = OTPService.generate_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

        otp = OTP(
            user_id=user_id,
            code=code,
            expires_at=expires_at,
        )
        db.add(otp)
        await db.flush()
        await db.refresh(otp)
        return otp

    @staticmethod
    async def verify_otp(user_id: int, code: str, db: AsyncSession) -> bool:
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(OTP).where(
                OTP.user_id == user_id,
                OTP.code == code,
                OTP.is_used == False,
                OTP.expires_at > now,
            ).order_by(OTP.created_at.desc()).limit(1)
        )
        otp = result.scalar_one_or_none()
        if not otp:
            return False

        otp.is_used = True
        await db.flush()
        return True

    @staticmethod
    async def invalidate_user_otps(user_id: int, db: AsyncSession) -> None:
        from sqlalchemy import update
        await db.execute(
            update(OTP).where(OTP.user_id == user_id).values(is_used=True)
        )


otp_service = OTPService()
