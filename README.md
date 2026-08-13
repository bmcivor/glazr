# glazr

A donut ordering and delivery service. Django REST API, React frontend,
Postgres, and Redis pub/sub for asynchronous messaging.


## Getting started

From a clean checkout:

```bash
docker compose up
```

- Frontend: http://localhost:5173
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

The catalogue starts empty. Create donuts through the admin, or POST to `/api/donuts/`

DRF's browsable form at http://localhost:5173/api/donuts/ is the quickest way.

For the admin:

```bash
docker compose run --rm backend python manage.py createsuperuser
```

There is no seeding of additional users in the application spin up.

You can create a donut with a cURL request so there is data.

```bash
curl -X POST http://localhost:8000/api/donuts/ \
  -H "Content-Type: application/json" \
  -d '{"donut_code":"CHOCOLATE","description":"A chocolatey goodness","price":"9.50","available":true}'
```

## Important Notes

- Containers run as uid `1000` so if your host user has differing user and group id's.
  Generated files from within the container will be owned by the wrong user. (Bad Dockerfile
  design here to not run things as root in the containers)


## Tests

```bash
./scripts/test.sh
```

Runs the tests in both React Land and Python Land. To specify a side, the arguments `backend` or `frontend`
can be used.

```bash
./scripts/test.sh backend
```

This spins up a dedicated test image with dev dependencies to run the tests in. Linting and tooling
is also available to be run through here.


## Linting and type checking

```bash
./scripts/lint.sh
```

Runs ruff format, ruff check and mypy on the backend, eslint and prettier on
the frontend. `./scripts/fix.sh` is the write counterpart to apply the suggested
fixes output by the included tooling.

```bash
./scripts/fix.sh
```

DRF functionality has been ignored mostly in the mypy config found in pyproject.toml,
just for time saving reasons

## Messaging

Redis pub/sub, on two channels: `glazr.events` outbound, `glazr.inbound`
inbound.

**Publishing.** `glazr/messaging.py` defines an `EventPublisher` protocol with
a Redis implementation and a recording one for tests. Application code calls `publish_event`.

This wraps the publish in `transaction.on_commit` so nothing is announced for a transaction that then rolls back.

Four events go out:

- `donut.created`
- `donut.updated`
- `order.created`
- `order.dispatched`

Publishing happens in the service layer and the viewset hooks, not in
`post_save` signals.

This is because signals fire for fixtures, admin edits and data migrations

**Consuming.** `manage.py run_consumer` subscribes to `glazr.inbound` and
handles `new_donut_order` by calling the same `create_order` the HTTP API uses.

It runs as its own compose service.

**Verifying it end to end.** With the stack up, watch the outbound channel:

```bash
docker compose exec redis redis-cli subscribe glazr.events
```

Place an order in the UI and `order.created` appears. Dispatch it and `order.dispatched` follows.

For the inbound direction:

```bash
docker compose exec redis redis-cli publish glazr.inbound '{"event":"new_donut_order","data":{"donuts":[{"donut_code":"CHOCOLATE","quantity":2}]}}'
```


The order appears on the Orders screen.

A full end to end test here is missing in the code, due to time constraints.

## Assumptions

- **Orders have no customer.** There wasn't a mention of tracking who placed an order, and the inbound
  message carries no customer either. The Orders screen therefore lists every order. Attaching a customer
  to an order would allow for scoping to whoever placed them.

- **Duplicate donut codes in one payload are merged.** Two entries for the same code become one line with
  the quantities added.

- **The catalogue filter runs client-side.** The API supports server-side filtering and it is tested,
  but the frontend filters the fetched list.

- **No cart persistence.** The order selection lives in component state and is gone on reload.

- **Database credentials are development defaults**, committed in `docker-compose.yml`. No secrets management
  here.

## Design decisions

**`unit_price` is stored on the order line; `total` is not stored.** The brief requires an endpoint that updates
a donut, so prices change. The price an order was placed at, is a fact about that line, not about the donut.
Editing a donut row, silently rewrites the totals of every past order.

The total, instead is derived from the lines, so storing it only creates something that can disagree with them.
It costs a `prefetch_related("items__donut")` on the list endpoint to stay flat.

At real volume the answer is pagination first, then a stored total if it measurably matters.

**Order creation lives in a service module.** `create_order` and `dispatch_order` are plain functions in `orders/services.py`.
Both the HTTP view and the message consumer call them, so the rules cannot drift apart. A manager method was the alternative
and is arguably a more expected Django pattern. But the logic spans two apps, it reads `Donut`, writes `Order`, so it sits
naturally on neither model.

**Errors are domain exceptions, not DRF ones.** The service raises `OrderError` subclasses; the view catches them and maps
to 400. The consumer is not an HTTP path and should not have to import DRF to handle a rejection.

**Redis pub/sub rather than a broker.** Pub/sub is fire-and-forget. A message published while the consumer is down is gone.
Redis was used purely because it's the one I am most experienced with, outside of RabbitMQ which has a lot more configuration
required to be correct.

Swapping it out is contained. `EventPublisher` is a protocol and nothing else in there knows which broker is behind it.

**The donut API exposes no delete.** The viewset is composed from mixins rather than `ModelViewSet`, since the brief asks for
list, retrieve, create and update.

**No authentication anywhere.** `AllowAny` is set explicitly in settings rather than inherited, so it reads as a decision.
This is not production ready, and it's in addition to the DEBUG level and production secret in settings still being
raw text, as opposed to even the most basic of loading in values from an env file.

## Deliberately incomplete

Time-boxed, so the following were left:

- **Authentication and permissions.** As above.

- **Pagination.** Both list endpoints return everything.

- **Idempotent message processing.** A `new_donut_order` delivered twice creates two orders. The fix is a message id in the envelope
  and a uniqueness constraint checked before creation.

- **Retries and dead-lettering.** Neither exists, and pub/sub gives you no redelivery to build on.

- **The consumer stops on an unexpected exception.** It handles malformed JSON, a missing key and the service's own errors, but a payload that is valid JSON
  with the right event name and the wrong shape underneath raises a `TypeError` that ends the command. Noticed while
  testing by hand, not fixed for time. Catching `Exception` in the handler and logging it is the fix.

  In addition, once the broker goes down you are out of business. A simple always restart would make this a bit more robust in a deployed application.

- **The publisher is held in a module-level global** with a setter, so one Redis client is reused and tests can swap it. That is mutable state at
  import scope; `functools.lru_cache` on the factory would give the same thing while removing the use of `globals`.

- **Test coverage reporting.** Not configured.

- **CI visible to a reviewer.** The `Jenkinsfile` runs the same two scripts, but on a private instance. It can mostly be ignored as it would look a quite
  a bit different in a gitlab-ci.yml. I just hooked it up to my home CI/CD for my own use so I could have tests running in the background while I
  worked.

- **`SECRET_KEY` and `DEBUG`** are Django's generated development defaults.

## Where TDD was applied

The order service layer, in two commits:

- `303b127` — The tests, with no implementation behind them
- `e79a498` — The implementation that made them pass

The tests drove:

- The total across multiple lines.
- Copying the donut's price onto the line when the order is placed, rather than reading it live.
- Merging duplicate donut codes in a single payload.
- Rejecting an unknown code, an unavailable donut, a zero quantity, an empty payload, and a second
  dispatch on an order already dispatched.

Each rejection also checks nothing was written.

I picked this area because it's where the business rules actually live, and both the API
and the message consumer run through it.
