import json

import pytest
from pydantic import ValidationError

from modwire_architecture import ArchitectureConfig


def test_shape_configuration_requires_a_non_empty_realm_boundary() -> None:
    with pytest.raises(ValidationError, match="shape"):
        ArchitectureConfig()

    with pytest.raises(ValidationError, match="at least 1 item"):
        ArchitectureConfig(shape={"realms": ()})


def test_shape_realm_configuration_round_trips_as_a_public_document() -> None:
    config = ArchitectureConfig(
        shape={
            "realms": (
                {
                    "name": "project",
                    "match": "*",
                },
            )
        }
    )

    document = json.loads(config.to_json())

    assert document["shape"]["realms"] == [
        {
            "name": "project",
            "match": "*",
            "shape": {
                "max_classes_per_file": -1,
                "max_interfaces_per_file": -1,
                "max_types_per_file": -1,
                "max_abstract_classes_per_file": -1,
                "max_functions_per_file": 0,
                "max_methods_per_class": -1,
                "max_declared_args": -1,
                "max_function_lines": -1,
                "max_method_lines": -1,
                "max_class_lines": -1,
                "allow_optional_function_args": False,
                "allow_optional_method_args": False,
                "allow_optional_class_properties": False,
                "allow_import_aliases": False,
                "require_joined_imports": True,
                "allowed_import_crossing_types": ["module", "symbol"],
            },
        }
    ]
    assert ArchitectureConfig.from_json(config.to_json()) == config
    assert ArchitectureConfig.from_yaml(config.to_yaml()) == config
