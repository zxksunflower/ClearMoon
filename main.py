from fastapi import FastAPI
import ssl
import os
from pydantic_settings import BaseSettings


def join_path(file_name: str) -> str:
    base_path = os.path.dirname(os.path.abspath(__file__))
    ssl_file_path = os.path.join(base_path, 'ssl_file')
    return os.path.join(ssl_file_path, file_name)


class Settings(BaseSettings):
    is_ssl_two_way: bool = False
    ca_path: str = join_path('ca.crt')
    server_cert_path: str = join_path('server.crt')
    server_key_path: str = join_path('server.key')


app = FastAPI()
settings = Settings()


@app.get("/")
async def root():
    return {"message": "Hello HTTPS World!"}


def get_ssl_context():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # 加载服务器证书和私钥
    ssl_context.load_cert_chain(settings.server_cert_path, settings.server_key_path)

    if settings.is_ssl_two_way:
        # 双向认证配置
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.load_verify_locations(settings.ca_path)
        ssl_context.set_ciphers('ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384')

    return ssl_context


if __name__ == "__main__":
    import uvicorn

    ssl_context = get_ssl_context()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8443,
        ssl_keyfile=settings.server_key_path,
        ssl_certfile=settings.server_cert_path,
        ssl_ca_certs=settings.ca_path if settings.is_ssl_two_way else None,
        ssl_cert_reqs=ssl.CERT_REQUIRED if settings.is_ssl_two_way else ssl.CERT_NONE,
    )
