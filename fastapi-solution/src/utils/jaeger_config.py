from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from core.config import jaeger_settings


def configure_jaeger_tracer(app: FastAPI, host: str, port: int) -> None:
    if not jaeger_settings.enable_tracer:
        return

    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({SERVICE_NAME: "Elastic API"}))
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=host,
                agent_port=port,
            )
        )
    )

    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    FastAPIInstrumentor.instrument_app(app)
