import os


class Config:
    __secret_key = os.getenv("SECRET_KEY")
    __port = int(os.getenv("PORT")) if os.getenv("PORT") else 5000

    @classmethod
    @property
    def secret_key(cls) -> str:
        return Config.__secret_key

    @classmethod
    def port(cls) -> int:
        return Config.__port
