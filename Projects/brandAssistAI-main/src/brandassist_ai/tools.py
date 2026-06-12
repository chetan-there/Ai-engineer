from __future__ import annotations

from datetime import date, timedelta
import re

from .models import Order, Product, WarrantyRegistration, WarrantyRule

SERIAL_RE = re.compile(r"[A-Z]{2,5}-[A-Z0-9]{4,10}", re.IGNORECASE)


class SupportTools:
    def __init__(
        self,
        products: list[Product],
        orders: list[Order],
        warranties: list[WarrantyRule],
        registrations: list[WarrantyRegistration] | None = None,
    ) -> None:
        self.products = {product.id: product for product in products}
        self.orders = {order.order_id.upper(): order for order in orders}
        self.orders_by_customer: dict[str, list[Order]] = {}
        for order in orders:
            if order.customer_id:
                key = order.customer_id.upper()
                self.orders_by_customer.setdefault(key, []).append(order)
        self.warranties = {rule.product_id: rule for rule in warranties}
        self.registrations = {reg.registration_id: reg for reg in (registrations or [])}
        self.registrations_by_serial = {
            (reg.product_id, reg.serial_number.upper()): reg for reg in (registrations or [])
        }
        self.tickets: list[dict] = []

    def product_lookup(self, product_id: str | None = None, query: str = "") -> dict:
        if product_id and product_id in self.products:
            product = self.products[product_id]
            return {
                "found": True,
                "product_id": product.id,
                "name": product.name,
                "category": product.category,
                "tags": product.tags,
            }

        query_lower = query.lower()
        for product in self.products.values():
            candidates = [product.name.lower(), product.id, *product.aliases, *product.tags]
            if any(candidate.lower() in query_lower for candidate in candidates):
                return {
                    "found": True,
                    "product_id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "tags": product.tags,
                }
        return {"found": False, "product_id": None}

    def order_lookup(self, order_id: str) -> dict:
        order = self.orders.get(order_id.upper())
        if not order:
            return {"found": False, "order_id": order_id}
        return {
            "found": True,
            "order_id": order.order_id,
            "product_id": order.product_id,
            "status": order.status,
            "delivery_eta": order.delivery_eta,
            "purchase_date": order.purchase_date,
        }

    def orders_by_customer_lookup(self, customer_id: str, limit: int = 5) -> dict:
        rows = self.orders_by_customer.get(customer_id.upper(), [])
        if not rows:
            return {"found": False, "customer_id": customer_id, "orders": []}
        orders = sorted(rows, key=lambda r: r.purchase_date, reverse=True)[:limit]
        return {
            "found": True,
            "customer_id": customer_id,
            "orders": [
                {
                    "order_id": order.order_id,
                    "product_id": order.product_id,
                    "status": order.status,
                    "delivery_eta": order.delivery_eta,
                    "purchase_date": order.purchase_date,
                }
                for order in orders
            ],
        }

    def warranty_check(self, product_id: str, order_id: str | None = None) -> dict:
        rule = self.warranties.get(product_id)
        if not rule:
            return {"eligible": False, "reason": "No warranty rule found."}
        if rule.requires_order and not order_id:
            return {
                "eligible": False,
                "reason": "Warranty review requires an order ID or proof of purchase.",
                "months": rule.months,
            }
        return {
            "eligible": True,
            "reason": f"Product has a {rule.months}-month limited warranty if damage is a manufacturing defect.",
            "months": rule.months,
            "checked_on": date.today().isoformat(),
        }

    def register_warranty(
        self,
        customer_id: str,
        product_id: str,
        serial_number: str,
        order_id: str | None = None,
    ) -> dict:
        if product_id not in self.products:
            return {"registered": False, "reason": "Unknown product.", "product_id": product_id}
        if not SERIAL_RE.fullmatch(serial_number):
            return {"registered": False, "reason": "Invalid serial number format.", "product_id": product_id}
        serial_key = (product_id, serial_number.upper())
        if serial_key in self.registrations_by_serial:
            existing = self.registrations_by_serial[serial_key]
            return {
                "registered": False,
                "reason": "Serial already registered.",
                "registration_id": existing.registration_id,
            }
        rule = self.warranties.get(product_id)
        coverage_months = rule.months if rule else 12
        start = date.today()
        end = start + timedelta(days=30 * coverage_months)
        registration_id = f"REG-{len(self.registrations) + 2001}"
        registration = WarrantyRegistration(
            registration_id=registration_id,
            customer_id=customer_id,
            product_id=product_id,
            serial_number=serial_number.upper(),
            order_id=order_id,
            registered_at=start.isoformat(),
            warranty_start_date=start.isoformat(),
            warranty_end_date=end.isoformat(),
            status="active",
        )
        self.registrations[registration.registration_id] = registration
        self.registrations_by_serial[serial_key] = registration
        return {
            "registered": True,
            "registration_id": registration.registration_id,
            "product_id": product_id,
            "customer_id": customer_id,
            "warranty_end_date": registration.warranty_end_date,
        }

    def create_ticket(self, summary: str, product_id: str | None = None) -> dict:
        ticket = {
            "ticket_id": f"TKT-{len(self.tickets) + 1001}",
            "product_id": product_id,
            "summary": summary,
            "status": "open",
        }
        self.tickets.append(ticket)
        return ticket
