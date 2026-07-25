from pathlib import Path


FIXTURE_DIRECTORY = Path(__file__).parent / "fixtures" / "import_only"


def test_published_import_consumer_can_request_reports() -> None:
    namespace: dict[str, object] = {}
    source = (FIXTURE_DIRECTORY / "consumer_after.py").read_text()

    exec(compile(source, "consumer_after.py", "exec"), namespace)

    catalog = namespace["catalog"]()

    assert tuple(report.id for report in catalog.reports) == (
        "architecture.map",
        "architecture.violations.flow",
        "architecture.violations.shape",
        "architecture.insights",
    )
