# DAGGR - Directed Acyclic Graph Generator & Runtime

![DAGGR logo --- a dagger over the letters DAGGR](docs/daggr_logo.png)

*This is a toy project.* 

DAGGR is designed to define and execute workflows that can be represented as Directed Acyclic Graphs (DAGs) using a declarative approach --- using YAML files, for example.

## DAG Steps
Each DAG is composed of series of steps. These steps can have inputs, outputs, parameters and dependencies.

### Step Input
There are two kinds of input sources: `static` and `step`. `static` inputs are loaded from files stored in the file system. `step` inputs are loaded from a previous step's output. 

### Step Output
A step output is always the returned value from the step function.

### Dependencies
Step dependencies can be established implicitly or explicitly.

![Drawing of a step B with a dependency on the output of a step A](docs/dag_dependency.png)
The implicit dependency is set by having a step `B` with inputs that depend on the outputs of step `A`.

An explicit dependency can be configured in the workflow definition by specifying the DAG and step names. See below for more details.

## Workflow Definition
 

## Dependencies

pyyaml==6.0
yamale==4.0.2

## Development Dependencies
pytest
black
autoflake
