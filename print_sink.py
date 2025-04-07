# a sink that prints the data to the console
from glassgen.sinks import BaseSink

class PrintSink(BaseSink):
    def __init__(self, config=None):
        self.config = config
    
    def publish(self, data):
        print(data)
    
    def close(self):
        pass