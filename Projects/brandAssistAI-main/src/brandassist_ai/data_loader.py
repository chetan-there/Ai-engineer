from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

from .models import ImageLabel, KnowledgeDoc, Order, Product, WarrantyRegistration, WarrantyRule


ROOT = Path(__file__).resolve().parents[2]
BRAND_DATA = ROOT / "data" / "brand"
EVAL_DATA = ROOT / "data" / "evals"
BRAND_DB = ROOT / "data" / "brandassist.db"


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _db_available() -> bool:
    return BRAND_DB.exists()


def _fetch_all(sql: str) -> list[sqlite3.Row]:
    with sqlite3.connect(BRAND_DB) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(sql).fetchall()


def load_products() -> list[Product]:
    if _db_available():
        rows = _fetch_all("SELECT product_id, name, category, aliases_json, tags_json FROM products ORDER BY product_id")
        return [
            Product(
                id=row["product_id"],
                name=row["name"],
                category=row["category"],
                aliases=json.loads(row["aliases_json"]),
                tags=json.loads(row["tags_json"]),
            )
            for row in rows
        ]
    return [Product(**item) for item in _load_json(BRAND_DATA / "products.json")]


def load_knowledge_docs() -> list[KnowledgeDoc]:
    if _db_available():
        rows = _fetch_all("SELECT doc_id, product_id, kind, title, text FROM knowledge_documents ORDER BY doc_id")
        return [
            KnowledgeDoc(
                id=row["doc_id"],
                product_id=row["product_id"],
                kind=row["kind"],
                title=row["title"],
                text=row["text"],
            )
            for row in rows
        ]
    return [KnowledgeDoc(**item) for item in _load_json(BRAND_DATA / "knowledge_base.json")]


def load_orders() -> list[Order]:
    if _db_available():
        rows = _fetch_all("SELECT order_id, customer_id, product_id, status, delivery_eta, purchase_date FROM orders ORDER BY order_id")
        return [
            Order(
                order_id=row["order_id"],
                customer_id=row["customer_id"],
                product_id=row["product_id"],
                status=row["status"],
                delivery_eta=row["delivery_eta"],
                purchase_date=row["purchase_date"],
            )
            for row in rows
        ]
    return [Order(**item) for item in _load_json(BRAND_DATA / "orders.json")]


def load_warranties() -> list[WarrantyRule]:
    if _db_available():
        rows = _fetch_all("SELECT product_id, months, requires_order FROM warranty_policies ORDER BY product_id")
        return [
            WarrantyRule(
                product_id=row["product_id"],
                months=int(row["months"]),
                requires_order=bool(row["requires_order"]),
            )
            for row in rows
        ]
    return [WarrantyRule(**item) for item in _load_json(BRAND_DATA / "warranties.json")]


def load_warranty_registrations() -> list[WarrantyRegistration]:
    if _db_available():
        rows = _fetch_all(
            """
            SELECT registration_id, customer_id, product_id, serial_number, order_id,
                   registered_at, warranty_start_date, warranty_end_date, status
            FROM warranty_registrations
            ORDER BY registration_id
            """
        )
        return [
            WarrantyRegistration(
                registration_id=row["registration_id"],
                customer_id=row["customer_id"],
                product_id=row["product_id"],
                serial_number=row["serial_number"],
                order_id=row["order_id"],
                registered_at=row["registered_at"],
                warranty_start_date=row["warranty_start_date"],
                warranty_end_date=row["warranty_end_date"],
                status=row["status"],
            )
            for row in rows
        ]
    path = BRAND_DATA / "warranty_registrations.json"
    if not path.exists():
        return []
    return [WarrantyRegistration(**item) for item in _load_json(path)]


def load_image_labels() -> list[ImageLabel]:
    return [ImageLabel(**item) for item in _load_json(BRAND_DATA / "image_labels.json")]


def load_golden_cases() -> list[dict[str, Any]]:
    return _load_json(EVAL_DATA / "golden_cases.json")
