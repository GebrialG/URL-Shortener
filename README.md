# URL Shortener

A minimal URL shortener built with FastAPI, SQLite, and SQLAlchemy. Accepts a long URL, stores it, and returns a short code. Short URLs redirect back to the original via a 302 response*.

---

## Write Path — `POST /shorten`

Converts a long URL into a short URL.

| 1. Validate | FastAPI passes the request body through the `URLRequest` Pydantic model. The `HttpUrl` type rejects malformed URLs with a `422` before any application code runs. |

| 2. Store | A `URL` row is inserted into SQLite via a SQLAlchemy session. The database assigns an auto-incrementing integer `id`. |

| 3. Encode | The integer `id` is passed to `to_base62()`, which converts it to a short alphanumeric code using the alphabet `0–9a–zA–Z`. |

| 4. Respond | The short code is prepended with the base URL and returned as JSON: `{ "short_url": "http://127.0.0.1:8000/g8" }` |

---

## Read Path — `GET /{short_code}`

Resolves a short code back to the original URL and redirects.

| 1. Capture | FastAPI extracts `short_code` from the URL path parameter. |

| 2. Decode | `from_base62()` converts the short code back to its integer `id` using the same `0–9a–zA–Z` alphabet. |

| 3. Look up | The SQLAlchemy session queries SQLite for the `URL` row with that `id`. If no row is found, a `404` is raised. |

| 4. Redirect | A `302 Found` response is returned with a `Location` header pointing to the original long URL. The browser follows it automatically. |

---

## Tech Stack

| Web framework | FastAPI | Defines endpoints, validates input, injects dependencies |

| Data validation | Pydantic (`HttpUrl`) | Validates incoming URL on the write path |

| ORM | SQLAlchemy (via SQLModel) | Maps Python classes to database rows; handles INSERT and SELECT |

| Database | SQLite | Persists URL mappings to disk; assigns auto-incrementing IDs |

| Encoding | Custom `to_base62` / `from_base62` | Converts integer IDs to short alphanumeric codes and back |

---

*: The HTTP 302 Found redirection response status code indicates that the requested resource has been temporarily moved to the URL in the Location header.

A browser receiving this status will automatically request the resource at the URL in the Location header, redirecting the user to the new page. Search engines receiving this response will not attribute links to the original URL to the new resource, meaning no SEO value is transferred to the new URL.
