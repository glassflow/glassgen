import yaml
import click
from pathlib import Path
from typing import Dict, Any

from .generator import Generator
from .schema import Schema
from .sinks import CSVSink, JSONSink, KafkaSink

def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path) as f:
        return yaml.safe_load(f)

def create_sink(config: Dict[str, Any]) -> Any:
    sink_config = config["sink"]
    sink_type = sink_config["type"]
    
    if sink_type == "csv":
        return CSVSink(sink_config["path"])
    elif sink_type == "json":
        return JSONSink(sink_config["path"])
    elif sink_type == "kafka":
        return KafkaSink(
            bootstrap_servers=sink_config["bootstrap_servers"],
            topic=sink_config["topic"]
        )
    else:
        raise ValueError(f"Unsupported sink type: {sink_type}")

@click.group()
def main():
    """GlassGen - Synthetic Data Generation Service"""
    pass

@main.command()
@click.option("--config", "-c", required=True, help="Path to configuration file")
def generate(config: str):
    """Generate data according to the configuration"""
    config_path = Path(config)
    if not config_path.exists():
        click.echo(f"Error: Configuration file not found: {config}")
        return

    try:
        config_data = load_config(config)
        schema = Schema.from_dict(config_data["schema"])
        schema.validate()
        
        sink = create_sink(config_data)
        generator = Generator(schema, sink)
        
        generation_config = config_data["generation"]
        generator.generate(
            count=generation_config["count"],
            rate=generation_config.get("rate", 0)
        )
        
        click.echo("Data generation completed successfully!")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    main() 