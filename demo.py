import time
import yaml
from pathlib import Path
from glassgen import Generator, Schema, CSVSink, JSONSink, KafkaSink

def demo_basic_usage():
    """Demonstrate basic usage of GlassGen with CSV output"""
    print("\n=== Basic Usage Demo ===")
    
    # Create a schema
    schema = Schema.from_dict({
        "name": "$string",        
        "email": "$email",
        "country": "$country",
        "id": "$uuid",
        "phone": "$phone_number",
    })
    
    # Create a CSV sink
    sink = CSVSink("basic_demo.csv")
    
    # Create and run the generator
    generator = Generator(schema, sink)
    print("Generating 10 records to basic_demo.csv...")
    generator.generate(10)
    print("Done!")

def demo_with_rate_limiting():
    """Demonstrate rate-limited generation with JSON output"""
    print("\n=== Rate-Limited Generation Demo ===")
    
    schema = Schema.from_dict({
        "name": "$string",      
        "email": "$email"
    })
    
    sink = JSONSink("rate_limited_demo.json")
    generator = Generator(schema, sink)
    
    print("Generating 5 records at 2 records/second to rate_limited_demo.json...")
    start_time = time.time()
    generator.generate(5, rate=2)
    end_time = time.time()
    
    print(f"Generation completed in {end_time - start_time:.2f} seconds")

def demo_kafka_sink():
    """Demonstrate Kafka sink usage"""
    print("\n=== Kafka Sink Demo ===")
    
    # Note: This requires a running Kafka instance
    try:
        schema = Schema.from_dict({
            "name": "$string",            
        })
        
        sink = KafkaSink(
            bootstrap_servers="localhost:9092",
            topic="glassgen_demo"
        )
        
        generator = Generator(schema, sink)
        print("Generating 3 records to Kafka topic 'glassgen_demo'...")
        generator.generate(3)
        print("Done!")
    except Exception as e:
        print(f"Kafka demo failed (make sure Kafka is running): {e}")

def demo_from_config():
    """Demonstrate usage with a configuration file"""
    print("\n=== Configuration File Demo ===")
    
    # Create a sample config file
    config = {
        "schema": {
            "name": "$string",
            "email": "$email"
        },
        "sink": {
            "type": "csv",
            "path": "config_demo.csv"
        },
        "generation": {
            "count": 5,
            "rate": 1
        }
    }
    
    # Save the config
    config_path = Path("demo_config.yaml")
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    
    print(f"Created config file at {config_path}")
    print("You can now run: glassgen generate --config demo_config.yaml")
    
    # Clean up
    config_path.unlink()

def main():
    """Run all demos"""
    print("GlassGen Demo\n")
    
    # Run each demo
    demo_basic_usage()
    demo_with_rate_limiting()
    demo_kafka_sink()
    demo_from_config()
    
    print("\nDemo completed!")
    print("Check the generated files:")
    print("- basic_demo.csv")
    print("- rate_limited_demo.json")
    print("- config_demo.csv (if you ran the CLI command)")

if __name__ == "__main__":
    main() 