from modwire_architecture import ArchitectureConfig, Modwire


def catalog():
    return Modwire().architecture(
        ArchitectureConfig(
            shape={"realms": ({"name": "project", "match": "*"},)}
        )
    ).reports()
