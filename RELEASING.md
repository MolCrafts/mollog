# Releasing

This repository uses a static version in `pyproject.toml`.

## PyPI Trusted Publisher

This repository is set up to publish through PyPI trusted publishing from GitHub Actions.
No PyPI API token should be stored in GitHub secrets for the normal release flow.

Configure the trusted publisher in PyPI with:

- Project name: `molcrafts-mollog`
- Owner: `MolCrafts`
- Repository: `mollog`
- Workflow: `release.yml`
- Environment: `pypi`

The GitHub repository must also have an environment named `pypi`.

## Release Checklist

1. Ensure `pyproject.toml` has the intended version.
2. Optionally refresh `docs/release-notes.md` for user-facing highlights
   (full history is git log / tags — no `CHANGELOG.md`).
3. Run the full test suite:

   ```bash
   pytest -q
   ```

4. Tag the release:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

5. Wait for the `release` workflow: it re-runs lint and the tests on the tag,
   checks the tag against `pyproject.toml`, builds, and publishes to PyPI via
   trusted publishing. Run it by hand (`workflow_dispatch`) for a dry run that
   builds without uploading.
6. Publish a GitHub release for the tag; draft notes from `git log` since the
   previous tag (or from `docs/release-notes.md` if you keep highlights there).

## Documentation Release

If documentation dependencies are installed:

```bash
zensical build
```

Deploy the generated `site/` directory with Cloudflare Pages.

Recommended Cloudflare Pages settings:

- Framework preset: `None`
- Build command: `uv run zensical build`
- Build output directory: `site`
