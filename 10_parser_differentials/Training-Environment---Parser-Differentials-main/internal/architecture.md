# Internal Architecture Notes

This document explains the intentionally vulnerable architecture used in this training environment.

## Request Flow

```text
Client
  |
  v
API Gateway policy layer
  - raw URL path prefix check
  - JSON duplicate keys resolved by first-key-wins parser
  |
  v
Legacy Backend router
  - repeated URL decoding
  - path normalization
  - JSON duplicate keys resolved by last-key-wins parser
```

## Gateway Rules

The gateway allows a request only when:

```text
raw_path starts with /api/public/
```

For JSON requests, it additionally requires:

```text
scope == public
```

The gateway parser is implemented with `object_pairs_hook` and intentionally keeps the first duplicate JSON key.

## Backend Rules

The backend first normalizes paths like this:

```python
decoded = unquote(unquote(raw_path))
normalized = posixpath.normpath(decoded)
```

The backend JSON parser uses Python's default `json.loads()`, which keeps the last duplicate key value.

## Intended Security Lesson

Parser differentials become vulnerabilities when security checks are performed on one interpretation of a request, but the actual action is performed on another interpretation.
