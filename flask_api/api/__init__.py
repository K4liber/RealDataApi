import os


class Config:
    __secret_key = os.getenv("SECRET_KEY")
    __port = int(os.getenv("PORT"))

    @classmethod
    @property
    def secret_key(cls) -> str:
        return Config.__secret_key

    @classmethod
    @property
    def port(cls) -> int:
        return Config.__port
