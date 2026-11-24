def fake_order_api(method, path, payload=None):
    return {"id": "A-10023", "total": 49.90}


def test_process_email(client, monkeypatch):
    monkeypatch.setattr("app.emails.call_order_api", fake_order_api)

    resp = client.post(
        "/emails",
        json={
            "sender": "anna@example.com",
            "subject": "Erstattung",
            "body": "Hallo, ich möchte Bestellung A-10023 zurückgeben.",
        },
    )

    assert resp.status_code == 200
    assert resp.json()["category"] == "refund"


def test_list_emails(client, monkeypatch):
    monkeypatch.setattr("app.emails.call_order_api", fake_order_api)
    client.post(
        "/emails",
        json={"sender": "anna@example.com", "subject": "Hallo", "body": "Test"},
    )

    resp = client.get("/emails")

    assert resp.status_code == 200
    assert resp.json()[0]["customer"]["email"] == "anna@example.com"
