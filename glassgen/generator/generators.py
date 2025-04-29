import random
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List

from faker import Faker


class GeneratorType(str, Enum):
    """Supported generator types"""

    STRING = "string"
    INT = "int"
    INTRANGE = "intrange"
    CHOICE = "choice"
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"
    EMAIL = "email"
    COUNTRY = "country"
    UUID = "uuid"
    NAME = "name"
    TEXT = "text"
    ADDRESS = "address"
    PHONE_NUMBER = "phone_number"
    JOB = "job"
    COMPANY = "company"
    CITY = "city"
    ZIPCODE = "zipcode"
    USER_NAME = "user_name"
    PASSWORD = "password"
    SSN = "ssn"
    IPV4 = "ipv4"
    URL = "url"
    UUID4 = "uuid4"
    BOOLEAN = "boolean"
    CURRENCY_NAME = "currency_name"
    COLOR_NAME = "color_name"
    COMPANY_EMAIL = "company_email"
    GREETING = "greeting"
    FLOAT = "float"
    PRICE = "price"


def choice_generator(choices: List[str]) -> str:
    """Generate a random choice from a list of strings"""
    return random.choice(choices)


def intrange_generator(min_val: int, max_val: int) -> int:
    """Generate a random integer between min_val and max_val"""
    return random.randint(min_val, max_val)


def greeting_generator() -> str:
    """Generate a random greeting from a list of strings"""
    return random.choice(["Hello", "Hi", "Hey", "Greetings", "Welcome"])


def price_generator(min_price: float = 0.99, max_price: float = 9999.99) -> float:
    """Generate a random price value with 2 decimal places"""
    return round(random.uniform(min_price, max_price), 2)


def datetime_generator(format_str: str = None) -> str:
    """Generate current datetime with custom format"""
    if format_str:
        return datetime.now().strftime(format_str)
    else:
        return datetime.now().isoformat()


class GeneratorRegistry:
    """Registry for data generators"""

    def __init__(self):
        self._faker = Faker()
        self._generators: Dict[str, Callable[..., Any]] = {}
        self._register_default_generators()

    def _register_default_generators(self):
        """Register default generators"""
        self._generators = {
            GeneratorType.STRING: self._faker.word,
            GeneratorType.INT: self._faker.random_int,
            GeneratorType.INTRANGE: intrange_generator,
            GeneratorType.CHOICE: choice_generator,
            GeneratorType.DATETIME: datetime_generator,
            GeneratorType.TIMESTAMP: lambda: int(time.time()),
            GeneratorType.EMAIL: self._faker.email,
            GeneratorType.COUNTRY: self._faker.country,
            GeneratorType.UUID: lambda: str(self._faker.uuid4()),
            GeneratorType.NAME: self._faker.name,
            GeneratorType.TEXT: self._faker.text,
            GeneratorType.ADDRESS: lambda: self._faker.address()
            .replace("\n", " ")
            .strip(),
            GeneratorType.PHONE_NUMBER: self._faker.phone_number,
            GeneratorType.JOB: self._faker.job,
            GeneratorType.COMPANY: self._faker.company,
            GeneratorType.CITY: self._faker.city,
            GeneratorType.ZIPCODE: self._faker.zipcode,
            GeneratorType.USER_NAME: self._faker.user_name,
            GeneratorType.PASSWORD: self._faker.password,
            GeneratorType.SSN: self._faker.ssn,
            GeneratorType.IPV4: self._faker.ipv4,
            GeneratorType.URL: self._faker.url,
            GeneratorType.UUID4: lambda: str(self._faker.uuid4()),
            GeneratorType.BOOLEAN: self._faker.boolean,
            GeneratorType.CURRENCY_NAME: self._faker.currency_name,
            GeneratorType.COLOR_NAME: self._faker.color_name,
            GeneratorType.COMPANY_EMAIL: self._faker.company_email,
            GeneratorType.GREETING: greeting_generator,
            GeneratorType.FLOAT: self._faker.pyfloat,
            GeneratorType.PRICE: price_generator,
        }

    def register_generator(self, name: str, generator: Callable[..., Any]) -> None:
        """Register a new generator"""
        self._generators[name] = generator

    def get_generator(self, name: str) -> Callable[..., Any]:
        """Get a generator by name"""
        if name not in self._generators:
            raise ValueError(f"Unknown generator type: {name}")
        return self._generators[name]

    def get_supported_generators(self) -> Dict[str, Callable[..., Any]]:
        """Get all supported generators"""
        return self._generators.copy()


# Create a global registry instance
registry = GeneratorRegistry()
