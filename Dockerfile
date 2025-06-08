# [stage__base]-[BEGIN]================================================
FROM python:3.13.1-slim AS base

ENV PYTHONUNBUFFERED=1
ARG WORKDIR=/wd
ARG USER=user

# Оновлення системи та базових пакетів
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt update && apt upgrade --yes && apt install -y libmagic1

WORKDIR ${WORKDIR}

# Створення користувача без пароля (system user)
RUN useradd --system ${USER} && chown --recursive ${USER} ${WORKDIR}
# [stage__base]-[END]================================================

# [stage__builder]-[BEGIN]===============================================
FROM base AS builder

# Копіюємо uv (у тебе воно в образі ghcr.io/astral-sh/uv:0.6.13)
COPY --from=ghcr.io/astral-sh/uv:0.6.13 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/opt/uv-cache/

# Встановлення залежностей через uv sync (передбачає uv.lock і pyproject.toml)
RUN --mount=type=cache,target=/opt/uv-cache/ \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=.python-version,target=.python-version \
    uv sync --frozen
# [stage__builder]-[END]================================================

# [stage__final]-[BEGIN]================================================
FROM base AS final

ARG USER=user
ARG WORKDIR=/wd
ARG VENV_DIR=${WORKDIR}/.venv

# Копіюємо віртуальне середовище з builder stage
COPY --from=builder ${VENV_DIR} ${VENV_DIR}

# Копіюємо скрипти запуску та код застосунку з потрібними правами
COPY --chown=${USER} --chmod=555 docker/app/entrypoint.sh /entrypoint.sh
COPY --chown=${USER} --chmod=555 docker/app/start.sh /start.sh
#COPY --chown=${USER} --chmod=555 docker/app/init.sh /init.sh
#COPY --chown=${USER} --chmod=555 docker/app/celery_worker_start.sh /celery_worker_start.sh
#COPY --chown=${USER} --chmod=555 docker/app/celery_beat_start.sh /celery_beat_start.sh

COPY --chown=${USER} manage.py manage.py
COPY --chown=${USER} templates/ templates/
COPY --chown=${USER} core/ core/
COPY --chown=${USER} apps/ apps/

USER ${USER}

ENV PATH="${VENV_DIR}/bin:$PATH"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["./start.sh"]
# [stage__final]-[END]==================================================
