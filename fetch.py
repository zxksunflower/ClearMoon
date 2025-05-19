import httpx
import os
import ssl
import asyncio
from pydantic_settings import BaseSettings


def join_path(file_name: str) -> str:
    base_path = os.path.dirname(os.path.abspath(__file__))
    ssl_file_path = os.path.join(base_path, 'ssl_file')
    return os.path.join(ssl_file_path, file_name)


class Settings(BaseSettings):
    is_ssl_two_way: bool = False
    ca_crt_path: str = join_path('ca.crt')
    client_crt_path: str = join_path('client.crt')
    client_key_path: str = join_path('client.key')


settings = Settings()


class HTTPXClient:
    def __init__(self):
        """
        初始化HTTPX客户端
        """
        self.ssl_context = self._create_ssl_context()

    def _create_ssl_context(self) -> ssl.SSLContext:
        """创建SSL上下文"""
        ssl_context = ssl.create_default_context(cafile=settings.ca_crt_path)

        if settings.is_ssl_two_way:
            ssl_context.load_cert_chain(settings.client_crt_path, settings.client_key_path)

        return ssl_context

    async def async_get(self, url: str, **kwargs) -> dict:
        """异步GET请求"""
        async with httpx.AsyncClient(verify=self.ssl_context) as client:
            try:
                response = await client.get(url, **kwargs)
                return response.json()
            except httpx.HTTPError as e:
                print(f"请求错误: {e}")
                return {"error": str(e)}


async def main():
    client = HTTPXClient()
    result = await client.async_get("https://localhost:8443")
    print("result:", result)


if __name__ == "__main__":
    asyncio.run(main())
