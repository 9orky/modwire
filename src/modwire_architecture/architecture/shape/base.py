import abc
from collections.abc import Iterable, Iterator, Sequence
from typing import Protocol, TypeVar

from modwire_extraction.code import QueryableCodeMap
from modwire_architecture.shared import ModwireModel
from modwire_architecture.shared.config import ShapeConfig


RealmResult = TypeVar("RealmResult")


class ArchitectureMapQuery(Protocol):
    code_map: QueryableCodeMap
    shape_realm_name: str
    shape_realm_source_ids: frozenset[str]


class NamedLineShape(Protocol):
    name: str
    line_count: int


class CallableShape(NamedLineShape, Protocol):
    declared_args: int
    optional_args: bool


class AbstractClassShape(NamedLineShape, Protocol):
    abstract_methods: Sequence[CallableShape]
    concrete_methods: Sequence[CallableShape]


class PropertyShape(Protocol):
    name: str
    is_optional: bool


class SignatureShape(Protocol):
    declared_args: int
    optional_args: bool


class ShapeViolation(ModwireModel):
    source_id: str
    rule_name: str
    actual: int | str | bool
    limit: int | str | bool
    realm: str = ""
    symbol_kind: str = ""
    symbol_name: str = ""


class ShapeResolverInterface(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def title(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def resolve(
        self,
        architecture_map: ArchitectureMapQuery,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        raise NotImplementedError


class SymbolShapeResolverInterface(ShapeResolverInterface):
    pass


class BaseShapeResolver:
    def realm_source_ids(
        self,
        architecture_map: ArchitectureMapQuery,
    ) -> Iterator[str]:
        return (
            source_id
            for source_id in architecture_map.code_map.source_ids()
            if self.source_is_in_realm(architecture_map, source_id)
        )

    def realm_results(
        self,
        architecture_map: ArchitectureMapQuery,
        results: Iterable[RealmResult],
    ) -> Iterator[RealmResult]:
        return (
            result
            for result in results
            if self.source_is_in_realm(architecture_map, result.source_id)
        )

    def source_is_in_realm(
        self,
        architecture_map: ArchitectureMapQuery,
        source_id: str,
    ) -> bool:
        source_ids = getattr(architecture_map, "shape_realm_source_ids", None)
        return source_ids is None or source_id in source_ids

    def limit_violation(
        self,
        *,
        source_id: str,
        rule_name: str,
        actual: int,
        limit: int,
        symbol_kind: str = "",
        symbol_name: str = "",
    ) -> ShapeViolation | None:
        if limit < 0 or actual <= limit:
            return None
        return ShapeViolation(
            source_id=source_id,
            rule_name=rule_name,
            actual=actual,
            limit=limit,
            symbol_kind=symbol_kind,
            symbol_name=symbol_name,
        )
