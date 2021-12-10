from pathlib import Path

import yamale
import yaml

from daggr.core.dag import WorkflowDefinition
from daggr.workflow_loader.workflow_definition_loader import (
    InvalidWorkflow,
    InvalidWorkflowSchema,
    WorkflowDefinitionLoader,
    WorkflowDefinitionValidator,
)
from daggr.workflow_loader.workflow_loader import WorkflowDefinitionLoader


class CouldNotLoadFile(Exception):
    def __init__(self, path: str, exception: Exception) -> None:
        self.path = path
        self.exception = exception

    def __str__(self) -> str:
        return (
            "File could not be loaded.\n"
            f"Path: {self.path}\n"
            f"Error: {self.exception}"
        )


class CouldNotParseYaml(Exception):
    def __init__(self, path: str, exception: Exception) -> None:
        self.path = path
        self.exception = exception

    def __str__(self) -> str:
        return (
            "YAML file could not be parsed.\n"
            f"Path: {self.path}\n"
            f"Error: {self.exception}"
        )


class _YamlFileLoader:
    @staticmethod
    def load(path: str):
        try:
            with open(path, "r") as f:
                return yaml.load(f, Loader=yaml.Loader)
        except OSError as e:
            raise CouldNotLoadFile(path, e)
        except Exception as e:
            raise CouldNotParseYaml(path, e)


class YamlDefinitionLoader(WorkflowDefinitionLoader):
    def __init__(self, filepath: str) -> None:
        super().__init__(filepath)
        self.validator = YamlWorkflowValidator(self.filepath)

    def load(self) -> WorkflowDefinition:
        self.validator.validate_schema()
        return WorkflowDefinition(
            **_YamlFileLoader.load(self.filepath), path=str(Path(self.filepath).parent)
        )


class YamlWorkflowValidator(WorkflowDefinitionValidator):
    filepath: str

    def validate_schema(self) -> None:
        schema_file = Path(__file__).parent / "workflow_schema.yml"
        schema = yamale.make_schema(str(schema_file))

        try:
            data = yamale.make_data(self.filepath)
            yamale.validate(schema, data)
        except Exception as e1:
            if locals().get("data"):
                raise InvalidWorkflowSchema(data, e1)

            try:
                _YamlFileLoader.load(self.filepath)
            except Exception as e2:
                raise InvalidWorkflow({}, e2)
