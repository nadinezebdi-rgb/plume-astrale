#!/usr/bin/env python3
"""Quick non-regression smoke test for frontend/backend compatibility routes.

Usage:
  python tests/smoke_api_compat.py
    python tests/smoke_api_compat.py --suite quick
    python tests/smoke_api_compat.py --suite pdf

This script runs fully local using FastAPI TestClient and mocks Stripe-dependent
legacy checkout aliases so no external checkout call is required.
"""

from __future__ import annotations

import os
import sys
import argparse
from typing import Any


def _set_defaults() -> None:
    os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
    os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test_service_role_key")
    os.environ.setdefault("SUPABASE_ANON_KEY", "test_anon_key")
    os.environ.setdefault("SUPABASE_JWT_SECRET", "test_jwt_secret")
    os.environ.setdefault("STRIPE_API_KEY", "sk_test_dummy")
    os.environ.setdefault("OPENAI_API_KEY", "test_openai_key")


def _ok(label: str) -> None:
    print(f"[OK]   {label}")


def _fail(label: str, detail: str) -> None:
    print(f"[FAIL] {label}: {detail}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run API compatibility smoke tests")
    parser.add_argument(
        "--suite",
        choices=["all", "quick", "pdf"],
        default="all",
        help="Subset of smoke tests to run",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    _set_defaults()
    sys.path.insert(0, "backend")

    try:
        import server  # type: ignore
        from fastapi.testclient import TestClient
    except Exception as exc:
        _fail("imports", str(exc))
        return 2

    # Mock Stripe-dependent aliases so this smoke test can run offline.
    async def fake_legacy_checkout_create(payload: Any, http_request: Any) -> dict:
        return {
            "url": "https://checkout.stripe.com/c/test_dummy",
            "session_id": "cs_test_dummy_123",
        }

    async def fake_legacy_checkout_status(session_id: str) -> dict:
        return {
            "status": "complete",
            "payment_status": "paid",
            "session_id": session_id,
        }

    server.legacy_checkout_create = fake_legacy_checkout_create
    server.legacy_checkout_status = fake_legacy_checkout_status

    client = TestClient(server.app)
    failed = False
    run_quick = args.suite in {"all", "quick"}
    run_pdf = args.suite in {"all", "pdf"}

    user_data = {
        "prenom": "Nadine",
        "dateNaissance": "1990-06-15",
        "heureNaissance": "12:00",
        "ville": "Paris",
        "pays": "France",
    }

    prem_data = {"prenom": "Nadine", "steps": {}}

    if run_quick:
        try:
            with open("frontend/src/pages/Premium.js", "r", encoding="utf-8") as f:
                premium_js = f.read()
            with open("frontend/src/App.js", "r", encoding="utf-8") as f:
                app_js = f.read()
            route_ok = (
                "/mon-compte" in premium_js
                and "/mon-profil" not in premium_js
                and 'path="/mon-compte"' in app_js
            )
            if route_ok:
                _ok("premium route /mon-compte")
            else:
                failed = True
                _fail("premium route /mon-compte", "route wiring mismatch")
        except Exception as exc:
            failed = True
            _fail("premium route /mon-compte", str(exc))

        compat_payload = {
            "person1": {
                "first_name": "Alice",
                "day": 10,
                "month": 5,
                "year": 1990,
                "hour": 10,
                "minute": 30,
            },
            "person2": {
                "first_name": "Bob",
                "day": 15,
                "month": 8,
                "year": 1989,
                "hour": 14,
                "minute": 0,
            },
            "question": "Sommes-nous compatibles ?",
        }
        r = client.post("/api/compatibility/generate", json=compat_payload)
        if r.status_code == 200 and str(r.json().get("pdf_url", "")).startswith(
            "data:application/pdf;base64,"
        ):
            _ok("/api/compatibility/generate")
        else:
            failed = True
            _fail(
                "/api/compatibility/generate",
                f"status={r.status_code} body={r.text[:160]}",
            )

        r = client.post("/api/share/generate-card", json={"user_data": user_data})
        if r.status_code == 200 and "image/png" in (r.headers.get("content-type") or ""):
            _ok("/api/share/generate-card")
        else:
            failed = True
            _fail(
                "/api/share/generate-card",
                f"status={r.status_code} content-type={r.headers.get('content-type')}",
            )

        r = client.post(
            "/api/premium/generate",
            json={
                "prenom": "Nadine",
                "dateNaissance": "1990-06-15",
                "heureNaissance": "12:00",
                "ville": "Paris",
            },
        )
        if r.status_code == 200 and r.json().get("success"):
            _ok("/api/premium/generate")
            prem_data = r.json().get("data") or {}
        else:
            failed = True
            _fail("/api/premium/generate", f"status={r.status_code} body={r.text[:160]}")

        r = client.post(
            "/api/order/book",
            json={
                "product_id": "livre",
                "origin_url": "https://plume-astrale.fr",
                "user_email": "test@example.com",
                "user_data": {"prenom": "Nadine"},
            },
        )
        if r.status_code == 200 and r.json().get("session_id"):
            _ok("/api/order/book")
            sid = r.json().get("session_id")
        else:
            failed = True
            sid = "cs_test_dummy_123"
            _fail("/api/order/book", f"status={r.status_code} body={r.text[:160]}")

        r = client.get(f"/api/order/book/{sid}")
        if r.status_code == 200 and r.json().get("payment_status"):
            _ok("/api/order/book/{session_id}")
        else:
            failed = True
            _fail(
                "/api/order/book/{session_id}",
                f"status={r.status_code} body={r.text[:160]}",
            )

    if run_pdf:
        if not prem_data.get("steps"):
            r = client.post(
                "/api/premium/generate",
                json={
                    "prenom": "Nadine",
                    "dateNaissance": "1990-06-15",
                    "heureNaissance": "12:00",
                    "ville": "Paris",
                },
            )
            if r.status_code == 200 and r.json().get("success"):
                prem_data = r.json().get("data") or prem_data
            else:
                failed = True
                _fail("/api/premium/generate (for pdf suite)", f"status={r.status_code} body={r.text[:160]}")

        r = client.post("/api/pdf/generate", json={"user_data": user_data})
        if r.status_code == 200 and "application/pdf" in (r.headers.get("content-type") or ""):
            _ok("/api/pdf/generate")
        else:
            failed = True
            _fail(
                "/api/pdf/generate",
                f"status={r.status_code} content-type={r.headers.get('content-type')}",
            )

        r = client.post("/api/premium/pdf", json={"data": prem_data})
        if r.status_code == 200 and "application/pdf" in (r.headers.get("content-type") or ""):
            _ok("/api/premium/pdf")
        else:
            failed = True
            _fail(
                "/api/premium/pdf",
                f"status={r.status_code} content-type={r.headers.get('content-type')}",
            )

        r = client.post(
            "/api/tarologie/pdf",
            json={"prenom": "Nadine", "date_naissance": "1990-06-15"},
        )
        if r.status_code == 200 and "application/pdf" in (r.headers.get("content-type") or ""):
            _ok("/api/tarologie/pdf")
        else:
            failed = True
            _fail(
                "/api/tarologie/pdf",
                f"status={r.status_code} content-type={r.headers.get('content-type')}",
            )

    if failed:
        print(f"\nSmoke test ({args.suite}): FAILED")
        return 1

    print(f"\nSmoke test ({args.suite}): PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
