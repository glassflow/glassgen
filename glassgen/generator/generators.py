import random
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List
from urllib.parse import quote

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
    PREFIXED_ID = "prefixed_id"
    ARRAY = "array"
    QUERY_STRING = "query_string"


def choice_generator(choices: List[str]) -> str:
    """Generate a random choice from a list of strings"""
    return random.choice(choices)


def intrange_generator(min_val: int, max_val: int) -> int:
    """Generate a random integer between min_val and max_val"""
    return random.randint(min_val, max_val)


def greeting_generator() -> str:
    """Generate a random greeting from a list of strings"""
    return random.choice(["Hello", "Hi", "Hey", "Greetings", "Welcome"])


def price_generator(min_price: float = 0.99, max_price: float = 9999.99, decimal_places: int = 2) -> float:
    """Generate a random price value with specified decimal places
    
    Args:
        min_price: Minimum price value
        max_price: Maximum price value
        decimal_places: Number of decimal places (default: 2)
    
    Returns:
        A random price value rounded to the specified decimal places
    """
    return round(random.uniform(min_price, max_price), decimal_places)


def datetime_generator(format_str: str = None) -> str:
    """Generate current datetime with custom format"""
    if format_str:
        return datetime.now().strftime(format_str)
    else:
        return datetime.now().isoformat()


def prefixed_id_generator(prefix: str = "item", min_val: int = 1, max_val: int = 1000) -> str:
    """Generate a prefixed ID with random number in range
    
    Args:
        prefix: The prefix for the ID (e.g., 'cat', 'prod')
        min_val: Minimum value for the number part
        max_val: Maximum value for the number part
    
    Returns:
        A string in format prefix_number (e.g., 'cat_1', 'prod_42')
    """
    number = random.randint(min_val, max_val)
    return f"{prefix}_{number}"


def array_generator(generator_name: str, count: int, *generator_params) -> List[Any]:
    """Generate an array of values using a specified generator
    
    Args:
        generator_name: The name of the generator to use for each element (e.g., 'string', 'email')
        count: Number of elements to generate in the array
        *generator_params: Parameters to pass to the underlying generator
    
    Returns:
        A list of generated values
    """
    if count <= 0:
        raise ValueError("Array count must be greater than 0")
    
    # Get the generator function from the registry
    generator_func = registry.get_generator(generator_name)
    
    # Generate the array
    result = []
    for _ in range(count):
        if generator_params:
            # Handle choice generator specially - it expects a list
            if generator_name == GeneratorType.CHOICE:
                result.append(generator_func(list(generator_params)))
            else:
                result.append(generator_func(*generator_params))
        else:
            result.append(generator_func())
    
    return result


def query_string_generator() -> str:
    """Generate a query string in the format: v=2&cid=...&sid=...&sct=...&seg=...&_et=...&en=...&ep.event_id=...&dt=...&ul=...&ur=...
    
    Returns:
        A query string with dynamically generated values
    """
    # Generate random values
    cid_part1 = random.randint(100000000, 999999999)
    cid_part2 = random.randint(1000000000000, 9999999999999)
    cid = f"{cid_part1}.{cid_part2}"
    
    sid = random.randint(1000000000, 9999999999)
    sct = random.randint(1, 10)
    seg = random.choice([0, 1])
    _et = random.randint(0, 30000)
    
    en_choices = ["page_view", "scroll", "click", "purchase", "add_to_cart"]
    en = random.choice(en_choices)
    
    event_id_part1 = random.randint(1000000000000, 9999999999999)
    event_id_part2 = random.randint(1, 9)
    ep_event_id = f"{event_id_part1}.{event_id_part2}"
    
    page_titles = ["Home Page", "Product Page", "Checkout", "About Us", "Test Page Title"]
    dt = quote(random.choice(page_titles))
    
    ul_choices = ["en-us", "de-de", "fr-fr", "es-es"]
    ul = random.choice(ul_choices)
    
    # US state codes
    us_states = ["US-CA", "US-NY", "US-TX", "US-FL", "US-IL", "US-PA", "US-OH", "US-GA", "US-NC", "US-MI"]
    ur = random.choice(us_states)
    
    # Build query string
    query_parts = [
        f"v=2",
        f"cid={cid}",
        f"sid={sid}",
        f"sct={sct}",
        f"seg={seg}",
        f"_et={_et}",
        f"en={en}",
        f"ep.event_id={ep_event_id}",
        f"dt={dt}",
        f"ul={ul}",
        f"ur={ur}"
    ]
    
    return "&".join(query_parts)


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
            GeneratorType.PREFIXED_ID: prefixed_id_generator,
            GeneratorType.ARRAY: array_generator,
            GeneratorType.QUERY_STRING: query_string_generator,
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
