import httpx
from pydantic import SecretStr

SPTRANS_BASE_URL = "https://api.olhovivo.sptrans.com.br/v2.1"

class SPTransError(Exception):
    """Erro genérico durante comunicação com a API do SPTrans."""

class SPTransAuthenticationError(SPTransError):
    """Erro específico com a API do SPTrans."""

class SPTransClient:
    def __init__(
            self, 
            token: SecretStr,
            transport: httpx.AsyncBaseTransport | None = None, 
        ) -> None:
            self.token = token
            self.client = httpx.AsyncClient(
                base_url=SPTRANS_BASE_URL,
                timeout=10.0,
                transport=transport,
            )

    async def authenticate(self) -> bool:
        try:
            response = await self.client.post(
                "Login/Autenticar",
                params={
                    "token": self.token.get_secret_value(),
                },
            )
        except httpx.RequestError:
            raise SPTransError(
                "Erro de comunicação com a API do SPTrans."
            ) from None
        
        if response.is_error:
            raise SPTransError(
                f"A API da SPTrans retornou HTTP {response.status_code}."
            )

        try:
            authenticated = response.json()
        except ValueError:
            raise SPTransError(
                "A API da SPTrans retornou uma resposta inválida."
            ) from None

        if authenticated is not True:
            raise SPTransAuthenticationError(
                "A SPTrans recusou a autenticação."
            )

        return True

    async def close(self) -> None:
        await self.client.aclose()

    async def __aenter__(self) -> "SPTransClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()
