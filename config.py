import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class TelegramConfig:
    token: str
    admin_id: int


@dataclass
class SQLConfig:
    host: str
    port: int
    name: str
    user: str
    password: str


@dataclass
class Config:
    tg: TelegramConfig
    sql: SQLConfig


def load_config() -> Config:
    token = os.getenv('BOT_TOKEN')
    admin_id = os.getenv('ADMIN_ID')

    if not token:
        raise ValueError('Missing token')
    elif not admin_id:
        raise ValueError('Missing admin id')

    tg = TelegramConfig(
        token=token,
        admin_id=int(admin_id),
    )

    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    name = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASS')

    if not host:
        raise ValueError('Missing database host')
    elif not port:
        raise ValueError('Missing database port')
    elif not name:
        raise ValueError('Missing database name')
    elif not user:
        raise ValueError('Missing database user')
    elif not password:
        raise ValueError('Missing database password')

    sql = SQLConfig(
        host=host,
        port=int(port),
        name=name,
        user=user,
        password=password,
    )

    return Config(
        tg=tg,
        sql=sql
    )