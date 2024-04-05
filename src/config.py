from dotenv import load_dotenv
from os import getenv
from pydantic_settings import BaseSettings

load_dotenv()


class DatabaseSettings(BaseSettings):
    user: str = getenv('USER')
    pwd: str = getenv('PASS')
    host: str = getenv('HOST')
    port: int = getenv('PORT')
    name: str = getenv('NAME')

    @property
    def db_url(self):
        return f'postgresql+psycopg2://{self.user}:{self.pwd}@{self.host}:{self.port}/{self.name}'


db_settings = DatabaseSettings()


class SMTPSettings(BaseSettings):
    sender: str = getenv('SMTP_SENDER')
    pwd: str = getenv('SMTP_PASS')


SMTP_SETTINGS = SMTPSettings()

print(SMTP_SETTINGS)