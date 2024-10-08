# ZonPrep OCR Parser.

ZonPreps OCR Parser.

Most of this project is going to be in the folder `apps/zonprep_file_parsing`.

## Installation

```bash
python -m venv ./venv
pip install -r dev-requirements.txt
```

## Set up database

Create a database named `zon_prep_ocr_project`.

```
createdb zon_prep_ocr_project
```

Create database migrations:

```
./manage.py makemigrations
```

Create database tables:

```
./manage.py migrate
```

## Running server

```bash
./manage.py runserver
```

## Building front-end

To build JavaScript and CSS files, first install npm packages:

```bash
npm install
```

Then build (and watch for changes locally):

```bash
npm run dev-watch
```

## Running Celery

Celery can be used to run background tasks.

Celery requires [Redis](https://redis.io/) as a message broker, so make sure
it is installed and running.

You can run it using:

```bash
celery -A zon_prep_ocr_project worker -l INFO --pool=solo
```

Or with celery beat (for scheduled tasks):

```bash
celery -A zon_prep_ocr_project worker -l INFO -B --pool=solo
```

Note: Using the `solo` pool is recommended for development but not for production.

## Updating translations

**Docker:**

```bash
make translations
```

**Native:**

```bash
./manage.py makemessages --all --ignore node_modules --ignore venv
./manage.py makemessages -d djangojs --all --ignore node_modules --ignore venv
./manage.py compilemessages
```

## Installing Git commit hooks

To install the Git commit hooks run the following:

```shell
$ pre-commit install --install-hooks
```

Once these are installed they will be run on every commit.

For more information see the [docs](https://docs.saaspegasus.com/code-structure.html#code-formatting).

## Running Tests

To run tests:

```bash
./manage.py test
```

Or to test a specific app/module:

```bash
./manage.py test apps.utils.tests.test_slugs
```

On Linux-based systems you can watch for changes using the following:

```bash
find . -name '*.py' | entr python ./manage.py test apps.utils.tests.test_slugs
```
