# Release Process

How to cut a new release of a `packages/*` module (e.g. `mcp-ibge`) and
publish it to [PyPI](https://pypi.org/). This page describes the **general
process**, reusable for every module in this workspace — replace
`<package>` with the package directory name (e.g. `mcp_ibge`) and
`<version>` with the new version (e.g. `0.3.0`).

`mcp-ibge` is the first module published this way; future modules
(`mcp-inep`, etc.) follow the same steps once they reach a publishable state.

## 1. Update the version

- [ ] `packages/<package>/pyproject.toml` → `[project] version = "<version>"`.
- [ ] `packages/<package>/src/<package>/__init__.py` → `__version__ = "<version>"`.
- [ ] If `config.py` has a `User-Agent` default that embeds the package's own
      version (e.g. `mcp-ibge/<version>`), update it too.
- [ ] `CHANGELOG.md`: move the contents of `[Unreleased]` into a new
      `## [<version>] - <YYYY-MM-DD>` section (keep `[Unreleased]` empty for
      the next cycle).
- [ ] Confirm `requires-python` in `pyproject.toml` still matches the Python
      versions tested in
      [`.github/workflows/ci.yml`](https://github.com/FilipePessoa30/mcp-data-br/blob/main/.github/workflows/ci.yml).

## 2. Run the test suite

```bash
uv run --directory packages/<package> pytest -q
```

All tests must pass — they run against `respx`-mocked HTTP responses, no
network access required.

## 3. Run lint, format and type checks

```bash
uv run ruff check packages/<package>
uv run ruff format --check packages/<package>
uv run --directory packages/<package> mypy
```

`mypy` is `continue-on-error` in CI, but should be clean before a release
when possible.

## 4. Generate the build

From the **workspace root**, build the sdist and wheel for the package with
`uv` — workspace builds always write to the root `dist/`, regardless of
which member is built:

```bash
rm -rf dist
uv build --package <package-name>   # e.g. mcp-ibge
```

- [ ] `dist/` contains exactly one `.tar.gz` (sdist) and one `.whl` (wheel).
- [ ] Inspect the contents for unwanted files (`.env`, caches,
      `tests/__pycache__`, `.mypy_cache`, `.ruff_cache`, ...):
  ```bash
  tar -tzf dist/<package_dist_name>-<version>.tar.gz | sort
  unzip -l dist/<package_dist_name>-<version>-py3-none-any.whl
  ```
- [ ] (Optional, requires `twine`) validate metadata and the rendered
      `README.md` long description:
  ```bash
  uv run --with twine twine check dist/*
  ```

## 5. Test the local install

Install the freshly built wheel into an isolated environment and confirm the
entry points work, **without** touching PyPI:

```bash
# Run the MCP server entry point from the local wheel
uvx --from ./dist/<package_dist_name>-<version>-py3-none-any.whl mcp-ibge --help

# Run the CLI entry point (mcp-ibge also ships `mcp-data-br`)
uvx --from ./dist/<package_dist_name>-<version>-py3-none-any.whl mcp-data-br status
```

- [ ] Both entry points (`mcp-ibge`, `mcp-data-br`) start without import
      errors.
- [ ] `mcp-data-br status` returns the standard `{ok, data, metadata,
      warnings, errors}` envelope.

## 6. Publish to TestPyPI (recommended first)

- [ ] Create/use a [TestPyPI](https://test.pypi.org/) account and generate an
      API token scoped to this project.
- [ ] Publish:
  ```bash
  uv publish --publish-url https://test.pypi.org/legacy/ --token <TEST_PYPI_TOKEN>
  ```
- [ ] In a clean environment, install from TestPyPI (falling back to PyPI for
      dependencies, since TestPyPI doesn't mirror them) and confirm the
      server starts:
  ```bash
  uvx --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mcp-ibge
  ```
- [ ] Confirm `MCP_IBGE_API_BASE_URL` is still restricted to the official IBGE
      domain (see [Security](security.md)).

## 7. Publish to PyPI

- [ ] Create/use a [PyPI](https://pypi.org/) account and generate an API
      token scoped to **this project only** (not the whole account).
- [ ] (Recommended medium-term) Configure
      [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC)
      between PyPI and GitHub Actions, so CI can publish without storing a
      long-lived token — see the optional workflow below.
- [ ] Publish:
  ```bash
  uv publish --token <PYPI_TOKEN>
  ```
- [ ] Check `https://pypi.org/project/mcp-ibge/`: version, description,
      rendered README, project URLs, classifiers and license are all correct.
- [ ] In a clean environment, install via `uvx mcp-ibge` (or
      `pip install mcp-ibge`) and confirm the server starts.

## 8. Create a GitHub release

```bash
git tag -a v<version> -m "v<version>"
git push origin v<version>
gh release create v<version> --title "v<version>" --notes-from-tag
```

- [ ] Tag `v<version>` exists on `main` and points at the commit that was
      built/published.
- [ ] GitHub Release created, with notes based on the new `CHANGELOG.md`
      section, marked as "Latest release".
- [ ] Once `uvx mcp-ibge` works from PyPI, remove the "not yet published"
      warning in [Installation](installation.md#option-1-uvx-published-package).

## Manual release via GitHub Actions (optional)

See
[`.github/workflows/release.yml`](https://github.com/FilipePessoa30/mcp-data-br/blob/main/.github/workflows/release.yml) —
a `workflow_dispatch` job that builds `packages/mcp_ibge` with `uv build` and
publishes to PyPI or TestPyPI, triggered manually from the Actions tab.
Requires a `PYPI_API_TOKEN` (and optionally `TEST_PYPI_API_TOKEN`) repository
secret, or Trusted Publishing configured for the `pypi` environment.
