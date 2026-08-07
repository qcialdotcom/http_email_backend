# Release Guide

This guide describes the standard process for publishing a new http_email_backend release to PyPI.

Recommended versioning:

- Alpha: `0.1.0a1`
- Beta: `0.1.0b1`
- RC: `0.1.0rc1`
- Stable: `1.0.0`

## Create Git Tag

Create the release tag for the version you are publishing:

```bash
git tag v0.1.0a1
```

## Push Tag

Push the release tag so the publish workflow can pick it up:

```bash
git push origin v0.1.0a1
```

This triggers the GitHub Actions publish workflow.

## Verify Release

Confirm the package is available on PyPI:

[https://pypi.org/project/http_email_backend/](https://pypi.org/project/http_email_backend/)

Install the published package locally:

```bash
pip install http_email_backend
```

For pre-release versions:

```bash
pip install --pre http_email_backend
```

## Recommended Release Flow

For a typical release, run the following commands in order:

```bash
git tag v0.1.0a1

git push origin v0.1.0a1
```

One more important thing:

Since this is an alpha release, users usually need:

```bash
pip install --pre http_email_backend
```

Because pip ignores pre-releases by default unless you explicitly allow them.
