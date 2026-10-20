# Diagram types

Read this when choosing which diagram to draw, or when the request names a UML type.
Each row gives the mermaid form that renders the type, and the PlantUML fallback where mermaid cannot show the notation the diagram needs.

## Choosing the type

| The diagram shows | Type |
| --- | --- |
| Classes, fields, and how they relate | Class |
| A data model with keys and cardinality | ER |
| Concrete instances and their values at one moment | Object |
| Modules or namespaces and the dependencies between them | Package |
| Deployable parts and the interfaces between them | Component |
| What runs where: hosts, clusters, databases, network hops | Deployment |
| The internal parts of one component and how they connect | Composite structure |
| Custom stereotypes a team applies to model elements | Profile |
| Who uses the system and for what | Use case |
| A workflow with decisions and parallel branches | Activity |
| The states one entity moves through and what moves it | State machine |
| Messages between participants in time order | Sequence |
| Messages between participants, arranged by who links to whom | Communication |
| The order in which several interactions run | Interaction overview |
| State changes of several participants against a shared time axis | Timing |

## Mermaid forms

| Type | Form | What the form lacks |
| --- | --- | --- |
| Class | `classDiagram` | Nothing for doc use |
| ER | `erDiagram` | Nothing for doc use |
| Object | `classDiagram`, each class titled `class o1["o1 : Order"]` with one `field = value` per line | Instance names are not underlined |
| Package | `classDiagram` with `namespace` blocks, or `flowchart` subgraphs for module-level dependencies | An edge into a namespace can overlap its title, so check the render |
| Component | `architecture-beta`, a `group` per component boundary and a `service` per part | Provided and required interface symbols |
| Deployment | `architecture-beta`, a `group` per host or cluster and a `service` per deployed artifact or database, with the protocol as the edge label | UML node boxes (groups render as dashed boxes) |
| Composite structure | `flowchart` subgraph for the container, nodes for parts | Ports. Use PlantUML when ports carry the message |
| Profile | `classDiagram` with `<<stereotype>>` or `<<metaclass>>` on its own line in the class body | Nothing for doc use |
| Use case | `flowchart LR`, actors and use cases as stadium nodes `(["..."])`, a subgraph as the system boundary, `include` and `extend` as labeled dotted edges | Stick-figure actors and ellipses. Use PlantUML when a reader expects UML notation |
| Activity | `flowchart TD`, start and end as `((...))`, decisions as `{...}`, fork and join as `[[fork]]` | Swimlanes (subgraphs approximate them, with the `direction` caveat from the layout checklist) |
| State machine | `stateDiagram-v2`, including composite states | Nothing for doc use |
| Sequence | `sequenceDiagram` with `activate`, `alt`, `opt`, `loop`, `par` | Nothing for doc use |
| Communication | `flowchart LR` with numbered message labels `1: submit()`, `1.1: save()` | Nothing for doc use |
| Interaction overview | `flowchart TD` whose nodes are labeled `ref: <interaction>`, with each referenced sequence diagram drawn below | Inline interaction frames |
| Timing | None. `gantt` shows durations per lifeline but not state levels | Use PlantUML |

Avoid `C4Context` and `C4Component`: their labels overlap edges and the layout cannot be steered.

GitHub renders mermaid 12.2.0 (checked 2026-10-20), the same version the local CLI installs, so a local render matches GitHub.
To check GitHub's version again, paste a `mermaid` block containing only `info` into a GitHub comment box and open Preview without submitting.

`architecture-beta` syntax, with the built-in icons `cloud`, `database`, `disk`, `internet`, and `server`:

```
architecture-beta
  group api(cloud)[API]
  service gw(internet)[Gateway] in api
  service svc(server)[Orders service] in api
  service db(database)[Postgres] in api
  gw:R -[HTTPS]-> L:svc
  svc:R -[SQL]-> L:db
```

Each edge names the side it leaves and enters (`T`, `B`, `L`, `R`), and `-[label]->` labels it.

## Label syntax

- `<<x>>` inside a `flowchart` label or on a class member line is parsed as an HTML tag and renders as `<>`. Write `«x»` in flowchart labels. In a class, put `<<x>>` alone on its own line in the body.
- `\n` inside a class body renders literally. Put each member on its own line.
- Break a flowchart label with `<br>`.

## PlantUML fallback

Use PlantUML only for the types the table sends there.
GitHub does not render PlantUML in markdown, so commit the `.puml` source and the rendered `.svg` next to the document and embed the SVG as an image: `![Request timing](request-timing.svg)`.

Start each file with `skinparam backgroundColor white`, so the SVG stays readable in GitHub's dark theme.
Add `!pragma layout smetana` to use the built-in layout engine when Graphviz is not installed. Timing diagrams do not need it.

Render with Docker, or with the jar when a Java runtime is installed:

```
docker run --rm -v "$PWD:/data" plantuml/plantuml:1.2025.4 -tsvg /data/d.puml
java -jar plantuml.jar -tsvg d.puml
```

On macOS, `/usr/bin/java` exists without a runtime and prints "Unable to locate a Java Runtime", so check `java -version` before choosing the jar.
Render to PNG with `-tpng` to look at the result, and apply the layout checklist as for mermaid.

A timing diagram, for reference:

```
@startuml
skinparam backgroundColor white
robust "Request" as R
concise "Worker" as W
@0
R is Idle
W is Idle
@10
R is Waiting
@15
W is Busy
@35
W is Idle
@40
R is Idle
@enduml
```
