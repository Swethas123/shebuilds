<<<<<<< HEAD
# 🎙 OmniConnect – Voice-Driven Virtual Community App

##  Overview

OmniConnect is a voice-driven virtual assistant web app designed for **community engagement** and **resident support**. It was built for the **SheBuilds Hackathon 2025** using:

- **FastAPI** (Backend)
- **HTML, CSS, JavaScript** (Frontend)
- **OmniDimension Voice Assistant Widget** (Voice Interaction)
- **VS Code** for development

---

## 🗂 Project Structure
=======
# shebuilds
# 🎙 OmniConnect – Voice-Driven Virtual Community App

## 🚀 Overview

OmniConnect is a voice-driven virtual assistant web app designed for *community engagement* and *resident support. It was built for the **SheBuilds Hackathon 2025* using:

- *FastAPI* (Backend)
- *HTML, CSS, JavaScript* (Frontend)
- *OmniDimension Voice Assistant Widget* (Voice Interaction)
- *VS Code* for development

---

## 🗂 Project Structure
>>>>>>> 3337c984cddb84bc34f515759dd3430c17732150

voiceapp/
│
├── shebuilds/ # Initial module (reference)
│ ├── frontend/
│ ├── app.py
│ ├── db.py
│ └── README.md
│
├── shebuilds-1/ # Final working app
│ ├── static/ # CSS and other assets
│ ├── templates/ # HTML files
│ ├── pycache/
│ ├── app.py # Application logic (FastAPI)
│ ├── db.py # Data storage logic
│ ├── main.py # Entry point (runs the server)
│ ├── README.md # Project readme
│ ├── requirement.txt # Requirements (initial version)
│ └── venv/ # Python virtual environment
│
├── requirements.txt # Final dependency list
└── README.md

yaml
Copy
Edit

---

##  Key Features

<<<<<<< HEAD
-  **Voice Complaint Registration**  
-  **Technician Dashboard** with issue tracking  
-  **Emotion-aware Ticket Prioritization** using OmniDimension  
-  **Voice-based Poll Creation**
- **Event Display + Feedback System**
-  **Multi-language Complaint Translation (planned)**
=======
-  *Voice Complaint Registration*  
-  *Technician Dashboard* with issue tracking  
-  *Emotion-aware Ticket Prioritization* using OmniDimension  
-  *Voice-based Poll Creation*
-  *Event Display + Feedback System*
-  *Multi-language Complaint Translation (planned)*
>>>>>>> 3337c984cddb84bc34f515759dd3430c17732150

---

## 🔧 How to Run This App

### 1. Clone or Open Project

```bash
git clone <repo_url>
cd voiceapp/shebuilds-1
2. Create & Activate Virtual Environment
bash
Copy
Edit
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Mac/Linux
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Start FastAPI Server
bash
Copy
Edit
uvicorn main:app --reload
This runs the app locally at:
 http://127.0.0.1:8000

 Voice Assistant Integration
OmniDimension voice widget is embedded via:

html
Copy
Edit
<script id="omnidimension-web-widget" async
  src="https://backend.omnidim.io/web_widget.js?secret_key=4c1a8491af016e877c8da98cabe47505">
</script>
<<<<<<< HEAD
🖼 Frontend Pages
=======
🖼 Frontend Pages
>>>>>>> 3337c984cddb84bc34f515759dd3430c17732150
Page	Description
index.html	Welcome screen with voice assistant
complaints.html	Voice complaint registration
technician.html	Technician dashboard
polls.html	Voice-based poll creation
events.html	Community event page with feedback

 Completed Milestones
 FastAPI backend set up and running

 Static + dynamic HTML templates created

 Connected OmniDimension voice widget

 Setup database interaction with db.py

 Designed user flow for complaints and technician mapping

 Frontend + backend integrated

 Created colorful UI with responsive layout

 To-Do (Planned Enhancements)
 Add multilingual voice input support

 Admin analytics dashboard

 Auto follow-up with contextual memory

 Google Calendar integration for events

 Final Goal
A fully working voice-first community management web app that empowers residents to engage and report issues hands-free using natural language, while providing tools for community managers to respond intelligently.
<<<<<<< HEAD

# shebuilds
=======
>>>>>>> 3337c984cddb84bc34f515759dd3430c17732150
