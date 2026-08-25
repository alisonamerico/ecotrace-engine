from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from app.core.telemetry import configure_telemetry, get_tracer


def test_configure_telemetry_returns_provider():
    provider = configure_telemetry()
    assert isinstance(provider, TracerProvider)


def test_get_tracer_returns_named_tracer():
    configure_telemetry()
    tracer = get_tracer("test.tracer")
    assert tracer is not None
    assert isinstance(tracer, trace.Tracer)


def test_configure_telemetry_is_idempotent():
    p1 = configure_telemetry()
    p2 = configure_telemetry()
    assert p1 is p2
