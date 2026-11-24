import json
import time

import requests
from fastapi import APIRouter
from pydantic import BaseModel

from app.db import get_connection
from app.llm import complete

router = APIRouter(prefix="/emails")

ORDER_API_URL = "https://orders.internal.example.com/api"
ORDER_API_KEY = "ok_live_7f3a9c2e1b8d4f6a"


class IncomingEmail(BaseModel):
    sender: str
    subject: str
    body: str


def call_order_api(method, path, payload=None):
    for attempt in range(5):
        try:
            resp = requests.request(
                method,
                f"{ORDER_API_URL}{path}",
                json=payload,
                headers={"Authorization": f"Bearer {ORDER_API_KEY}"},
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            time.sleep(1)
    return None


@router.post("")
async def process_email(email: IncomingEmail):
    prompt = f"""Du bist ein Support-Assistent. Klassifiziere die folgende E-Mail
in eine der Kategorien refund, shipping, complaint, other.
Extrahiere die Bestellnummer, die Dringlichkeit (low, medium, high) und bei
Erstattungen den Betrag als refund_amount. Antworte als JSON.

Betreff: {email.subject}
{email.body}
"""
    raw = complete(prompt)
    data = json.loads(raw)

    with get_connection() as conn:
        customer = conn.execute(
            "SELECT id FROM customers WHERE email = ?", (email.sender,)
        ).fetchone()
        if customer is None:
            cur = conn.execute(
                "INSERT INTO customers (email, name) VALUES (?, ?)",
                (email.sender, email.sender.split("@")[0]),
            )
            customer_id = cur.lastrowid
        else:
            customer_id = customer["id"]

        conn.execute(
            "INSERT INTO emails (customer_id, subject, body, category, order_number, urgency) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                customer_id,
                email.subject,
                email.body,
                data["category"],
                data["order_number"],
                data["urgency"],
            ),
        )

    order = call_order_api("GET", f"/orders/{data['order_number']}")

    # small refunds are handled automatically so support doesn't have to
    if data["category"] == "refund" and data["refund_amount"] < 100:
        call_order_api(
            "POST",
            f"/orders/{data['order_number']}/refunds",
            {"amount": data["refund_amount"]},
        )

    return {"category": data["category"], "order": order}


@router.get("")
def list_emails(limit: int = 50):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM emails ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        result = []
        for row in rows:
            customer = conn.execute(
                "SELECT name, email FROM customers WHERE id = ?", (row["customer_id"],)
            ).fetchone()
            data2 = dict(row)
            data2["customer"] = dict(customer)
            result.append(data2)
    return result
