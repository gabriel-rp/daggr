from daggr.workflow_loader.workflow_definition_loader import WorkflowDefinitionLoader
from daggr.workflow_loader.yaml_definition_loader import YamlDefinitionLoader


class WorkflowDefinitionLoaderFactory:
    IMPLEMENTATIONS = {"yaml": YamlDefinitionLoader}

    @staticmethod
    def create(type: str, filepath: str) -> WorkflowDefinitionLoader:
        return WorkflowDefinitionLoaderFactory.IMPLEMENTATIONS[type](filepath)
