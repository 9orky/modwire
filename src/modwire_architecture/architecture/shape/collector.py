import re
from collections.abc import Sequence
from dataclasses import dataclass

from modwire_architecture.shared import report
from modwire_architecture.shared.config import ArchitectureConfig, ShapeRealm

from ..map.base import ArchitectureMap
from .base import ShapeResolverInterface, ShapeViolation


class ShapeReport(report.ReportItem):
    report_id: str = "architecture.violations.shape"
    report_title: str = "Shape Violations"
    report_description: str = (
        "Reports source-shape violations detected by configured resolvers, "
        "including file, class, callable, import, property, signature, and symbol rules."
    )
    report_path: str = "violations.shape"
    report_order: int = 20

    violations: tuple[ShapeViolation, ...] = ()
    resolvers: tuple[str, ...] = ()


@dataclass(frozen=True)
class ShapeRealmArchitectureMap:
    code_map: object
    shape_realm_name: str
    shape_realm_source_ids: frozenset[str]


class ShapeReportCollector(report.ReportCollector[ShapeReport]):
    report_type: type[ShapeReport] = ShapeReport

    def __init__(
        self,
        config: ArchitectureConfig,
        resolvers: Sequence[ShapeResolverInterface],
    ):
        self.config = config.shape
        self.resolvers = tuple(sorted(resolvers, key=lambda resolver: resolver.name))

    def collect(self, architecture_map: ArchitectureMap) -> ShapeReport:
        resolver_names = tuple(resolver.name for resolver in self.resolvers)
        violations: list[ShapeViolation] = []
        for realm in self.config.realms:
            realm_map = self.realm_map(architecture_map, realm)
            for resolver in self.resolvers:
                violations.extend(
                    violation.model_copy(update={"realm": realm.name})
                    for violation in resolver.resolve(realm_map, realm.shape)
                )
        return self.report_type(
            violations=tuple(violations),
            resolvers=resolver_names,
        )

    def realm_map(
        self,
        architecture_map: ArchitectureMap,
        realm: ShapeRealm,
    ) -> ShapeRealmArchitectureMap:
        return ShapeRealmArchitectureMap(
            code_map=architecture_map.code_map,
            shape_realm_name=realm.name,
            shape_realm_source_ids=frozenset(
                source_id
                for source_id in architecture_map.code_map.source_ids()
                if self.matches(realm.match, source_id)
            ),
        )

    def matches(self, pattern: str, source_id: str) -> bool:
        normalized_pattern = pattern.replace("\\", "/").strip("/")
        normalized_source_id = source_id.replace("\\", "/").strip("/")
        pattern_regex = "/".join(
            "([^/]+)" if part == "*" else re.escape(part)
            for part in normalized_pattern.split("/")
        )
        return re.match(f"^{pattern_regex}(?:/.*)?$", normalized_source_id) is not None
