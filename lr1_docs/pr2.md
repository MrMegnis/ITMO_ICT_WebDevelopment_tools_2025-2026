# Практика 1.2. Настройка БД, SQLModel и миграции через Alembic

> **Для выполнения лабораторной и всех практических работ рекомендуется использовать версию Python 3.10+**

## SQLModel и ORM


Для того чтобы реализовывать взаимодействие с БД не чистыми SQL-запросами 
при разработке приложений обычно используют ORM. При работе с Django в качестве
ORM выступала библиотека, интегрированная во фреймворк, без возможности ее отдельного 
использования в сторонних разработках. Т.к. FastAPI предоставляет разработчику наиболее
гибкую настройку всего проекта, то встроенных ORM такой фреймворк не предусматривает.
При этом от разработчиков существует интегрируемая в фреймворк библиотека, 
а также ряд рекомендованных ORM для использования.

### SQLModel. Реализация и подключение
!!! warning "Внимание!"
    Далее будет описано как внедрять ORM SQLModel внутрь проекта на FastAPI.
    SQLModel - это библиотека, использующая "под капотом" SQLAlchemy как движок,
    и содержит в себе в упрощенном для разработчика виде множество методов из SQLAlchemy.
    При проблемах, возникающих при реализации БД чаще всего, ошибки возникают из-за 
    некорректного использования базовой ORM, поэтому, в случае возникновения трудностей при разработке
    рекомендуется также обращаться к [документации исходной ORM](https://www.sqlalchemy.org/)

От разработчиков FastAPI, Помимо исходного фреймворка существует также ряд рекомендованных библиотека
(таких как Pydantic), упрощающих реализацию серверного API-приложения. Одной из таких библиотек
является SQLModel, предоставляющую "гибкую" ORM, основывающуюся на Pydantic и SQLAlchemy.
Такая библиотека позволяет реализовывать таблицы в БД посредством инструментов аннотирования на
языке Python. Как и FastAPI содержит подробную [документацию](https://sqlmodel.tiangolo.com/) включая стандартные
решения для большинства задач.

Для того чтобы установить библиотеку достаточно в командной строке при инициализированном виртуальном окружении написать
следующую команду:

```
pip install sqlmodel
```
!!! danger "Обратите внимание!"
    В рамках практических и лабораторных работ будет использоваться СУБД PostgreSQL. Установить ее можно через 
    [официальный сайт](https://www.postgresql.org/download/). Также необходимо установить драйвер СУБД для языка Python:
    ```
    pip install psycopg2-binary
    ```

После установки всех зависимостей необходимо реализовать файл с подключением к БД. В подобном файле описывается способ
подключения к БД и реализованы дополнительные методы, упрощающие инициализацию и взаимодействие с БД. Рекомендуется 
называть такой файл db.py или connection.py:

**connection.py**
```py
from sqlmodel import SQLModel, Session, create_engine

db_url = 'postgresql://postgres:123@localhost/warriors_db'
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

```

- `db_url` и `engine` создают подключение к БД, эта реализация аналогично той, что использует ORM SQLAlchemy
  _(неудивительно, ведь SQLModel является надстройкой над этой библиотекой)_. Для подробной информации, что
  такое `db_url`
  и как происходит подключение к движку БД, рекомендуется обратиться к
  [документации](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls).
- параметр `echo=True` в методе  `create_engine` включает вывод всех осуществляемых SQL-запросов в командную строку.
- метод `init_db` используется для инициализации всех таблиц в созданной базе данных, его использование будет 
  представлено ниже
- метод-генератор `get_session` используется для получения сессий, необходимых при выполнении запросов к БД через 
  `Dependencies`. О том как использовать этот метод будет рассказано в следующей главе.

### Создание моделей

Чтобы классы моделей можно было инициализировать в БД, необходимо в параметры класса передать в качестве наследника
класс `SQLModel` и в аргументах указать `table=true`

??? abstract "Обновленный файл models.py "
    ```py
    from enum import Enum
    from typing import Optional, List
    
    #from pydantic import BaseModel
    from sqlmodel import SQLModel, Field, Relationship
    
    
    class RaceType(Enum):
        director = "director"
        worker = "worker"
        junior = "junior"
    
    
    class SkillWarriorLink(SQLModel, table=True):
        skill_id: Optional[int] = Field(
            default=None, foreign_key="skill.id", primary_key=True
        )
        warrior_id: Optional[int] = Field(
            default=None, foreign_key="warrior.id", primary_key=True
        )
    
    
    class Skill(SQLModel, table=True):
        id: int = Field(default=None, primary_key=True)
        name: str
        description: Optional[str] = ""
        warriors: Optional[List["Warrior"]] = Relationship(back_populates="skills", link_model=SkillWarriorLink)
    
    
    class Profession(SQLModel, table=True):
        id: int = Field(default=None, primary_key=True)
        title: str
        description: str
        warriors_prof: List["Warrior"] = Relationship(back_populates="profession")
    
    
    class Warrior(SQLModel, table=True):
        id: int = Field(default=None, primary_key=True)
        race: RaceType
        name: str
        level: int
        profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")
        profession: Optional[Profession] = Relationship(back_populates="warriors_prof")
        skills: Optional[List[Skill]] = Relationship(back_populates="warriors", link_model=SkillWarriorLink)

    ```
В рамках реализации связей в базе данных была создана ассоциативная сущность `SkillWarriorLink`. Всем таблицам были 
указаны первичные ключи через класс `Field`. С помощью этого же класса были описаны внешние ключи к таблицам.

!!! note "Полезные ссылки"
    Как можно заметить, в таблицах были созданы связи "Один-ко-многим" и "Многие-ко-многим". Чтобы понять логику работы
    отношений в SQLModel и SQLAlchemy рекомендуется прочитать про
    [внешние ключи](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/define-relationships-attributes/),
    [реализацию "многие ко многим"](https://sqlmodel.tiangolo.com/tutorial/many-to-many/create-models-with-link/) и
    [обратные связи (аналог related_name в django)](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/back-populates/)
    в документации.

Чтобы описанные таблицы были созданы необходимо добавить в  `main.py` специальный метод `on_startup` с декоратором
`on_event` вызывающий внутри их инициализацию.
```py
@app.on_event("startup")
def on_startup():
    init_db()
```

Если все было реализовано корректно, то после запуска приложения в консоли выведется SQL-запрос на создание сущностей,
описанных в  `models.py`
??? abstract "Лог созданных таблиц"
    ```sql
    CREATE TABLE skill (
            id SERIAL NOT NULL,
            name VARCHAR NOT NULL,
            description VARCHAR,
            PRIMARY KEY (id)
    )
    
    
    
    CREATE TABLE profession (
            id SERIAL NOT NULL,
            title VARCHAR NOT NULL,
            description VARCHAR NOT NULL,
            PRIMARY KEY (id)
    )
    
    
    
    CREATE TABLE warrior (
            id SERIAL NOT NULL,
            race racetype NOT NULL,
            name VARCHAR NOT NULL,
            level INTEGER NOT NULL,
            profession_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY(profession_id) REFERENCES profession (id)
    )
    
    
    
    CREATE TABLE skillwarriorlink (
            skill_id INTEGER NOT NULL,
            warrior_id INTEGER NOT NULL,
            PRIMARY KEY (skill_id, warrior_id),
            FOREIGN KEY(skill_id) REFERENCES skill (id),
            FOREIGN KEY(warrior_id) REFERENCES warrior (id)
    )
    
    ```

## Запросы

После реализации таблиц необходимо обновить все ранее созданные эндпоинты. Так как теперь вместо
виртуальной базы данных будет использоваться настоящая, то необходимо понять логику взаимодействия с
ORM.

Ранее, в файле `connection.py` был создан генератор для получений объекта сессий в БД. Такой объект позволяет выполнять
запросы к базе данных через специальные методы библиотек SQLModel и SQLAlchemy.

Для того чтобы получать подобный объект внутри разрабатываемых API-функций необходимо в них указывать параметр  
`session` c изначальным значением в виде класса `Depends` с аргументом в виде ссылки на генератор `get_session`:
```py
session=Depends(get_session)
```
Класс Depends отвечает за выполнение внедрения зависимостей в приложениях FastAPI. Класс Depends принимает функцию в 
качестве аргумента и передается в качестве аргумента функции в маршруте, требуя, чтобы 
условие зависимости было выполнено до инициализации любой операции внутри тела API-метода.
Подробнее о том как можно работать с зависимостями описано в 
[официальной документации](https://fastapi.tiangolo.com/tutorial/dependencies/)

### Создание объектов

Для реализации POST-запроса записывающий новый объект воина в БД необходимо:

- создать новую модель для POST-запросов к объекту
- Обновить изначально разработанный эндпоинт, добавляющий запись воина во временную БД

Ввиду того, что при создании нового объекта некоторые поля не всегда надо указывать
_(таким полем может быть, например, первичный ключ)_, возникает необходимость в добавлении новых моделей, обрабатывающих
запросы. Подобные модели, по факту, являются аналогами Pydantic-объектов, сериализирующие данные в ту и другую сторону и
в БД не реализуются.

!!! note "Замечание"
    За реализацию конкретной модели в БД отвечает аргумент table=True, при описании класса
Для модели воина, таким образом, можно реализовать еще одну базовую модель `WarriorDefault`, не имеющую id и ссылок
на многие-ко многим. Также от такой модели можно отнаследоваться основной моделью, реализующейся в базе данных 
вместо указания в поле наследования `SQLModel`. В таком случае достаточно дописать недостающие поля.

```py
class WarriorDefault(SQLModel):
    race: RaceType
    name: str
    level: int
    profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")


class Warrior(WarriorDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    profession: Optional[Profession] = Relationship(back_populates="warriors_prof")
    skills: Optional[List[Skill]] = Relationship(back_populates="warriors", link_model=SkillWarriorLink)
```

Используя классы `WarriorDefault` и `Warrior` можно переписать POST-запрос `/warrior` для новой логики:

```py
@app.post("/warrior")
def warriors_create(warrior: WarriorDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                     "data": Warrior}):
    warrior = Warrior.model_validate(warrior)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return {"status": 200, "data": warrior}

```

Метод [model_validate](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_validate) загружает
упрощенную модель в основную, связанную с БД. Далее обработанный объект передается в сессию с помощью `session.add`,
изменения сохраняются через метод `commit` и данные для объекта обновляются до актуальных методом `refresh`

!!! note "Полезные ссылки"
    В документации для SQLModel есть несколько статей, подробнее рассказывающих о создании объектов и POST-запросах:

    1. [Cоздание объектов через сессии](https://sqlmodel.tiangolo.com/tutorial/insert/)
    2. [Пример API с созданием объекта](https://sqlmodel.tiangolo.com/tutorial/fastapi/simple-hero-api/)
    3. [Как описывать возвращаемые объекты](https://sqlmodel.tiangolo.com/tutorial/fastapi/response-model/)

### Получение объектов и списки.

Аналогичным образом необходимо обновить list и GET запросы для объектов, чтобы в дальнейшем данные брались из БД.

```py
@app.get("/warriors_list")
def warriors_list(session=Depends(get_session)) -> List[Warrior]:
    return session.exec(select(Warrior)).all()


@app.get("/warrior/{warrior_id}")
def warriors_get(warrior_id: int, session=Depends(get_session)) -> Warrior:
    return session.exec(select(Warrior).where(Warrior.id == warrior_id)).first()
```

В коде выше реализованы два метода: на получение списка воинов и для получения воина по id. Для выполнения
SELECT-запроса используется улучшенная в SQLModel функция `select` из библиотеки SQLAlchemy, в которую передается объект
модели БД.
Далее, через объект сессии вызывается метод `exec`, возвращающий генератор значений из таблицы по отправленному
SELECT-запросу. Если необходимо произвести фильтрацию по значению, то к методу `select` необходимо применить метод
`where`  с аргументами в виде поля для фильтрации, взятого из модели БД, и аргумента.

Чтобы сразу получать какое-то конкретное значение необходимо в случае запроса на список вызывать метод `all()` - он
возвращает
python-список объектов. В случае единичного GET-запроса необходимо вызвать метод `first()`.

!!! note "Полезные ссылки"
    Полезные ссылки из документации, позволяющие лучше разобраться в том как выполнять SELECT-запросы в ORM:

    1. [SQLAlchemy и select](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html)
    2. [SQLAlchemy и where](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#the-where-clause)
    3. [Чтение одной стороки из БД в SQLModel](https://sqlmodel.tiangolo.com/tutorial/one/)
    4. [SELECT в SQLModel и разница с SQLAlchemy](https://sqlmodel.tiangolo.com/tutorial/select/) 
    5. [WHERE в SQLModel](https://sqlmodel.tiangolo.com/tutorial/where/) 

### Обновление и Внешние ключи.
Схожим образом необходимо изменить функции обновления данных.
Теперь, вместо PUT-метода в коде API будет использоваться PATCH для частичного обновления данных.
```py
@app.patch("/warrior{warrior_id}")
def warrior_update(warrior_id: int, warrior: WarriorDefault, session=Depends(get_session)) -> WarriorDefault:
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    warrior_data = warrior.model_dump(exclude_unset=True)
    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior

```
Так же как и для создания объекта при его изменении используется базовая модель `WarriorDefault`.
Для получения записи существующей в единичном экземпляре можно использовать также метод `get`, в который
надо передать модель таблицы и идентификатор объекта. По сравнению со способами получения одиночных записей 
описанных выше такой запрос легче читать при анализе кода.

В коде происходит проверка на существование объекта, если такого не существует то возвращается 404 код.
Подробнее про обработку ошибок можно почитать в [документации](https://fastapi.tiangolo.com/tutorial/handling-errors/)

Пришедшая модель преобразуется в формат json через метод 
[`model_dump` с параметром `exclude_unset`](https://fastapi.tiangolo.com/tutorial/body-updates/#using-pydantics-exclude_unset-parameter)
Затем, для модели устанавливаются новые поля и она сохраняется.

API для обновления реализовано не просто так: т.к. в разработке присутствуют не только модели воинов, но и другие
связанные модели,
то надо реализовать возможность создавать и отображать связи между объектами. На примере с моделью
профессий можно реализовать API с использованием отношений внутри разрабатываемого приложения.

Для начала необходимо создать основное API по аналогии с воинами:

```py
@app.get("/professions_list")
def professions_list(session=Depends(get_session)) -> List[Profession]:
    return session.exec(select(Profession)).all()


@app.get("/profession/{profession_id}")
def profession_get(profession_id: int, session=Depends(get_session)) -> Profession:
    return session.get(Profession, profession_id)


@app.post("/profession")
def profession_create(prof: ProfessionDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                     "data": Profession}):
    prof = Profession.model_validate(prof)
    session.add(prof)
    session.commit()
    session.refresh(prof)
    return {"status": 200, "data": prof}

```
!!! note "Замечание"
    Как можно заметить, теперь запрос на одиночный объект использует метод `get` ля получения записи из базы

Если создать профессию и привязать ее идентификатор к воину, а после этого запросить объект воина, вернется следующий 
результат:
```Json
{
  "race": "junior",
  "profession_id": 2,
  "level": 1,
  "name": "Yuuko Aioi",
  "id": 11
}
```

Как видно, возвращается идентификатор профессий, но не возвращается вложенный объект профессии. Для
того чтобы это исправить, необходимо воспользоваться специальным
полем [response_model](https://sqlmodel.tiangolo.com/tutorial/fastapi/response-model/)
позволяющее сериализовать запись из БД в соответствии с указаным значением в виде класса модели.
Из-за особенностей связанных с реализацией отношений в SQLModel воспользоваться стандартной моделью 
`Warrior' не выйдет, необходимо реализовать модель-наследник, описывающую связь с профессией повторно

**Код модели в models.py**

```py
class WarriorProfessions(WarriorDefault):
    profession: Optional[Profession] = None
```

**Код обновленного GET-эндпоинта**
```py
@app.get("/warrior/{warrior_id}", response_model=WarriorProfessions)
def warriors_get(warrior_id: int, session=Depends(get_session)) -> Warrior:
    warrior = session.get(Warrior, warrior_id)
    return warrior
```

Теперь при вызове  `warriors_get` будет возвращаться результат с вложенным объектом профессии:

```Json
{
  "race": "junior",
  "name": "Yuuko Aioi",
  "level": 1,
  "profession_id": 2,
  "profession": {
    "id": 2,
    "title": "baka",
    "description": "most non-intelligent human being"
  }
}
```

!!! note "Полезные ссылки"
    Документация по обновлению объектов и их связей:

    1. [Про обновления](https://sqlmodel.tiangolo.com/tutorial/fastapi/update/)
    2. [Обновление связанных моделей](https://sqlmodel.tiangolo.com/tutorial/connect/update-data-connections/)
    3. [Как реализуется отображение отношений в FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/relationships/)


### Удаление

API для удаления схоже по логике с обновлением. Пример кода удаления объектов воинов:
```py
@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}

```
Такой код вызывает метод `delete` удаляющий запись о воине с переданным id из БД.
!!! warning "Внимание!"
    SQLModel предполагает, что при удалении связанных таблиц, все ссылки будут обнуляться, а объекты 
    сохраняться. Для того чтобы изменить поведение `ON DELETE` для связанных моделей, необходимо указывать следующую 
    конструкцию в агрументах класса `Relationship` при создании модели:
    ```py
    sa_relationship_kwargs={
            "cascade": "all, delete",
        },
    ```
    подробнее о том как реализуются `ON DELETE` взаимодействия и какие параметры можно указывать в словарь, описанный 
    выше, рассказано в [документации к SQLAlchemy](https://docs.sqlalchemy.org/en/14/orm/cascades.html#using-foreign-key-on-delete-cascade-with-orm-relationships)

## Практическое задание

1. **Если реализуется по модели из практического задания**:
    1. Пошагово реализовать проект и методы, описанные в практике
    2. Создать API и модели для умений воинов и их ассоциативной сущности, вложено отображать умения при запросе воина

2. **Если реализуется по модели из своего варианта**:
    1. Пошагово реализовать подключение к БД, АПИ и модели, на основании своего варианта основываясь на действиях
       в практике
    2. Сделать модели и API для many-to-many связей с вложенным отображением.