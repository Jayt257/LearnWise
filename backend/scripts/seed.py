"""
backend/scripts/seed.py
Seeds the learnwise database with:
  1. Admin user (from .env settings)
  2. hi-ja language pair progress for admin (for testing roadmap)
  3. Verifies meta.json is accessible
Run: cd backend && ./venv/bin/python3 scripts/seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine, SessionLocal
from app.models.user import User, UserRole
from app.models.progress import UserLanguageProgress, ActivityCompletion
from app.models.friends import FriendRequest
from app.core.config import settings
from app.services import content_service
from passlib.context import CryptContext
import uuid
from datetime import datetime

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _hash(password: str) -> str:
    """Bcrypt requires passwords <= 72 bytes."""
    return pwd_ctx.hash(password[:72])

def seed():
    db = SessionLocal()
    try:
        print("=" * 50)
        print("LearnWise Database Seeder")
        print("=" * 50)

        # 1. Create admin user
        existing_admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if existing_admin:
            print(f"✓ Admin already exists: {existing_admin.email}")
            admin = existing_admin
        else:
            admin = User(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                password_hash=_hash(settings.ADMIN_PASSWORD),
                display_name="Platform Admin",
                role=UserRole.admin,
                is_active=True,
                native_lang="hi",
            )
            db.add(admin)
            db.flush()
            print(f"✓ Admin created: {admin.email} (role={admin.role})")

        # 2. Create a test regular user
        test_email = "testuser@learnwise.app"
        existing_user = db.query(User).filter(User.email == test_email).first()
        if existing_user:
            print(f"✓ Test user already exists: {existing_user.email}")
            test_user = existing_user
        else:
            test_user = User(
                username="testuser",
                email=test_email,
                password_hash=_hash("Test@1234"),
                display_name="Test Learner",
                role=UserRole.user,
                is_active=True,
                native_lang="hi",
            )
            db.add(test_user)
            db.flush()
            print(f"✓ Test user created: {test_user.email}")

        # 3. Create hi-ja progress for test user
        pair_id = "hi-ja"
        existing_progress = db.query(UserLanguageProgress).filter(
            UserLanguageProgress.user_id == test_user.id,
            UserLanguageProgress.lang_pair_id == pair_id,
        ).first()
        if existing_progress:
            print(f"✓ Progress already exists for {test_user.email} ({pair_id})")
        else:
            progress = UserLanguageProgress(
                user_id=test_user.id,
                lang_pair_id=pair_id,
                total_xp=0,
                current_month=1,
                current_block=1,
                current_activity_id=1,
            )
            db.add(progress)
            print(f"✓ Progress record created for {test_user.email} ({pair_id})")

        # 4. Verify meta.json loads correctly
        try:
            meta = content_service.get_meta(pair_id)
            months = meta.get("months", [])
            total_blocks = sum(len(m.get("blocks", [])) for m in months)
            total_acts = sum(
                len(b.get("activities", []))
                for m in months
                for b in m.get("blocks", [])
            )
            print(f"✓ hi-ja meta.json valid: {len(months)} months, {total_blocks} blocks, {total_acts} activities")
        except Exception as e:
            print(f"⚠ meta.json check failed: {e}")

        # 5. Verify all 144 JSON files exist
        files = content_service.list_pair_files(pair_id)
        print(f"✓ Content files on disk: {len(files)} JSON files")
        if len(files) < 144:
            missing = 144 - len(files)
            print(f"  ⚠ {missing} activity files missing (admin must create them)")

        db.commit()
        print("\n✅ Seeding complete!")
        print(f"\nLogin credentials:")
        print(f"  Admin:    {settings.ADMIN_EMAIL} / {settings.ADMIN_PASSWORD}")
        print(f"  Learner:  {test_email} / Test@1234")
        print(f"\nSCORE_THRESHOLD_OVERRIDE={settings.SCORE_THRESHOLD_OVERRIDE} (0=always pass for testing)")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
