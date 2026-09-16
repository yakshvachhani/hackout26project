# ⚡ OptiGrid-AI

> **An Intelligent Grid Management and Optimization Platform**  
> *Built for HackOut'26 at DA-IICT*

[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-18-blue?style=for-the-badge&logo=react)](https://reactjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)](https://python.org/)
[![PuLP](https://img.shields.io/badge/PuLP-Optimization-orange?style=for-the-badge)](#)

---

## 📖 The Problem
Rural and remote communities in India often rely on expensive, highly polluting diesel generators or experience frequent grid outages. While renewable energy (solar/wind) combined with Battery Energy Storage Systems (BESS) provides a clean alternative, calculating the *exact moment* to dispatch power, store energy, or run a backup generator is an incredibly complex mathematical problem. Volatile weather, fluctuating community demand, and battery degradation make manual dispatching highly inefficient and costly.

## 💡 Our Solution
**OptiGrid-AI** is an enterprise-grade Microgrid SCADA dashboard and Linear Programming (LP) optimizer designed to intelligently dispatch energy resources in off-grid rural networks. By analyzing weather forecasts, real-time load demand, and battery state-of-charge, OptiGrid-AI dictates the most cost-effective and carbon-neutral energy mix.

---

## 🧠 Technical Approach

### 1. Mathematical Optimization Engine (Linear Programming)
At the core of the backend is a highly sophisticated dispatch algorithm built using Python's **PuLP** library. 
- **Objective Function:** The algorithm mathematically minimizes total operating costs and CO₂ emissions.
- **Constraints:** It balances the grid equation (`Solar + Wind + Battery_Discharge + Diesel = Load + Battery_Charge`) at every time interval.
- **Battery Health Preservation:** The algorithm strictly enforces State-of-Charge (SOC) constraints (keeping batteries between 20% and 95%) to prevent deep discharge degradation.

### 2. Live SCADA Telemetry & Dynamic Scaling
The Next.js frontend acts as a Supervisory Control and Data Acquisition (SCADA) system. It features an interactive, animated SVG transmission diagram.
The platform dynamically scales energy profiles based on geographic selection. If a user switches from the **Kutch Desert Hub** to the **Spiti Valley Microgrid**, the system instantly pulls that region's unique metadata, adjusts temperature scales, modifies solar irradiance multipliers, and redraws the UI telemetry in real-time.

### 3. Predictive Weather Risk Integration
OptiGrid-AI connects to the **Open-Meteo API** to pull live 48-hour forecasts for the exact GPS coordinates of the selected microgrid. It correlates cloud cover percentages with expected solar drops and issues preemptive AI recommendations (e.g., *"Trigger battery charging cycle before 14:00 today due to expected cloud cover"*).

---

## ✨ Key Features
- 📊 **Real-Time Dashboards:** Track "Renewable Share", "Diesel Dependency", and "CO₂ Avoided" metrics.
- ⚙️ **Mathematical Dispatch Breakdown:** Dedicated Optimizer page showing exactly how the LP algorithm arrived at its conclusions.
- 🌍 **Multi-Region Support:** Hot-swap between diverse Indian microgrids instantly.
- 📑 **Auditor PDF Export:** Clean, printable, optimized PDF reports removing dashboard UI elements for compliance auditing.

---

## 📂 Repository Structure

```text
OptiGrid-AI/
├── frontend/        # Next.js Web dashboard, SCADA UI, and global state
├── backend/         # FastAPI Server, REST endpoints, and API integrations
├── optimization/    # PuLP Linear Programming models & grid algorithms
└── data/            # Simulated SCADA datasets and historical telemetry
```

---

## 🚀 How to Run Locally

### 1. Start the Backend (Python/FastAPI)
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install fastapi uvicorn pulp pandas
python -m uvicorn main:app --reload --port 8000
```

### 2. Start the Frontend (Next.js/React)
```bash
cd frontend
npm install
npm run dev
```

### 3. View the App
Open `http://localhost:3000` in your browser.

---

## 👥 The Team
Built with ❤️ by a team of 4 for **HackOut'26**:

| Name | Role / GitHub |
| :--- | :--- |
| **Daksh Kevadiya** | [GitHub Profile](https://github.com/dakshkevadiya) |
| **Yaksh Vachhani** | [GitHub Profile](https://github.com/yakshvachhanis) |
| **Pal Patel** | [GitHub Profile](https://github.com/pal0611) |
| **Dhruvi Ambaliya** | [GitHub Profile](https://github.com/dhruvi544) |

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
