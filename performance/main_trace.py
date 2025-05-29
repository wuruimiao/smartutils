from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# 设置 Resource，指定 service.name
resource = Resource(
    attributes={
        "service.name": "my-fastapi-service",  # 这里设置你的服务名
    }
)

provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://192.168.1.56:4318/v1/traces",
    # insecure=True,
)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)

app = FastAPI()

# Instrument
FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
RequestsInstrumentor().instrument()


@app.get("/")
async def root():
    return {"hello": "world"}
