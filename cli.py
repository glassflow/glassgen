import json
from typing import Optional

import click

from glassgen import generate


@click.group()
def cli():
    """GlassGen - Flexible synthetic data generation service"""
    pass


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    required=True,
    help="Path to configuration file",
)
def generate_data(config: str):
    """Generate synthetic data based on the specified configuration file"""
    try:
        with open(config, "r") as f:
            config_data = json.load(f)

        # Generate data
        num_records = config_data.get("generator", {}).get("num_records", 1000)
        click.echo(f"Generating {num_records} records...")
        generate(config=config_data)
        output_path = (
            config_data.get("sink", {}).get("params", {}).get("path", "output")
        )
        click.echo(f"Data generation completed. Output saved to {output_path}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort() from e


@cli.command()
@click.option(
    "--type",
    "-t",
    type=click.Choice(["csv", "kafka"]),
    default="csv",
    help="Configuration type",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def init_config(type: str, output: Optional[str]):
    """Initialize a new configuration file"""
    config_templates = {
        "csv": {
            "schema": {
                "name": "$name",
                "email": "$email",
                "country": "$country",
                "id": "$uuid",
                "address": "$address",
                "phone": "$phone_number",
                "job": "$job",
                "company": "$company",
            },
            "sink": {"type": "csv", "params": {"path": "output.csv"}},
            "generator": {"rps": 500, "num_records": 1000},
        },
        "kafka": {
            "schema": {
                "name": "$name",
                "email": "$email",
                "country": "$country",
                "id": "$uuid",
                "address": "$address",
                "phone": "$phone_number",
                "job": "$job",
                "company": "$company",
            },
            "sink": {
                "type": "kafka",
                "params": {
                    "bootstrap.servers": "your-kafka-host:9092",
                    "topic": "glassgen-data",
                    "security.protocol": "SASL_SSL",
                    "sasl.mechanism": "PLAIN",
                    "sasl.username": "your-api-key",
                    "sasl.password": "your-api-secret",
                },
            },
            "generator": {"rps": 500, "num_records": 1000},
        },
    }

    output_path = output or f"config.{type}.json"
    try:
        with open(output_path, "w") as f:
            json.dump(config_templates[type], f, indent=4)
        click.echo(f"Configuration file created at {output_path}")
    except Exception as e:
        click.echo(f"Error creating configuration file: {str(e)}", err=True)
        raise click.Abort() from e


if __name__ == "__main__":
    cli()
