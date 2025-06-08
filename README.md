# Ricepe finder

---

## 🏠 Pre-alfa

Recipe site for find eat.

### ▶️ Run

Make all actions needed for run homework from zero. Including configuration.

```shell
just homework-i-docker-i-run
```

### 🚮 Purge

Make all actions needed for run homework from zero.

```shell
just homework-i-docker-i-purge
```

---

## 🛠️ Development

### Install just

You must have [just] installed on your system for run different commands.

If you don't have [just] installed, you can find commands for installation here:

- [just.just](just/dev/just.just)

After installing [just], you can see all available commands with:

```bash
just --list
```

[just]: https://github.com/casey/just

### Initialize development environment

Create venv, register pre-commit hooks, and install dependencies:

```bash
just init-i-dev
```

## Install PostgreSQL

For this project to run locally,
you'll need a PostgreSQL database server.
On most Linux distributions (like Ubuntu/Debian),
you can install it using your package manager.
This process typically sets up the PostgreSQL server and creates
a default postgres system user.

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

After installation, the PostgreSQL service should start automatically. You can verify its status to ensure it's running:

```bash
sudo systemctl status postgresql@<VERSION>-main.service
```

Replace <VERSION> with the specific PostgreSQL version installed on your system (e.g., 14 or 15). You should see Active:
active (running) in the output.

### Initialize development environment

Create venv, register pre-commit hooks, and install dependencies:

```bash
just init-i-dev
```