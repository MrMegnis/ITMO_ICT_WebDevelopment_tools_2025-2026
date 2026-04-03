# Практика 1.3. Миграции, ENV, GitIgnore и структура проекта

> **Для выполнения лабораторной и всех практических работ рекомендуется использовать версию Python 3.10+**

## Миграции. Alembic

При разработке проекта может возникнуть потребность добавлять новые таблицы или изменять уже существующие. Ввиду того,
что ORM SQLModel  (и, следовательно, SQLAlchemy) не предусматривает встроенный механизм миграций, необходимо
использовать готовые библиотеки позволяющие безопасно вносить изменения в таблицы и БД проекта.

В официальной документации к FastAPI [рекомендуется](https://fastapi.tiangolo.com/tutorial/sql-databases/#alembic-note)
использовать Alembic в качестве библиотеки для менеджмента изменений в базе данных. Эта библиотека разработана специально
для ORM SQLAlchemy, и совместима с SQLModel.
Подробнее можно прочитать на [официальном сайте](https://alembic.sqlalchemy.org/en/latest/).

Для интеграции Alembic в разрабатываемый проект необходимо его установить через пакетный менеджер:
```
pip install alembic  
```

Реализация механизма миграций происходит через вызов `alembic init [name]` в командной строке, где [name] — название 
папки, хранящей настройки миграций. Сгенерируем папку с миграциями и сопутствующие файлы настроек:

```
alembic init migrations 
```
В корне проекта, помимо ранее созданных файлов должна сформироваться следующая структура:
```
migratgions/
├─ versions/
├─ env.py
├─ README
├─ script.py.mako
alembic.ini
```

Сгенерировалась папка `migratgions` хранящая внутри себя папку с файлами миграций `versions`,
файл окружения БД `env.py` и шаблон генерации миграций `script.py.mako`. В корне проекта добавился файл настроек
`alembic.ini`

Для создания миграций в SQLModel необходимо добавить импорты моделей и настроить подключение к БД

1. **В файле `alembic.ini`  переменной `sqlalchemy.url` необходимо указать адрес БД, по аналогии с тем, что находится в
   файле `connection.py`**

2. **В файле `env.py` импортировать все из `models.py`  и в переменной `target_metadata` указать
   значение `target_metadata=SQLModel.metadata`**

    ??? abstract "Пример файла"
        ```py
        
        from logging.config import fileConfig

        from sqlalchemy import engine_from_config
        from sqlalchemy import pool

        from alembic import context

        from models import *

        # this is the Alembic Config object, which provides
        # access to the values within the .ini file in use.
        config = context.config

        # Interpret the config file for Python logging.
        # This line sets up loggers basically.
        fileConfig(config.config_file_name)

        # add your model's MetaData object here
        # for 'autogenerate' support
        # from myapp import mymodel
        # target_metadata = mymodel.Base.metadata
        #target_metadata = None

        target_metadata = SQLModel.metadata

        # other values from the config, defined by the needs of env.py,
        # can be acquired:
        # my_important_option = config.get_main_option("my_important_option")
        # ... etc.


        def run_migrations_offline() -> None:
            """Run migrations in 'offline' mode.

            This configures the context with just a URL
            and not an Engine, though an Engine is acceptable
            here as well.  By skipping the Engine creation
            we don't even need a DBAPI to be available.

            Calls to context.execute() here emit the given string to the
            script output.

            """
            url = config.get_main_option("sqlalchemy.url")
            context.configure(
                url=url,
                target_metadata=target_metadata,
                literal_binds=True,
                dialect_opts={"paramstyle": "named"},
            )

            with context.begin_transaction():
                context.run_migrations()


        def run_migrations_online() -> None:
            """Run migrations in 'online' mode.

            In this scenario we need to create an Engine
            and associate a connection with the context.

            """
            connectable = engine_from_config(
                config.get_section(config.config_ini_section, {}),
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
            )

            with connectable.connect() as connection:
                context.configure(
                    connection=connection, target_metadata=target_metadata
                )

                with context.begin_transaction():
                    context.run_migrations()


        if context.is_offline_mode():
            run_migrations_offline()
        else:
            run_migrations_online()

        ```

3. **В файле `script.py.mako` импортировать библиотеку `sqlmodel`** 

4. **Добавить `level` поле модели `SkillWarriorLink`** 
    ```py
    class SkillWarriorLink(SQLModel, table=True):
        skill_id: Optional[int] = Field(
        default=None, foreign_key="skill.id", primary_key=True
        )
        warrior_id: Optional[int] = Field(
        default=None, foreign_key="warrior.id", primary_key=True
        )
        level: int | None
    ```
5. **Создать файл миграций с помощью команды `alembic revision --autogenerate -m "skill added"`**
6. **Применить миграции с помощью команды `alembic upgrade head`**

Увидеть полученные изменения можно просмотрев поля таблицы через pgAdmin. Файлы миграций хранятся в 
.migrations/versions.

!!! note "Замечание"
    Использование библиотеки alembic и миграций предполагает их описание, как описываются коммиты в гите. 
    При создании файлов миграции рекомендуется писать полезную информацию об изменениях в соответствующей команде
    после маркера `-m`.


## Переменные окружения и .gitignore

При разработке приложений часто необходимо хранить ключи и пароли от БД и различного АПИ, к которому обращается
сервер. В больших проектах часто используются специальные хранилища
типа  [Hashicorp Vault](https://www.vaultproject.io/)
или [GitGub Secrets](https://docs.github.com/ru/actions/security-guides/using-secrets-in-github-actions) для
хранения подобной информации, но если разработка небольшая, то прятать важные данные можно посредством `.env` файлов.

env-файлы - специальные файлы, имеющие которые `.env` расширение. Служат для изоляции приложения от среды, где оно
запускается. Они не должны
индексироваться системами контроля версий т.к. хранят чувствительную информацию о проекте.

!!! warning "Внимание!"
    Не стоит путать env-файлы  с `venv` (Виртуальным окружением) языка Python

### .gitignore

Такие файлы необходимо реализовывать с учетом используемой системы контроля версий. При использовании Git необходимо
создать специальный .gitignore-файл, исключающий индексацию таких файлов при разработке проекта.

!!! note "Замечание"
    .gitignore-файлы используются для исключения из индексации лишних элементов внутри файловой структуры системы, не
    только файлов с чувствительной информацией. Обычно, исключаются все файлы влияющие на окружение, IDE и
    файлы БД.

У gitignore-файлов довольно простой синтаксис, ознакомится с ним можно в 
[документации](https://git-scm.com/docs/gitignore). Обычно, для типовых проектов существуют готовые шаблоны подобных 
файлов -  они легко ищутся через поисковые системы. 

??? abstract "Пример подобного файла для FastAPI-проекта"
    ```
    .idea
    .ipynb_checkpoints
    .mypy_cache
    .vscode
    __pycache__
    .pytest_cache
    htmlcov
    dist
    site
    .coverage
    coverage.xml
    .netlify
    test.db
    log.txt
    Pipfile.lock
    env3.*
    env
    docs_build
    site_build
    venv
    docs.zip
    archive.zip
    
    # vim temporary files
    *~
    .*.sw?
    .cache
    
    # macOS
    .DS_Store
    ```

Для исключения `.env` файла необходимо создать `.gitignore` файл и всписать в него строку "`*.env`", таким
образом исключив все варианты расположения файлов с подобным расширением.

После того

### .env

По аналогии с `.gitignore` необходимо создать файл `.env` в корне проекта и вписать туда переменную с чувствительными 
данными. В случае описываемого проекта это URL базы данных:

```
DB_ADMIN = postgresql://postgres:123@localhost/warriors_db
```

Чтобы получить данные из такого файла можно воспользоваться пакетом python-dotenv, для этого его надо установить:

```
pip install python-dotenv
```

После установки, в файле `connetion.py` адрес БД с использованием переменных окружения должен указываться
следующим образом:

```py
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DB_ADMIN')
```

## Практическое задание

1. Реализовать в своем проекте все улучшения, описанные в практике
2. [Разобраться](https://alembic.sqlalchemy.org/en/latest/api/config.html) как передать в alembic.ini URL базы данных с
   помощью`.env`-файла и реализовать подобную передачу.