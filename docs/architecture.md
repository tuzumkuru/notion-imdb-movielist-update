# Architecture Diagram

This diagram shows the high-level structure of your application. It illustrates the main components: the script itself, the external services it communicates with (Notion and IMDb), and how configuration is loaded.

```mermaid
graph TD
    subgraph Your System
        A[Python Script]
    end

    subgraph External Services
        C[Notion API]
        D[IMDb via imdbinfo lib]
    end

    B[Environment/.env] -->|Loads Config| A
    A -->|Fetches pages| C
    A -->|Gets movie data| D
    A -->|Updates pages| C

```
