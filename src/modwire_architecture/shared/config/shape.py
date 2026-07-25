from pydantic import Field, field_validator, model_validator

from ..base import ModwireConfigModel


class ShapeRules(ModwireConfigModel):
    max_classes_per_file: int = -1
    max_interfaces_per_file: int = -1
    max_types_per_file: int = -1
    max_abstract_classes_per_file: int = -1
    max_functions_per_file: int = 0
    max_methods_per_class: int = -1
    max_declared_args: int = -1
    max_function_lines: int = -1
    max_method_lines: int = -1
    max_class_lines: int = -1
    allow_optional_function_args: bool = False
    allow_optional_method_args: bool = False
    allow_optional_class_properties: bool = False
    allow_import_aliases: bool = False
    require_joined_imports: bool = True
    allowed_import_crossing_types: tuple[str, ...] = ("module", "symbol")

    @field_validator(
        "max_classes_per_file",
        "max_interfaces_per_file",
        "max_types_per_file",
        "max_abstract_classes_per_file",
        "max_functions_per_file",
        "max_methods_per_class",
        "max_declared_args",
        "max_function_lines",
        "max_method_lines",
        "max_class_lines",
    )
    @classmethod
    def disabled_or_non_negative(cls, limit: int) -> int:
        if limit < -1:
            raise ValueError("Limit must be -1 or a non-negative integer")
        return limit


class ShapeRealm(ModwireConfigModel):
    name: str
    match: str
    shape: ShapeRules = Field(default_factory=ShapeRules)

    @field_validator("name", "match")
    @classmethod
    def require_value(cls, value: str) -> str:
        if not value:
            raise ValueError("Shape realm name and match pattern cannot be empty")
        return value


class ShapeConfig(ModwireConfigModel):
    realms: tuple[ShapeRealm, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_realms(self) -> "ShapeConfig":
        names = tuple(realm.name for realm in self.realms)
        if len(names) != len(set(names)):
            raise ValueError("Shape realm names must be unique")
        return self
