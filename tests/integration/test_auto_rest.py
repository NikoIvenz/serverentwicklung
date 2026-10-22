"""Integration tests for the REST interface (requires the running PostgreSQL)."""

from collections.abc import Iterator
from http import HTTPStatus
from typing import Any, Final
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from auto.fastapi_app import app

pytestmark = [pytest.mark.rest]

EXISTING_ID: Final = 30
"""Auto from the CSV test data (MERCEDES-BENZ)."""


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def _new_auto() -> dict[str, Any]:
    return {
        "fin": f"TST{uuid4().hex[:14].upper()}",
        "marke": "TESLA",
        "modell": "Model 3",
        "farbe": "W",
        "kennzeichen": {"kombination": "KA-TS 123", "ausstellungsdatum": "2026-02-01"},
        "wartungen": [{"beschreibung": "Reifenwechsel", "kosten": "79.90"}],
    }


@pytest.fixture
def created_auto(client: TestClient) -> Iterator[tuple[str, dict[str, Any]]]:
    """Create an Auto and delete it afterwards; yields its URL and payload."""
    payload = _new_auto()
    response = client.post("/rest", json=payload)
    assert response.status_code == HTTPStatus.CREATED
    location = response.headers["Location"]
    yield location, payload
    client.delete(location)


@pytest.mark.get_request
def test_get_by_id(client: TestClient) -> None:
    response = client.get(f"/rest/{EXISTING_ID}")

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["id"] == EXISTING_ID
    assert body["marke"] == "MERCEDES-BENZ"
    assert body["kennzeichen"]["kombination"] == "K-LM 3000"
    assert body["wartungen"]
    assert response.headers["ETag"].strip('"').isdecimal()


@pytest.mark.get_request
def test_get_if_none_match(client: TestClient) -> None:
    etag = client.get(f"/rest/{EXISTING_ID}").headers["ETag"]

    response = client.get(f"/rest/{EXISTING_ID}", headers={"If-None-Match": etag})

    assert response.status_code == HTTPStatus.NOT_MODIFIED
    assert not response.content


@pytest.mark.get_request
def test_get_not_found(client: TestClient) -> None:
    response = client.get("/rest/999999")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.headers["content-type"] == "application/problem+json"


@pytest.mark.get_request
def test_get_by_marke(client: TestClient) -> None:
    response = client.get("/rest", params={"marke": "bmw", "size": 10})

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["total_elements"] >= 1
    assert all("BMW" in auto["marke"] for auto in body["content"])


@pytest.mark.post_request
def test_post_valid(client: TestClient) -> None:
    response = client.post("/rest", json=_new_auto())

    assert response.status_code == HTTPStatus.CREATED
    location = response.headers["Location"]
    assert location.startswith("/rest/")
    assert location.removeprefix("/rest/").isdecimal()
    client.delete(location)


@pytest.mark.post_request
def test_post_invalid(client: TestClient) -> None:
    payload = _new_auto()
    payload["fin"] = "too-short"
    payload["kennzeichen"]["kombination"] = "not a plate"
    payload["wartungen"][0]["kosten"] = "-1"

    response = client.post("/rest", json=payload)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.post_request
def test_post_fin_exists(
    client: TestClient,
    created_auto: tuple[str, dict[str, Any]],
) -> None:
    _, payload = created_auto

    response = client.post("/rest", json=payload)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.headers["content-type"] == "application/problem+json"


@pytest.mark.put_request
def test_put_optimistic_locking(
    client: TestClient,
    created_auto: tuple[str, dict[str, Any]],
) -> None:
    location, payload = created_auto
    etag = client.get(location).headers["ETag"]
    changed = {key: payload[key] for key in ("fin", "marke", "modell", "farbe")}
    changed["modell"] = "Model Y"

    response = client.put(location, json=changed, headers={"If-Match": etag})

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.headers["ETag"] != etag
    assert client.get(location).json()["modell"] == "Model Y"

    stale = client.put(location, json=changed, headers={"If-Match": etag})

    assert stale.status_code == HTTPStatus.PRECONDITION_FAILED
    assert stale.headers["content-type"] == "application/problem+json"


@pytest.mark.put_request
def test_put_if_match_missing_or_invalid(
    client: TestClient,
    created_auto: tuple[str, dict[str, Any]],
) -> None:
    location, payload = created_auto
    changed = {key: payload[key] for key in ("fin", "marke", "modell", "farbe")}

    missing = client.put(location, json=changed)
    invalid = client.put(location, json=changed, headers={"If-Match": '"abc"'})

    assert missing.status_code == HTTPStatus.PRECONDITION_REQUIRED
    assert invalid.status_code == HTTPStatus.PRECONDITION_FAILED


@pytest.mark.delete_request
def test_delete(client: TestClient) -> None:
    location = client.post("/rest", json=_new_auto()).headers["Location"]

    assert client.delete(location).status_code == HTTPStatus.NO_CONTENT
    assert client.get(location).status_code == HTTPStatus.NOT_FOUND
