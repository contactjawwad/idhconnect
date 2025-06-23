
# 🧠 IDHConnect – Inventory Data Hub

**A Dockerized Flask + NGINX Web App for Validating and Reporting Excel-Based Inventory Data From NSP**

IDHConnect (Inventory Data Hub) is a modular inventory management platform built with Flask and served through NGINX. Designed primarily for telecom hardware inventory files extracted from Nokia NSP, it enables users to upload Excel files, validate them, and generate structured report sheets for operational review and exports.

The app is built using Flask’s MVC pattern, supports future multi-tenancy and authentication, and is fully containerized using Docker Compose with an automated CI/CD pipeline via GitLab.

---

## 🚀 Key Features

- ✅ Upload large Excel-based inventory files
- 🧠 Intelligent validation for various hardware fields (e.g., SFPs, Flash, Power Modules)
- 📊 Auto-generation of Excel reports with both `Main` and `Summary` tabs
- 🔄 Real-time interactivity with AJAX
- 🔒 Secure and scalable (multi-user support in roadmap)
- 🐳 Dual container deployment: Flask backend + NGINX frontend
- 🔁 CI/CD integrated: Docker Hub builds and live deployment

---

## 🧱 Architecture Overview

```
User ↔ NGINX (Port 80)
             ↓
       IDH Flask App (Gunicorn, Port 8000)
```

- `nginx_container`: reverse proxy for routing, timeout tuning, static file serving
- `idh_container`: Flask backend (4 Gunicorn workers) exposing port 8000 internally
- Docker Compose handles both containers via bridge network (`myappnetwork`)
- All logs and assets use persistent volumes: `idh_logs` and `nginx_logs`

---

## 🗂️ Directory Structure

```
InventoryDataHub/
├── app/                    # Flask MVC app
│   ├── controllers/        # View logic (routes)
│   ├── models/             # Data parsing logic
│   ├── services/           # Report logic
│   ├── static/             # JS, CSS, images
│   ├── templates/          # HTML reports
│   └── utils/              # Logging, cleanup
├── deploy/
│   ├── docker-compose.yml  # Compose deployment
│   ├── idh-docker/         # Dockerfile for backend
│   ├── nginx-docker/       # Dockerfile + NGINX config
├── tests/                  # Pytest files
├── requirements.txt
├── run.sh
```

---

## 🐳 How to Deploy with Docker Compose

> 🔥 Requires: Docker + Docker Compose (v2 or above)

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/idhconnect
cd idhconnect/deploy
```

### Step 2: Run the App

```bash
docker-compose up -d
```

Then go to: [http://localhost](http://localhost)

---

## 🧪 Run Backend Tests

```bash
docker-compose run --rm idh_container /bin/sh -c "export PYTHONPATH=/usr/src/app:\$PYTHONPATH && pytest tests/"
```

---

## 📦 Docker Images Used

| Image | Purpose | Tagged On |
|-------|---------|-----------|
| `contactjawwad/idh-app:idh-latest` | Flask Backend (Gunicorn) | Docker Hub |
| `contactjawwad/idh-app:nginx-latest` | NGINX Reverse Proxy | Docker Hub |

> These are **auto-built and pushed by GitLab CI/CD** during deployment.

---

## 📋 NGINX Configuration Highlights

- Routes all frontend requests to backend Flask app:
  ```nginx
  proxy_pass http://idh_container:8000;
  ```
- Client body limit: `1000M`
- Timeout tuning: `900s` for uploads and processing
- Also serves static test page at: [http://localhost/test](http://localhost/test)

---

## 💡 Build Notes

### Local Builds (Compose)

Docker Compose builds both images from these locations:
- `deploy/idh-docker/Dockerfile` → `idh_container`
- `deploy/nginx-docker/Dockerfile` → `nginx_container`

To force cache refresh:
```yaml
args:
  - CACHEBUST=1
```

---

## 🔄 GitLab CI/CD Pipeline

Defined in `.gitlab-ci.yml` and used to:
1. Build both containers (`idh_container`, `nginx_container`)
2. Run Pytest for backend
3. Push tagged images to Docker Hub
4. Deploy to your runner machine via Compose
5. Manually clean up containers/images using `cleanup_app`

---

## 🔗 Related Docker Hub Links

- [Docker Hub – IDH App (Gunicorn)](https://hub.docker.com/r/contactjawwad/idh-app/tags?page=1&name=idh)
- [Docker Hub – NGINX Container](https://hub.docker.com/r/contactjawwad/idh-app/tags?page=1&name=nginx)

---

## 📷 Screenshots

| Upload Page | Summary Report |
|-------------|----------------|
| ![upload](app/static/images/select_and_report.png) | ![summary](app/static/images/summary_report.png) |

---

## 📚 Documentation

- 📘 User Guide (`IDH_Connect_User_Guide.docx`)
- 🧱 Software Design Document (`InventoryHub_SDD_Draft.docx`)
- 📊 Demo Presentation (`IDH Demo Presentation.pptx`)

---

## 📬 Maintainer

Jawwad Qureshi  
📧 jawwad.qureshi@nokia.com  
📞 +61 481 592 790  

---

## 📜 License

This is a proprietary project. Please contact the maintainer for any reuse or redistribution inquiries.
