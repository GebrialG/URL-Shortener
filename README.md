# URL Shortener

A minimal URL shortener built with FastAPI, SQLite, and SQLModel. Accepts a long URL, stores it, and returns a short code. Short URLs redirect back to the original via a 302 response.

I worked on this project to help me work with databases using Python as well with FastAPI in chunks. 

This project was worked on as now each piece can be tested independently and you can see the results quickly with working URL redirects. 

---

## Prerequisites

- Python 3.10 or higher
- `pip` or `pip3` available in your terminal

Check your Python version with `python3 --version` before continuing.

---

## Setup

### 1. Create and activate a virtual environment

A virtual environment keeps this project's dependencies isolated from your system Python.

```bash
python3 -m venv venv
source venv/bin/activate
```

Your terminal prompt will change to show `(venv)` when the environment is active. All subsequent commands should be run with the environment active.

### 2. Install dependencies

```bash
pip install fastapi sqlmodel uvicorn
```

- **fastapi** — the web framework
- **sqlmodel** — the ORM layer combining SQLAlchemy and Pydantic
- **uvicorn** — the server that runs your FastAPI application

### 3. Confirm installation

```bash
pip show fastapi
```

This should print the installed version. If it returns nothing, the install did not succeed.

---

## Running the Application

Start the server with uvicorn from the directory containing `URL_Shortener_complete.py`:

```bash
uvicorn URL_Shortener_complete:app --reload
```

- `URL_Shortener_complete` is the filename without `.py`
- `app` is the FastAPI instance declared inside that file
- `--reload` restarts the server automatically when you save changes to the file

You should see output similar to:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

A file called `urls.db` will be created in the same directory the first time the server starts. This is your SQLite database.

---

## Using the API

### Interactive documentation (recommended starting point)

FastAPI generates interactive documentation automatically. Open your browser and visit:

```
http://127.0.0.1:8000/docs
```

This gives you a UI where you can test both endpoints directly without needing any additional tools.

---

### Write Path — `POST /shorten`

Submits a long URL and receives a short URL in return.

**Using the `/docs` UI:** Click `POST /shorten` → `Try it out` → enter a URL in the request body → `Execute`.

**Using curl:**

```bash
curl -X POST "http://127.0.0.1:8000/shorten" \
     -H "Content-Type: application/json" \
     -d '{"long_url": "https://www.example.com/some/very/long/path"}'
```

**Expected response:**

```json
{
  "short_url": "http://127.0.0.1:8000/1"
}
```

The short code increments with each URL submitted. The first URL will return `1`, the second `2`, and so on. Codes grow to multiple characters as the integer ID grows larger.

---

### Read Path — `GET /{short_code}`

Visits a short URL and is redirected to the original.

**Using a browser:** paste `http://127.0.0.1:8000/1` directly into the address bar. The browser will follow the 302 redirect automatically and land on the original URL.

**Using curl** (the `-L` flag tells curl to follow redirects):

```bash
curl -L "http://127.0.0.1:8000/1"
```

**If the short code does not exist:**

```json
{
  "detail": "Short URL not found"
}
```

---

## Project Structure

```
URL_Shortener_complete.py   # All application code
urls.db                     # SQLite database file (created on first run)
```
---

## Stopping and Restarting

Stop the server with `Ctrl+C` in the terminal.

To reset the database and start fresh, delete `urls.db` and restart the server:

```bash
rm urls.db
uvicorn URL_Shortener_complete:app --reload
```

To deactivate the virtual environment when you are done:

```bash
deactivate
```
---

## Write Path — `POST /shorten`

Converts a long URL into a short URL.

| 1. Validate | FastAPI passes the request body through the `URLRequest` Pydantic model. The `HttpUrl` type rejects malformed URLs with a `422` before any application code runs. |

| 2. Store | A `URL` row is inserted into SQLite via a SQLModel session. The database assigns an auto-incrementing integer `id`. |

| 3. Encode | The integer `id` is passed to `to_base62()`, which converts it to a short alphanumeric code using the alphabet `0–9a–zA–Z`. |

| 4. Respond | The short code is prepended with the base URL and returned as JSON: `{ "short_url": "http://127.0.0.1:8000/g8" }` |

---

## Read Path — `GET /{short_code}`

Resolves a short code back to the original URL and redirects.

| 1. Capture | FastAPI extracts `short_code` from the URL path parameter. |

| 2. Decode | `from_base62()` converts the short code back to its integer `id` using the same `0–9a–zA–Z` alphabet. |

| 3. Look up | The SQLModel session queries SQLite for the `URL` row with that `id`. If no row is found, a `404` is raised. |

| 4. Redirect | A `302 Found` response is returned with a `Location` header pointing to the original long URL. The browser follows it automatically. |

---

## Tech Stack

| Web framework : FastAPI | Defines endpoints, validates input, injects dependencies |

| Data validation : Pydantic (`HttpUrl`) | Validates incoming URL on the write path |

| ORM : SQLModel (wraps SQLAlchemy) | Maps Python classes to database rows; handles INSERT and SELECT |

| Database : SQLite | Persists URL mappings to disk; assigns auto-incrementing IDs |

| Encoding : Custom `to_base62` / `from_base62` | Converts integer IDs to short alphanumeric codes and back |

| Server : Uvicorn | ASGI server that runs the FastAPI application |

---

## Notes

- The `echo=True` setting on the database engine prints every SQL statement to the terminal while the server is running. This is intentional for learning — you can watch the INSERT and SELECT statements execute in real time as you use the API. Remove it for a cleaner terminal in production.

- The `--reload` flag on uvicorn is for development only. It watches your files for changes and restarts the server automatically. Remove it in production.

- The base URL `http://127.0.0.1:8000` is hardcoded for local development. In production this would come from an environment variable.
- The HTTP 302 Found status indicates the resource has been temporarily moved to the URL in the `Location` header. 

Browsers follow this automatically. Search engines receiving this response will not transfer SEO value to the destination URL, which is the correct behaviour for a URL shortener where mappings may change.
