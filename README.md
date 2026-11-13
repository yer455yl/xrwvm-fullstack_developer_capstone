# fullstack_developer_capstone

## Best Cars — Dealership Reviews Portal

A full-stack car dealership directory built from the IBM capstone starter repository. Visitors browse 50 dealerships and filter by US state or city/name. Registered users can publish purchase reviews; Django authenticates requests and supplies the author identity, while a separate sentiment service classifies review text.

### Architecture

- **React**: accessible directory, about/contact pages, sign-up, sign-in, dealer details, review submission.
- **Django**: user accounts, session authentication, CSRF protection, CarMake/CarModel administration and a proxy API.
- **Express + MongoDB**: persistent dealer/review storage, state filtering, atomic review ID allocation, validation and idempotent initial data loading.
- **Flask + NLTK VADER**: positive, negative and neutral review classification.
- **Docker Compose**: web, database API, sentiment service and MongoDB.
- **GitHub Actions**: React production build, Django tests, sentiment tests, MongoDB integration tests and web container build.

### Local development

Prerequisites: Python 3.12 and Node.js 22 (or later supported versions).

```sh
python3 -m venv .venv
.venv/bin/pip install -r server/requirements.txt -r server/djangoapp/microservices/requirements.txt
.venv/bin/python -m nltk.downloader vader_lexicon
cd server/frontend
npm ci
npm run build
cd ../..
cd server/database
npm ci
cd ../..
.venv/bin/python scripts/start_local.py
```

`start_local.py` migrates SQLite, seeds car makes/models and starts Django, Express with a real isolated MongoDB server, and the sentiment service. Open http://127.0.0.1:8000. The first local API launch downloads a MongoDB binary from its official distribution. Local MongoDB files are retained in `.local/mongodb`; application accounts are stored in `server/db.sqlite3`. Neither database is committed.

Create a local Django administrator separately:

```sh
cd server
../.venv/bin/python manage.py createsuperuser
```

No production accounts or passwords are embedded in the source. Register a test user through the application.

### Docker deployment

Set environment variables in a private `.env` file (do not commit it):

```dotenv
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

```sh
docker compose up --build
# Optional administrator account:
docker compose exec web python manage.py createsuperuser
```

SQLite and MongoDB are persisted in named volumes. The web port binds to loopback for local use. For cloud deployment, set the allowed host and trusted HTTPS origin to the assigned domain and configure routing/TLS in the hosting platform. The Dockerfiles and Compose configuration are provided; a successful cloud deployment must be verified separately.

### API endpoints

| Service | Endpoint | Purpose |
|---|---|---|
| Django | GET `/djangoapp/session` | Session identity and CSRF cookie |
| Django | POST `/djangoapp/register` | Register an account |
| Django | POST `/djangoapp/login` | Authenticate |
| Django | POST `/djangoapp/logout` | End session |
| Django | GET `/djangoapp/get_dealers[/<state>]` | Dealer directory |
| Django | GET `/djangoapp/dealer/<id>` | Dealer details |
| Django | GET `/djangoapp/reviews/dealer/<id>` | Reviews with sentiment |
| Django | GET `/djangoapp/get_cars` | Car makes/models |
| Django | POST `/djangoapp/add_review` | Authenticated purchase review |
| Express | GET `/fetchDealers[/<state>]` | Raw dealer data |
| Express | GET `/fetchDealer/<id>` | Raw single dealer data |
| Express | GET `/fetchReviews/dealer/<id>` | Raw reviews |
| Express | POST `/insert_review` | Internal review persistence |
| Sentiment | GET `/analyze/<text>` | Sentiment label and compound score |

The Express API is intended for the private application network. Do not expose its write endpoint directly to the public Internet. Public review submissions are authenticated by Django.

### Validation

```sh
cd server/frontend && npm ci && npm run build
cd ../.. && .venv/bin/python server/manage.py test djangoapp
cd server/database && npm ci && npm test
cd ../djangoapp/microservices && ../../../.venv/bin/python -m unittest test_sentiment.py
```

The MongoDB tests check filtering, invalid IDs, posting/persistence, concurrent IDs and retaining data after reconnect. Django tests cover authentication, duplicate/weak registrations, CSRF, author identity, validation and unavailable backend services. Sentiment tests cover positive, negative and neutral input.

### Submission evidence

Screenshots under `evidence/local/` demonstrate the locally running implementation. They are **local evidence**, not proof of Skills Network lab execution or cloud deployment. Before course submission, capture the required deployment screenshots in the actual assigned environment and verify GitHub Actions has succeeded. Use the checklist in `SUBMISSION_STATUS.md` to track outstanding evidence. Never substitute a local screenshot for a claimed cloud deployment result.

### Attribution

Starter code, sample images and sample dealer/review data: [IBM Developer Skills Network](https://github.com/ibm-developer-skills-network/xrwvm-fullstack_developer_capstone), Apache-2.0 (see LICENSE). Implementation, test and documentation assistance: OpenAI Codex, November 13, 2026. Review all generated work and disclose assistance as required by your course.
