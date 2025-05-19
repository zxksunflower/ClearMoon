from fastapi import FastAPI, Request, HTTPException, status
import ssl
from typing import Optional
import os
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SSL_FILE_DIR = os.path.join(BASE_DIR, 'ssl_file')

CA_PATH = os.path.join(SSL_FILE_DIR, 'ca.crt')
SERVER_CERT_PATH = os.path.join(SSL_FILE_DIR, 'server.crt')
SERVER_KEY_PATH = os.path.join(SSL_FILE_DIR, 'server.key')


class Settings(BaseSettings):
    ssl_mode: str = "two_way"  # 或 "two_way"

    class Config:
        env_file = ".env"


app = FastAPI()
settings = Settings()


@app.get("/")
async def root():
    return {"message": "Hello HTTPS World!"}


def get_ssl_context():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # 加载服务器证书和私钥
    ssl_context.load_cert_chain(SERVER_CERT_PATH, SERVER_KEY_PATH)

    if settings.ssl_mode == "two_way":
        # 双向认证配置
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.load_verify_locations(CA_PATH)
        ssl_context.set_ciphers('ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384')

    return ssl_context


if __name__ == "__main__":
    import uvicorn

    ssl_context = get_ssl_context()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8443,
        ssl_keyfile=SERVER_KEY_PATH,
        ssl_certfile=SERVER_CERT_PATH,
        ssl_ca_certs=CA_PATH if settings.ssl_mode == "two_way" else None,
        ssl_cert_reqs=ssl.CERT_REQUIRED if settings.ssl_mode == "two_way" else ssl.CERT_NONE,
    )
