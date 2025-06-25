## 📦 AI Technology Stack Recommender API

This project is an **AI-powered backend API** built with **FastAPI**, designed to recommend:

* 💡 Technology stack
* 👨‍💻 Optimal team composition
* 💸 Cost estimation
* 🗺 Implementation roadmap
* 🔎 Market insights

### 🧠 Powered by:

* 🧠 Large Language Model (Groq / LLaMA3)
* 📈 Real-time tech & salary analysis
* 🗃 SQLite database (for persistence)
* 📋 MLOps logging (for observability & auditing)

---

## ⚙️ Setup Instructions

### 1. Clone this repo

```bash
git clone https://github.com/your-username/tech-stack-recommender.git
cd tech-stack-recommender
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
uvicorn main:app --reload
```

> Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 API Endpoints

---

### ✅ `GET /health`

**Purpose:** Health check
**Response:**

```json
{ "status": "ok" }
```

---

### ✅ `POST /generate`

**Purpose:** Generate full recommendation (tech stack, team, cost, roadmap, risk)

**Request:**

```json
{
  "description": "Build a scalable ecommerce platform with real-time inventory.",
  "budget": "moderate",
  "timeline": "3-6 months"
}
```

**Response:**

```json
{
  "recommendation": "### TECHNOLOGY STACK RECOMMENDATION REPORT ...",
  "source": "generated"
}
```

> If cached, `"source": "cache"`

---

### ✅ `GET /recommendation`

**Purpose:** Get cached recommendation
**Params:**

```http
/recommendation?description=...&budget=moderate&timeline=3-6%20months
```

**Response:**

```json
{
  "recommendation": "### TECHNOLOGY STACK RECOMMENDATION REPORT ...",
  "source": "cache"
}
```

---

### ✅ `GET /teams/members`

**Purpose:** List all team members from the database
**Response:**

```json
[
  {
    "id": 101,
    "name": "John Smith",
    "role": "Senior Frontend Developer",
    "skills": ["React", "Vue.js", "GraphQL"],
    ...
  }
]
```

---

### ✅ `POST /analyze/tech`

**Purpose:** Analyze technologies (category, salary, description, market)

**Request:**

```json
{
  "technologies": ["React", "Node.js", "MongoDB"]
}
```

**Response:**

```json
{
  "React": {
    "category": "Frontend",
    "salary_data": { "low": 80000, "high": 130000 },
    "description": "...",
    "market_position": "...",
    "competitors": ["Vue.js", "Angular"],
    "merits": ["Component-based architecture", ...]
  }
}
```

---

### ✅ `POST /search/technologies`

**Purpose:** Extract relevant technologies from a natural language query

**Request:**

```json
{ "query": "Build a mobile app with cloud backend and ML integration" }
```

**Response:**

```json
{
  "technologies": ["Flutter", "Firebase", "Python", "TensorFlow"]
}
```

---

### ✅ `GET /salary`

**Purpose:** Get salary range for a technology
**Params:**

```http
/salary?technology=React
```

**Response:**

```json
{
  "low": 80000,
  "median": 100000,
  "high": 130000
}
```

---

### ✅ `GET /roadmap`

**Purpose:** Generate implementation roadmap
**Params:**

```http
/roadmap?description=...&stack=...&timeline=3-6 months
```

**Response:**

```json
{
  "roadmap": "### Planning Phase\n- Define scope\n- Create wireframes\n..."
}
```

---

### ✅ `GET /market-position`

**Purpose:** Get market trends for a technology
**Params:**

```http
/market-position?technology=React&context=ecommerce
```

**Response:**

```json
{
  "market_analysis": "React continues to be a dominant frontend framework..."
}
```

---

## 🧠 MLOps Logging

All API actions are logged in:

```
mlops_logs/log_YYYY-MM-DD.jsonl
```

Each log includes:

* Timestamp
* Event type (`request`, `response`, `error`, `recommendation`, `cache_hit`)
* Payload summary
* Latency (in seconds)
* Model version used

---

## 🗄 SQLite Database

Your recommendation data is persisted in:

```
recommendations.db
```

Tables:

* `projects`: Stores project description + budget + timeline
* `recommendations`: Links to project and stores full recommendation text

---

## 📎 Example: Generate + Cache

1. First call to `/generate`:

   * Triggers model
   * Saves to SQLite
   * Returns `source: generated`

2. Second call with same input:

   * Fetches from cache
   * Returns `source: cache`

---

## 💡 Future Ideas

* Add JWT authentication
* Add API Key management
* Integrate frontend using React or Vite
* Use MLflow or Prometheus for advanced monitoring

---

## 🤝 Contributing

1. Fork this repo
2. Create your feature branch
3. Submit a PR after testing

---

## 📃 License

MIT © 2025 \[Aayush Gid]

