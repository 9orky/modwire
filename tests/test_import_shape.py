from modwire_architecture import ArchitectureConfig, Modwire
from modwire_extraction import QueryableCodeMap
from modwire_extraction.code import CodeMap


def test_shape_realms_apply_their_own_defaulted_rules_to_matching_files() -> None:
    config = ArchitectureConfig(
        shape={
            "realms": (
                {
                    "name": "application",
                    "match": "src/*",
                },
                {
                    "name": "tests",
                    "match": "tests/*",
                    "shape": {"max_functions_per_file": -1},
                },
            )
        }
    )
    code_map = queryable_map(
        "src/application.py",
        "tests/test_application.py",
    )

    shape = next(
        report
        for report in Modwire().architecture(config).report(code_map)
        if report.metadata.id == "architecture.violations.shape"
    )

    assert tuple(
        (violation.realm, violation.source_id, violation.rule_name)
        for violation in shape.violations
    ) == (("application", "src/application.py", "max_functions_per_file"),)


def test_shape_realms_report_each_matching_glob_independently() -> None:
    config = ArchitectureConfig(
        shape={
            "realms": (
                {
                    "name": "application",
                    "match": "src/*",
                },
                {
                    "name": "repository",
                    "match": "*",
                },
            )
        }
    )

    shape = next(
        report
        for report in Modwire().architecture(config).report(
            queryable_map("src/application.py")
        )
        if report.metadata.id == "architecture.violations.shape"
    )

    assert tuple(
        (violation.realm, violation.source_id, violation.rule_name)
        for violation in shape.violations
    ) == (
        ("application", "src/application.py", "max_functions_per_file"),
        ("repository", "src/application.py", "max_functions_per_file"),
    )


def queryable_map(*paths: str) -> QueryableCodeMap:
    files = {path: source_file(path) for path in paths}
    return QueryableCodeMap(
        CodeMap.from_dict(
            {
                "language": "test",
                "extraction": {
                    "files": files,
                    "modules": {
                        source["module_id"]: file_id
                        for file_id, source in files.items()
                    },
                    "files_found": len(files),
                    "files_excluded": 0,
                },
                "dependency_graph": {
                    "nodes": {
                        path: {"id": path, "kind": "file"}
                        for path in paths
                    },
                    "edges": [],
                },
            }
        )
    )


def source_file(file_id: str) -> dict[str, object]:
    return {
        "file_id": file_id,
        "module_id": file_id.rsplit(".", 1)[0],
        "imports": [],
        "exports": [],
        "classes": [],
        "interfaces": [],
        "types": [],
        "abstract_classes": [],
        "functions": [
            {
                "name": "entrypoint",
                "visibility": "public",
                "visibility_intent": "public",
                "line_count": 1,
                "declared_args": 0,
                "optional_args": 0,
            }
        ],
        "values": [],
        "callables": [],
        "calls": [],
        "line_count": 1,
        "code_line_count": 1,
        "public_symbol_count": 1,
    }
