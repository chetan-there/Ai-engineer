from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def _count(conn: sqlite3.Connection, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def validate(db_path: Path) -> None:
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    with sqlite3.connect(db_path) as conn:
        counts = {
            "products": _count(conn, "products"),
            "customers": _count(conn, "customers"),
            "orders": _count(conn, "orders"),
            "warranty_policies": _count(conn, "warranty_policies"),
            "warranty_registrations": _count(conn, "warranty_registrations"),
            "support_cases": _count(conn, "support_cases"),
            "knowledge_documents": _count(conn, "knowledge_documents"),
        }

        broken_orders = conn.execute(
            """
            SELECT COUNT(*)
            FROM orders o
            LEFT JOIN customers c ON c.customer_id = o.customer_id
            LEFT JOIN products p ON p.product_id = o.product_id
            WHERE c.customer_id IS NULL OR p.product_id IS NULL
            """
        ).fetchone()[0]
        broken_regs = conn.execute(
            """
            SELECT COUNT(*)
            FROM warranty_registrations w
            LEFT JOIN products p ON p.product_id = w.product_id
            LEFT JOIN customers c ON c.customer_id = w.customer_id
            WHERE p.product_id IS NULL OR c.customer_id IS NULL
            """
        ).fetchone()[0]

    print("Row counts:", counts)
    if broken_orders or broken_regs:
        raise RuntimeError(f"Integrity validation failed: broken_orders={broken_orders}, broken_registrations={broken_regs}")
    print("Validation passed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate generated SQLite seed data.")
    parser.add_argument("--db-path", default="data/brandassist.db")
    args = parser.parse_args()
    validate(Path(args.db_path))


if __name__ == "__main__":
    main()
