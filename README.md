# px-assignment
[Python][FastAPI] Asynchronously fetch given `{sku}` from different vendors via API call, apply business logic over the response and cache the best vendor per `{sku}`

# 🚀 FastAPI Vendor Aggregator — Clean Architecture, Caching, Resilience & Observability

A minimal and clean fastapi service that fetches product pricing from `THREE` external vendors, compares them, and returns the best vendor — **fast, resilient, observable, cached, and fully dockerized**.

---

## ✨ Features

* **`GET /products/{sku}`** — fetch best vendor price
* **Three external vendor clients** with isolation & clean separation
* **Redis cache** for SKUs (reduces vendor calls)
* **HTTP timeouts + retries** using `httpx`
* **Rate‑limiter** per vendor (Redis‑based)
* **Circuit breaker** ("fail fast" protection)
* **Prometheus metrics**: latency, failures, request counts
* **Grafana dashboards**
* **Docker & Docker Compose** support

---

## 📂 Project Structure

```
px-assignment
├── Dockerfile
├── README.md
├── app
│   ├── __init__.py
│   ├── config
│   │   ├── __init__.py
│   │   └── config.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── dependencies.py
│   │   └── lifespan_events.py
│   ├── external_clients
│   │   ├── __init__.py
│   │   └── vendors.py
│   ├── instrumentation
│   │   ├── __init__.py
│   │   ├── metrics.py
│   │   └── middleware.py
│   ├── main.py
│   ├── resilience
│   │   ├── __init__.py
│   │   └── rate_limiter.py
│   ├── routers
│   │   ├── __init__.py
│   │   └── sku.py
│   ├── schemas
│   │   └── vendor
│   │       ├── __init__.py
│   │       └── models.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── cache_service.py
│   │   └── sku_service.py
│   └── switch
│       ├── __init__.py
│       └── switch.py
├── docker
│   ├── grafana
│   │   └── dashboards
│   └── prometheus.yml
├── docker-compose.yml
├── project_tree.txt
├── requirements.txt
└── simulation
    └── simulators.py
```

---

## 🔧 How It Works (High‑Level)

### 1️⃣ Request hits **/products/{sku}**

Router delegates to `sku_service.get_best_vendor_for_sku()`.

### 2️⃣ Redis cache lookup

If cached → returned immediately.

### 3️⃣ Vendor calls

Calls all three vendors (async):

* Each wrapped in

  * retry policy
  * timeout
  * redis rate limit
  * circuit breaker (only over the third vendor known for slow responses & errors)

### 4️⃣ Prometheus metrics

Each vendor call logs:

* latency
* success/failure

### 5️⃣ Best vendor chosen → cached → returned

---

## 🐳 Running with Docker

```bash
docker-compose -f 'docker-compose.yml' up -d --build
```

Services started:

* `px-assignment` — FastAPI app
* `redis_cache` — caching + rate limiter storage
* `prometheus` — metrics scraping
* `grafana` — visualization

---

## 📈 Observability

* **Prometheus UI:** [http://localhost:9090](http://localhost:9090)
* **Grafana UI:** [http://localhost:3000](http://localhost:3000)

  * Dashboards to track: *Vendor Performance*

Example PromQL queries:

```
vendor_latency_seconds_bucket
vendor_failures_total
rate(vendor_latency_seconds_sum[1m])
```

---

## ⚡ Example API Call

```bash
curl http://localhost:8000/products/sku123
```

## ⚡ Example Response

```json
"vendorB"
```

---

## 📝 Environment Variables (.env.example)

```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL=120
```

---

## 🔒 Clean Architecture Principles Followed

* **Business logic isolated** (`services/`)
* **Vendor‑specific logic isolated** (`external_clients/`)
* **Resilience policies reusable** (`resilience/`)
* **Metrics isolated** (`instrumentation/`)
* **Transport layer isolated** (`routers/`)
* **Config isolated** (`config/`)
