from pydantic import BaseModel


class Address(BaseModel):
    hostname: str
    port: str


class Proxy(BaseModel):
    name: str
    status: str
    alive: bool
    address: Address
