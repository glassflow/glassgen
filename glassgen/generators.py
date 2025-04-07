from enum import Enum
from typing import Any, Callable, Dict
from faker import Faker

class GeneratorType(str, Enum):
    """Supported generator types"""
    STRING = "string"
    INT = "int"    
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
            GeneratorType.EMAIL: self._faker.email,
            GeneratorType.COUNTRY: self._faker.country,
            GeneratorType.UUID: lambda: str(self._faker.uuid4()),
            GeneratorType.NAME: self._faker.name,
            GeneratorType.TEXT: self._faker.text,
            GeneratorType.ADDRESS: lambda: self._faker.address().replace('\n', ' ').strip(),
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