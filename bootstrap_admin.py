"""Prepare Mealie's database and secure its first admin before the server starts.

Mealie seeds its first admin as changeme@example.com / MyPassword and shows those
credentials on the login page until the email is changed. On a public Railway URL
that is a known login, so this script:

* waits for the database (Railway starts services in no fixed order),
* runs Mealie's own migrations and first-run seeding (mealie.db.init_db.main),
* changes the seeded admin's email and password to MEALIE_ADMIN_EMAIL and
  MEALIE_ADMIN_PASSWORD, but only while the row still has the shipped email and
  password. Changes you make later in the UI are never overwritten.
"""

import os
import sys
import time

from sqlalchemy import create_engine, text

from mealie.core.config import get_app_settings

DEFAULT_PASSWORD = "MyPassword"


def log(msg: str) -> None:
    print(f"[railway-bootstrap] {msg}", flush=True)


def wait_for_db(url: str, timeout: int = 180) -> None:
    deadline = time.time() + timeout
    while True:
        engine = create_engine(url)
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception as exc:  # noqa: BLE001
            if time.time() > deadline:
                log(f"database still unreachable after {timeout}s: {exc.__class__.__name__}")
                raise
            log("waiting for the database...")
            time.sleep(3)
        finally:
            engine.dispose()


def main() -> None:
    settings = get_app_settings()
    password = os.environ.get("MEALIE_ADMIN_PASSWORD", "")
    email = os.environ.get("MEALIE_ADMIN_EMAIL", "").strip().lower() or "admin@example.com"

    if len(password) < 8:
        log("MEALIE_ADMIN_PASSWORD must be set (8+ characters); refusing to start with Mealie's default login.")
        sys.exit(1)

    wait_for_db(settings.DB_URL)

    from mealie.db import init_db

    init_db.main()

    from mealie.core.security.hasher import get_hasher
    from mealie.db.db_setup import session_context
    from mealie.db.models.users.users import User

    hasher = get_hasher()
    default_email = settings._DEFAULT_EMAIL.strip().lower()
    with session_context() as session:
        user = session.query(User).filter(User.email == default_email).one_or_none()
        if user is None:
            log("first admin already configured; nothing to do")
            return
        if not user.password or not hasher.verify(DEFAULT_PASSWORD, user.password):
            log("default admin row has a changed password; leaving it alone")
            return
        if email != default_email and session.query(User).filter(User.email == email).count():
            log(f"another user already uses {email}; set MEALIE_ADMIN_EMAIL to a free address")
            sys.exit(1)
        user.email = email
        user.password = hasher.hash(password)
        session.commit()
        log(f"first admin set: username 'admin', email {email}, password from MEALIE_ADMIN_PASSWORD")


if __name__ == "__main__":
    main()
