-->> 🚀 K3s Monitoring App

This project is a **Python application deployed on a K3s Kubernetes cluster**, fully monitored using **Prometheus**, **Grafana**, and **Alertmanager**.  

The setup provides robust observability with dashboards and email alerts, and demonstrates modern DevOps best practices.

---

-->> 📄 **Project Overview**

- ✅ Python web application (with CPU & memory metrics)
- ✅ Deployed on a lightweight K3s cluster (single-node)
- ✅ Service exposure via NodePort
- ✅ Integrated monitoring stack:
  - **Prometheus**: Metrics collection & alerting
  - **Grafana**: Visualization dashboards
  - **Alertmanager**: Email notifications for alerts


-->> 🗂️ **Folder Structure**

Python_proj/
├── Python_App/ # Python app source code and Dockerfile
├── Prometheus/ # Prometheus deployment & config files
├── Grafana/ # Grafana deployment & config files
├── Alertmanager/ # Alertmanager deployment & config files
├── K3s_Common/ # Shared service and deployment files

 -->>⚙️ **Key Features**

-->> 💻 Python Application

- Simple FastAPI or Flask-based app
- Provides custom `/metrics` endpoint for Prometheus scraping
- Tracks CPU and memory usage

-->> ☸️ Kubernetes with K3s

- Lightweight K3s cluster deployed on AWS EC2
- NodePort service to expose application and dashboards

-->> 📈 Monitoring & Alerts

- Prometheus scrapes app and cluster metrics
- Grafana dashboards visualize resource usage
- Alertmanager sends email notifications on:
  - App downtime
  - High CPU usage
  - High memory usage

---

-->> 📦 **Deployment Steps**

-->> ✅ Prerequisites

- AWS EC2 instance (Ubuntu)
- Docker & K3s installed
- kubectl configured

# Test pipeline
