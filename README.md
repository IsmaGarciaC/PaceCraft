# PaceCraft 🏃‍♂️💨
#### Video Demo:  <YOUR_YOUTUBE_URL_HERE>
#### Description:

**PaceCraft** is a lightweight, full-stack web application tailored for runners. It allows athletes to log their training sessions, calculate accurate paces, visualize their progression over time, and mathematically project future race performances (5K, 10K, and Half-Marathons).

This project was built as the Final Project for Harvard University's **CS50x** course. Beyond satisfying the academic requirements, PaceCraft is engineered with modern industry practices, making it a robust, recruiter-friendly portfolio piece.

---

## 🚀 Features
*   **Secure Authentication**: Custom-built JWT (JSON Web Tokens) authentication system. Tokens are securely stored in `HttpOnly` cookies to prevent XSS attacks, and passwords are comprehensively hashed using `bcrypt`.
*   **Training Dashboard**: An intuitive UI to log distances and times. The backend automatically computes the exact pace (min/km).
*   **Interactive Data Visualization**: A dynamic line chart tracks the user's pace progression over time. The frontend fetches this data asynchronously from a custom JSON REST API using Vanilla JavaScript and renders it via **Chart.js**.
*   **Mathematical Race Projections**: Implements **Peter Riegel's fatigue formula** ($T_2 = T_1 \times (D_2 / D_1)^{1.06}$) to scientifically predict race times based on the user's most recent performance.

## 🛠️ Tech Stack
*   **Backend**: Python 3.12+, FastAPI, Uvicorn
*   **Database**: SQLite managed via synchronous SQLAlchemy ORM
*   **Data Validation**: Pydantic
*   **Frontend**: Jinja2 Templates, Bootstrap 5 (UI), Chart.js
*   **Security**: Passlib (Bcrypt), python-jose (JWT)

---

## 📁 Project Architecture & File Structure

The project departs from the traditional CS50 Flask architecture, opting instead for **FastAPI**, a modern, high-performance web framework.

*   `app/main.py`: The core entry point. Contains the initialization of the FastAPI application, the mounting of static assets, and all the routing logic (both UI endpoints returning HTML, and REST endpoints returning JSON).
*   `app/database.py`: Establishes the connection to the SQLite database. Configures the SQLAlchemy `engine` and the `SessionLocal` factory.
*   `app/models.py`: Defines the relational database schema using SQLAlchemy ORM. Contains the `User` and `Run` models and establishes a bidirectional `relationship` between them. Specifically, the `Run` model records crucial datapoints including the exact date, the distance covered in kilometers, the total duration in minutes, and the pre-calculated average pace. A deliberate architectural choice was made to calculate and store the pace during the database insertion phase rather than computing it dynamically on the fly during data retrieval. This significantly reduces computational overhead and drastically improves query speeds when sorting or filtering large datasets of historical running logs.
*   `app/schemas.py`: Contains Pydantic models (e.g., `UserCreate`) used to enforce strict type checking and data validation on incoming payloads.
*   `app/auth.py`: Centralizes all security logic. Handles password hashing/verification, JWT token creation, and provides the `get_current_user_from_cookie` dependency to securely extract and validate tokens from requests.
*   `app/calculations.py`: The pure "business logic" module. Isolates the mathematical operations, preventing the routing files from becoming cluttered. This module handles critical data transformations, specifically taking human-readable inputs and converting them into precise float values for backend storage. Furthermore, it mathematically executes Peter Riegel's fatigue formula for endurance sports ($T_2 = T_1 \times (D_2 / D_1)^{1.06}$). By isolating this logic, we ensure that the complex calculations required to project race times across different distances (5K, 10K, Half-Marathon) remain testable and entirely decoupled from the API routing layer.
*   `templates/`: Contains all Jinja2 HTML views (`base.html`, `index.html`, `login.html`, `register.html`, `add_run.html`, `predictions.html`).
*   `static/js/charts.js`: Houses the Vanilla JavaScript logic responsible for hitting the `/api/chart-data` endpoint and plotting the results on the canvas.

---

## 🧠 Key Design Decisions

1.  **FastAPI over Flask**: While CS50 teaches Flask, I opted for FastAPI. Its usage of Python type hints, automatic documentation generation, and superior performance make it a highly relevant skill in the current job market.
2.  **JWT in HttpOnly Cookies vs LocalStorage**: Storing JWTs in LocalStorage exposes them to Cross-Site Scripting (XSS) attacks. By instructing the backend to set an `HttpOnly` cookie upon login, the browser handles sending the token automatically with every request, keeping the token completely invisible to client-side scripts.
3.  **Hybrid Communication Approach**: To balance simplicity and modern UX, I utilized a hybrid approach. Standard operations (Login, Register, Add Run) utilize traditional HTML `<form>` submissions for native browser behavior. However, for the data visualization component, I used asynchronous `fetch()` requests to an API endpoint (`/api/chart-data`), preventing full page reloads and mimicking Single Page Application (SPA) behavior where it matters most.
4.  **Synchronous SQLAlchemy**: Despite FastAPI being inherently asynchronous, I purposefully chose to run SQLAlchemy synchronously. For an application of this scale using SQLite, the overhead of managing `async/await` database sessions outweighs the performance benefits, allowing for cleaner, more readable code.

---

## 🛑 Challenges Faced

Building PaceCraft involved tackling several non-trivial technical challenges, particularly since the project sidesteps beginner-friendly abstractions in favor of industry-standard tools:

1.  **JWT Authentication Implementation**: Implementing JSON Web Tokens from scratch without relying on heavyweight authentication plugins was highly complex. The primary challenge was securely bridging the stateless nature of FastAPI with the stateful HTML rendering of Jinja2 templates. To achieve this securely, I had to configure HTTP middleware to inject and read strict `HttpOnly` cookies, ensuring that the FastAPI dependency injection system could accurately parse, decode, and validate these cookies on every protected route without failing silently.
2.  **Asynchronous Data Visualization**: Integrating Chart.js into a server-side rendered application without triggering disruptive full-page reloads posed another hurdle. The solution involved writing Vanilla JavaScript to leverage the asynchronous `fetch()` API. By exposing a dedicated JSON endpoint, the frontend can seamlessly request the user's running progression in the background, parse the raw mathematical data, and dynamically redraw the responsive canvas.

---

## 🔮 Future Improvements

While PaceCraft currently satisfies all core requirements for a robust running log, its modular architecture leaves room for significant future scaling:

*   **Third-Party API Integrations**: A logical next step is implementing OAuth 2.0 to auto-sync workout data directly from popular fitness platforms like Strava or Garmin Connect.
*   **Elevation & Heart Rate Tracking**: Expanding the database schema to include vertical elevation gain and average heart rate (BPM) would allow for much more granular pace analysis and fatigue calculation.
*   **Time Zone Support**: Implementing comprehensive timezone tracking to ensure accurate logging for runners who travel across the globe.

---

## 💻 How to Run Locally

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/IsmaGarciaC/PaceCraft.git
    cd PaceCraft
    ```
2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    
    # Windows:
    .\venv\Scripts\activate
    
    # Mac/Linux:
    source venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the development server**:
    ```bash
    uvicorn app.main:app --reload
    ```
5.  **Access the application**:
    Open your browser and navigate to `http://127.0.0.1:8000`.
