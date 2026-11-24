"""Thin wrapper around our LLM provider.

Locally and in tests (LLM_FAKE=1, the default) it returns a fixed answer,
so nobody needs an API key to run the service.
"""

import json
import os


def complete(prompt: str, system: str | None = None) -> str:
    if os.environ.get("LLM_FAKE", "1") == "1":
        return json.dumps(
            {
                "category": "refund",
                "order_number": "A-10023",
                "urgency": "high",
                "refund_amount": 49.90,
            }
        )
    raise NotImplementedError("The real provider is only configured in production.")
