import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.db.models.user import User, UserType


def create_superadmin() -> None:
    print("\nICMS Super Admin Creation")
    print("=" * 28)

    username = input("Username: ").strip()
    email = input("Email: ").strip().lower()

    if not username:
        print("Error: Username cannot be empty.")
        return

    if not email:
        print("Error: Email cannot be empty.")
        return

    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm Password: ")

    if not password:
        print("Error: Password cannot be empty.")
        return

    if password != confirm_password:
        print("Error: Passwords do not match.")
        return

    with SessionLocal() as db:
        existing_username = db.scalar(
            select(User).where(User.username == username)
        )

        if existing_username:
            print(f"Error: Username '{username}' already exists.")
            return

        existing_email = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_email:
            print(f"Error: Email '{email}' is already registered.")
            return

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            user_type=UserType.SUPER_ADMIN,
            is_active=True,
            created_by=None,
            updated_by=None,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print("\nSuper Admin created successfully.")
        print(f"ID:       {user.id}")
        print(f"Username: {user.username}")
        print(f"Email:    {user.email}")
        print(f"Role:     {user.user_type.value}")


def main() -> None:
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m app.cli.main create-superadmin")
        return

    command = sys.argv[1]

    if command == "create-superadmin":
        create_superadmin()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()