"""Run the weather pipeline once.

Run from backend/:  uv run python -m scripts.run_pipeline --days 30
"""

import argparse
import logging

from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.services.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch recent weather into PostgreSQL."
    )
    parser.add_argument("--days", type=int, default=10, help="how many past days")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    with Session(get_engine()) as session:
        results = run_pipeline(session, days=args.days)
    for city, count in results.items():
        print(f"{city:15} {count:3} rows")


if __name__ == "__main__":
    main()
