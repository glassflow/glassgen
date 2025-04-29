# a user schema that generates a simulated user profile
import random
from typing import Any, Dict

from glassgen.generator.generators import GeneratorType, registry
from glassgen.schema.base import BaseSchema


class UserSchema(BaseSchema):
    """A schema for generating user profile data"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate()

    def validate(self):
        """Validate the schema configuration"""
        # Check if all required generators are available
        required_generators = {
            GeneratorType.NAME,
            GeneratorType.EMAIL,
            GeneratorType.PHONE_NUMBER,
            GeneratorType.ADDRESS,
        }

        available_generators = set(registry.get_supported_generators().keys())
        missing_generators = required_generators - available_generators

        if missing_generators:
            raise ValueError(
                f"Missing required generators: {', '.join(missing_generators)}"
            )

    def _generate_record(self) -> Dict[str, Any]:
        """Generate a user profile record using the generator registry"""
        return {
            "name": registry.get_generator(GeneratorType.NAME)(),
            # custom schemas can easily extend the generators available
            "age": random.randint(18, 65),
            "email": registry.get_generator(GeneratorType.EMAIL)(),
            "phone": registry.get_generator(GeneratorType.PHONE_NUMBER)(),
            "address": registry.get_generator(GeneratorType.ADDRESS)(),
        }
