# Training-Environment---Blind-ORM-Leak

## Overview

A new internal user search system has been deployed.  
The development team proudly introduced a flexible search feature, but they believe that administrator notes are never exposed externally.

This environment is a training setup designed to demonstrate a **Blind ORM Leak** vulnerability, where user input is directly reflected into ORM filter fields and operators through a search API.  
An attacker can use differences in search result counts as an oracle to infer the flag stored in the administrator's private note.

---

## Directory Structure

```text
Training-Environment---Blind-ORM-Leak/
├── app/                  # Public-facing vulnerable web application
├── internal/             # Internal-only flag source service
├── docs/                 # Write-ups and exploit documentation
├── solver/               # Intended solver script
├── docker-compose.yml    # Environment launch file
├── README.md
└── README-EN.md
```

---

## Service Information

| Item      | Value                                                              |
| --------- | ------------------------------------------------------------------ |
| Web App   | http://localhost:8080                                              |
| Objective | Obtain the flag stored in the administrator account's private note |

---

## How to Run

### Start the environment

```bash
docker compose up -d --build
```

### Stop the environment

```bash
docker compose down -v
```

---

## Goal

Obtain the flag in `WSL{...}` format stored in `admin.secret_note`.
