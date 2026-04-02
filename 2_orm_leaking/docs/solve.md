# Intended Solve

## Vulnerability
The vulnerable endpoint is:

```http
GET /api/users?field=<field>&op=<operator>&value=<value>
```

The backend constructs a Prisma `where` object from untrusted input:

```js
const where = {
  [field]: {
    [op]: value
  }
};
```

This allows an attacker to query unintended fields such as `secret_note`.

## Oracle
Even though the server only returns `username`, `email`, and `role`, the `total` field reveals whether the condition matched at least one row.

## Example

```bash
curl "http://localhost:8080/api/users?field=secret_note&op=startsWith&value=WSL{orm"
```

A response with `total: 1` means the prefix is correct.

## Solver
Use the script in `solver/solve.py` to brute-force the value one character at a time.

## Remediation
- Allowlist searchable fields.
- Allowlist allowed operators.
- Never let user input shape the ORM query object directly.
- Separate display logic from query construction.
