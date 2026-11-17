[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new/template/mealie-2?utm_medium=integration&utm_source=button&utm_campaign=mealie)

# Mealie on Railway

A Railway template for [Mealie](https://github.com/mealie-recipes/mealie), the self-hosted recipe manager and meal planner.

It deploys:

| Service | Source | State |
|---|---|---|
| **Mealie** | this repo's `Dockerfile`: the official `ghcr.io/mealie-recipes/mealie:v3.31.0` image, pinned by digest, plus a small start script | volume at `/app/data` (images, backups, secrets) |
| **Postgres** | Railway's PostgreSQL 17 | volume |

Version: **Mealie v3.31.0** (`ghcr.io/mealie-recipes/mealie:v3.31.0@sha256:97e21ac96e9a8d1ee15aaf558ba3f14998936b9d6f334e40ebb4c6c2127dc12f`).

## Variables

Nothing to fill in. The template sets these on the Mealie service:

| Variable | Value |
|---|---|
| `MEALIE_ADMIN_PASSWORD` | generated 24-character password for the first admin |
| `MEALIE_ADMIN_EMAIL` | optional: email for the first admin (default `admin@example.com`) |
| `POSTGRES_URL_OVERRIDE` | `${{Postgres.DATABASE_URL}}` |
| `BASE_URL` | `https://${{RAILWAY_PUBLIC_DOMAIN}}` (used in links, emails and shared recipes) |
| `PORT` | `9000` |
| `TZ` | `UTC` (time zone for the nightly jobs) |

## After deploying

1. Open the Mealie service's **Variables** tab and copy `MEALIE_ADMIN_PASSWORD`.
2. Open the public URL and sign in as `admin` (or the email in `MEALIE_ADMIN_EMAIL`) with that password.
3. Change the admin's name, email and password under your profile. The template never overwrites them again.

Sign-up is closed (`ALLOW_SIGNUP=false`, Mealie's default): invite people from the admin's user management page, or set `ALLOW_SIGNUP=true` on the Mealie service.

### How the first admin is secured

Mealie creates its first admin as `changeme@example.com` / `MyPassword` and shows those details on the login page. On a public URL that's a known login. `bootstrap_admin.py` runs before Mealie starts: it runs Mealie's own migrations and first-run setup, then changes that admin's email and password to `MEALIE_ADMIN_EMAIL` and `MEALIE_ADMIN_PASSWORD`. It does this only while the admin still has the built-in email and password, so changes you make in Mealie are kept. Mealie refuses to start if `MEALIE_ADMIN_PASSWORD` is missing or shorter than 8 characters.

### Optional features

Add these to the Mealie service as described in [Mealie's backend configuration](https://docs.mealie.io/documentation/getting-started/installation/backend-config/): email (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`), OpenID Connect (`OIDC_*`), LDAP (`LDAP_*`) and AI features (`OPENAI_API_KEY`).

To use SQLite on the volume instead of Postgres, remove `POSTGRES_URL_OVERRIDE` (the start script then sets `DB_ENGINE=sqlite`). Move data between the two with Mealie's backup and restore page.

## Updates

The Mealie service builds from this repository. When a new Mealie release is pinned here, Railway shows an "update available" notice on your project, and you choose when to apply it. Mealie runs its database migrations on start. Read [CHANGELOG.md](CHANGELOG.md) first: breaking changes are listed first. Take a backup from Mealie's admin page before a major version update.

## Files

- `Dockerfile`: `FROM` the pinned official image, plus the start script.
- `railway-start.sh`: maps `PORT` to Mealie's `API_PORT`, picks the database engine, runs `bootstrap_admin.py`, then starts upstream's `/app/run.sh`.
- `bootstrap_admin.py`: waits for the database, runs Mealie's migrations and first-run setup, secures the first admin.
- `compose.test.yml`: local test only, not used by Railway.

The wrapper is MIT-licensed. Mealie itself is AGPL-3.0.
