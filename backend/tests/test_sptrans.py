import httpx
import pytest

from pydantic import SecretStr

from app.integrations.sptrans import (
    SPTransAuthenticationError,
    SPTransClient,
    SPTransError,
)


@pytest.mark.asyncio
async def test_authenticate_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path.endswith("/Login/Autenticar")
        assert request.url.params["token"] == "fake-token"

        return httpx.Response(200, json=True)

    transport = httpx.MockTransport(handler)

    async with SPTransClient(
        SecretStr("fake-token"),
        transport=transport,
    ) as client:
        result = await client.authenticate()

    assert result is True


@pytest.mark.asyncio
async def test_authenticate_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=False)

    transport = httpx.MockTransport(handler)

    async with SPTransClient(
        SecretStr("invalid-token"),
        transport=transport,
    ) as client:
        with pytest.raises(SPTransAuthenticationError):
            await client.authenticate()


@pytest.mark.asyncio
async def test_authenticate_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    transport = httpx.MockTransport(handler)

    async with SPTransClient(
        SecretStr("fake-token"),
        transport=transport,
    ) as client:
        with pytest.raises(
            SPTransError,
            match="HTTP 503",
        ):
            await client.authenticate()


@pytest.mark.asyncio
async def test_authenticate_invalid_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text="resposta quebrada",
        )

    transport = httpx.MockTransport(handler)

    async with SPTransClient(
        SecretStr("fake-token"),
        transport=transport,
    ) as client:
        with pytest.raises(
            SPTransError,
            match="resposta inválida",
        ):
            await client.authenticate()


@pytest.mark.asyncio
async def test_authenticate_network_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(
            "Connection failed",
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with SPTransClient(
        SecretStr("fake-token"),
        transport=transport,
    ) as client:
        with pytest.raises(
            SPTransError,
            match="Erro de comunicação",
        ):
            await client.authenticate()