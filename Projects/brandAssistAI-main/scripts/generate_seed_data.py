from __future__ import annotations

import argparse
import json
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_SQL = ROOT / "db" / "schema.sql"


PRODUCT_BLUEPRINTS = [
    ("nimbus-ac-1500", "NimbusCool AC 1500", "climate", ["ac", "air conditioner", "split ac"], ["cooling", "filter"]),
    ("toastpro-2s", "ToastPro 2 Slice", "kitchen", ["toaster", "bread toaster"], ["heating", "crumb"]),
    ("thermoboil-k1", "ThermoBoil Kettle K1", "kitchen", ["kettle", "electric kettle"], ["boil", "heating"]),
    ("microchef-20l", "MicroChef 20L", "kitchen", ["microwave"], ["heating", "turntable"]),
    ("aeropure-220", "AeroPure 220", "climate", ["air purifier"], ["filter", "airflow"]),
    ("dustmate-v10", "DustMate V10", "homecare", ["vacuum"], ["suction", "filter"]),
    ("wavehub-r5", "WaveHub Router R5", "networking", ["router", "wifi router"], ["wifi", "network"]),
    ("sonicbar-s20", "SonicBar S20", "audio", ["soundbar"], ["audio", "bluetooth"]),
    ("breezefan-f7", "BreezeFan F7", "climate", ["fan", "table fan"], ["airflow", "motor"]),
    ("blendgo-b2", "BlendGo B2", "kitchen", ["blender"], ["blade", "motor"]),
]


def _date_string(days_ago: int) -> str:
    return (date.today() - timedelta(days=days_ago)).isoformat()


def _serial(prefix: str, idx: int) -> str:
    return f"{prefix.upper()}-{10000 + idx}"


def generate(args: argparse.Namespace) -> None:
    random.seed(args.seed)
    db_path = Path(args.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))
        cur = conn.cursor()

        products = []
        for idx in range(args.products):
            base = PRODUCT_BLUEPRINTS[idx % len(PRODUCT_BLUEPRINTS)]
            product_id = f"{base[0]}-{idx+1:02d}" if idx >= len(PRODUCT_BLUEPRINTS) else base[0]
            products.append(
                {
                    "id": product_id,
                    "name": f"{base[1]} {idx+1}" if idx >= len(PRODUCT_BLUEPRINTS) else base[1],
                    "category": base[2],
                    "aliases": base[3],
                    "tags": base[4],
                }
            )
        cur.executemany(
            "INSERT OR REPLACE INTO products(product_id,name,category,aliases_json,tags_json) VALUES(?,?,?,?,?)",
            [(p["id"], p["name"], p["category"], json.dumps(p["aliases"]), json.dumps(p["tags"])) for p in products],
        )

        customers = [
            {
                "id": f"CUST-{i+1:03d}",
                "name": f"Customer {i+1}",
                "email": f"customer{i+1}@demo.example",
                "country": random.choice(["IN", "US", "UK", "DE"]),
            }
            for i in range(args.customers)
        ]
        cur.executemany(
            "INSERT OR REPLACE INTO customers(customer_id,name,email,country) VALUES(?,?,?,?)",
            [(c["id"], c["name"], c["email"], c["country"]) for c in customers],
        )

        orders = []
        for i in range(args.orders):
            product = random.choice(products)
            customer = random.choice(customers)
            order_id = f"A{2000+i}"
            days_ago = random.randint(5, 400)
            purchase_date = _date_string(days_ago)
            delivery_eta = (date.fromisoformat(purchase_date) + timedelta(days=random.randint(2, 9))).isoformat()
            status = random.choice(["processing", "shipped", "delivered", "returned"])
            orders.append(
                {
                    "order_id": order_id,
                    "customer_id": customer["id"],
                    "product_id": product["id"],
                    "status": status,
                    "delivery_eta": delivery_eta,
                    "purchase_date": purchase_date,
                }
            )
        cur.executemany(
            "INSERT OR REPLACE INTO orders(order_id,customer_id,product_id,status,delivery_eta,purchase_date) VALUES(?,?,?,?,?,?)",
            [(o["order_id"], o["customer_id"], o["product_id"], o["status"], o["delivery_eta"], o["purchase_date"]) for o in orders],
        )

        warranties = [{"product_id": p["id"], "months": random.choice([12, 18, 24]), "requires_order": 1} for p in products]
        cur.executemany(
            "INSERT OR REPLACE INTO warranty_policies(product_id,months,requires_order) VALUES(?,?,?)",
            [(w["product_id"], w["months"], w["requires_order"]) for w in warranties],
        )

        registrations = []
        for i in range(args.registrations):
            order = random.choice(orders)
            days_ago = random.randint(1, 200)
            start = _date_string(days_ago)
            months = next(w["months"] for w in warranties if w["product_id"] == order["product_id"])
            end = (date.fromisoformat(start) + timedelta(days=30 * months)).isoformat()
            reg = {
                "registration_id": f"REG-{3000+i}",
                "customer_id": order["customer_id"],
                "product_id": order["product_id"],
                "serial_number": _serial(order["product_id"][:4], i),
                "order_id": order["order_id"],
                "registered_at": start,
                "warranty_start_date": start,
                "warranty_end_date": end,
                "status": "active",
            }
            registrations.append(reg)
        cur.executemany(
            "INSERT OR REPLACE INTO warranty_registrations(registration_id,customer_id,product_id,serial_number,order_id,registered_at,warranty_start_date,warranty_end_date,status) VALUES(?,?,?,?,?,?,?,?,?)",
            [(r["registration_id"], r["customer_id"], r["product_id"], r["serial_number"], r["order_id"], r["registered_at"], r["warranty_start_date"], r["warranty_end_date"], r["status"]) for r in registrations],
        )

        intents = ["setup", "troubleshooting", "warranty", "order_status", "return_policy", "general_support"]
        support_cases = []
        for i in range(args.support_cases):
            customer = random.choice(customers)
            order = random.choice(orders)
            intent = random.choice(intents)
            outcome = random.choice(["resolved", "escalated", "clarify"])
            support_cases.append(
                {
                    "case_id": f"CASE-{5000+i}",
                    "customer_id": customer["id"],
                    "product_id": order["product_id"],
                    "order_id": order["order_id"],
                    "intent": intent,
                    "status": "open" if outcome != "resolved" else "closed",
                    "summary": f"{intent} support request for {order['product_id']}",
                    "escalated": 1 if outcome == "escalated" else 0,
                    "outcome": outcome,
                    "created_at": _date_string(random.randint(0, 60)),
                }
            )
        cur.executemany(
            "INSERT OR REPLACE INTO support_cases(case_id,customer_id,product_id,order_id,intent,status,summary,escalated,outcome,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
            [(c["case_id"], c["customer_id"], c["product_id"], c["order_id"], c["intent"], c["status"], c["summary"], c["escalated"], c["outcome"], c["created_at"]) for c in support_cases],
        )

        docs = []
        for product in products:
            docs.extend(
                [
                    {
                        "doc_id": f"manual-{product['id']}",
                        "product_id": product["id"],
                        "kind": "manual",
                        "title": f"{product['name']} quick setup",
                        "text": f"Setup {product['name']} on a stable surface, verify power, and complete first-run diagnostics.",
                    },
                    {
                        "doc_id": f"troubleshoot-{product['id']}",
                        "product_id": product["id"],
                        "kind": "troubleshooting",
                        "title": f"{product['name']} common troubleshooting",
                        "text": f"If {product['name']} is not working, check cleaning, filter state, firmware reset, and safe operating range.",
                    },
                ]
            )
        docs.append(
            {
                "doc_id": "policy-warranty-standard",
                "product_id": None,
                "kind": "policy",
                "title": "Standard warranty policy",
                "text": "Products include limited warranty for manufacturing defects and exclude misuse or unauthorized repairs.",
            }
        )
        cur.executemany(
            "INSERT OR REPLACE INTO knowledge_documents(doc_id,product_id,kind,title,text,source_url,updated_at) VALUES(?,?,?,?,?,?,?)",
            [(d["doc_id"], d["product_id"], d["kind"], d["title"], d["text"], None, date.today().isoformat()) for d in docs],
        )

        conn.commit()

    export_dir = Path(args.export_json_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    (export_dir / "products.json").write_text(json.dumps(products, indent=2), encoding="utf-8")
    (export_dir / "orders.json").write_text(json.dumps(orders, indent=2), encoding="utf-8")
    (export_dir / "warranties.json").write_text(json.dumps(warranties, indent=2), encoding="utf-8")
    (export_dir / "warranty_registrations.json").write_text(json.dumps(registrations, indent=2), encoding="utf-8")
    (export_dir / "support_cases.json").write_text(json.dumps(support_cases, indent=2), encoding="utf-8")
    (export_dir / "knowledge_base.json").write_text(
        json.dumps(
            [{"id": d["doc_id"], "product_id": d["product_id"], "kind": d["kind"], "title": d["title"], "text": d["text"]} for d in docs],
            indent=2,
        ),
        encoding="utf-8",
    )
    (export_dir / "customers.json").write_text(json.dumps(customers, indent=2), encoding="utf-8")

    print(f"Generated SQLite seed at {db_path}")
    print(f"Exported JSON snapshots at {export_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate pseudonymized synthetic seed data.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--products", type=int, default=30)
    parser.add_argument("--customers", type=int, default=100)
    parser.add_argument("--orders", type=int, default=100)
    parser.add_argument("--registrations", type=int, default=60)
    parser.add_argument("--support-cases", type=int, default=100)
    parser.add_argument("--db-path", default=str(ROOT / "data" / "brandassist.db"))
    parser.add_argument("--export-json-dir", default=str(ROOT / "data" / "brand"))
    generate(parser.parse_args())


if __name__ == "__main__":
    main()
