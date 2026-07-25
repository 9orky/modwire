from modwire_architecture import ArchitectureConfig, Modwire


def test_published_api_exposes_the_architecture_report_catalog() -> None:
    catalog = Modwire().architecture(project_config()).reports()

    assert tuple(report.id for report in catalog.reports) == (
        "architecture.map",
        "architecture.violations.flow",
        "architecture.violations.shape",
        "architecture.insights",
    )
    assert tuple(child.id for child in catalog.reports[-1].children) == (
        "architecture.insights.clusters",
        "architecture.insights.hotspots",
        "architecture.insights.coherence",
        "architecture.insights.callables",
        "architecture.insights.exports",
    )


def project_config() -> ArchitectureConfig:
    return ArchitectureConfig(
        shape={"realms": ({"name": "project", "match": "*"},)}
    )
