# G01: Contributor Workflow

**Status:** DRAFT

1. Read D00 and the relevant scientific specification before editing.
2. Keep changes in English and use SI quantities with explicit conventions.
3. For scientific changes, identify affected claims/equations, cite primary sources and update traceability.
4. Keep configuration and code changes reviewable; never commit generated run data, secrets or credentials.
5. Record assumptions and proposed tolerance changes. Do not mark a document BASELINE without recorded technical review.
6. Before a pull request, inspect the diff, verify internal links and complete the applicable validation workflow.

## Repository identity and local tooling

Use the repository owner's configured Git identity for every commit. Before committing, inspect `git var GIT_AUTHOR_IDENT` and `git var GIT_COMMITTER_IDENT`; do not create commits under Codex, OpenAI, or another AI-agent identity. Keep local AI instructions, machine-specific MCP settings, and the CodeGraph index out of Git.

CodeGraph is optional code-navigation tooling. The validated project setup uses `@colbymchenry/codegraph@1.6.1`: install it with `npm install --prefix "$HOME/.local" @colbymchenry/codegraph@1.6.1`, add `$HOME/.local/bin` to `PATH`, then run `codegraph init .` and `codegraph status .`. MCP-capable clients can launch `codegraph serve --mcp` through their own local client configuration. Do not commit the client configuration or `.codegraph/` index; CodeGraph supports navigation and does not validate scientific claims.
