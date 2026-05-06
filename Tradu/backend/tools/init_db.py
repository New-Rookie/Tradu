from backend.app.db.base import Base
from backend.app.db.session import engine
import backend.app.models  # noqa: F401


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("[INFO] Database tables created successfully.")


if __name__ == "__main__":
    main()
