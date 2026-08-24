import hashlib
import uuid
import random
from datetime import datetime, date
from typing import Optional, List

from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import io
import csv

# -------------------------------------------------------------
# Database Setup & Resilient Fallback
# -------------------------------------------------------------
USER_EMAIL = 'resident@omnicennect.io'

try:
    client = MongoClient(
        "mongodb+srv://swethas2005:Hello2005@cluster0.tbxmbbi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
        server_api=ServerApi('1'),
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=3000
    )
    client.admin.command('ping')
    print("DEBUG: MongoDB Connected Successfully!")
    db = client["shebuilds_db"]
except Exception as e:
    print(f"DEBUG: MongoDB Connection Failed ({e}). Falling back to in-memory mock DB.")
    import mongomock
    client = mongomock.MongoClient()
    db = client["shebuilds_db"]

users_collection = db["users"]
problems_collection = db["problems"]
events_collection = db["events"]
participation_collection = db["participate"]
feedback_collection = db["feedback"]
polls_collection = db["polls"]
leaderboard_collection = db["leaderboard"]

# -------------------------------------------------------------
# Initial Seed Data for Demo & Presentation
# -------------------------------------------------------------
def seed_initial_data():
    # Upgrade / Seed Problems
    if problems_collection.count_documents({"priority": {"$exists": True}}) == 0:
        seed_problems = [
            {
                "ticket_number": 10243,
                "resident_name": "Aarav Sharma",
                "user_email": "resident@omnicennect.io",
                "hno": "Tower A - Flat 402",
                "category": "Plumbing",
                "priority": "P1",
                "emotion": "Urgent",
                "days_facing_issue": 1,
                "description": "Main water supply pipe burst in utility area, leaking into hallway.",
                "status": "in-progress",
                "handleby": "Ramesh Kumar (Master Plumber)",
                "contact": "+91 98401 22345",
                "timestamp": "2026-08-24 09:30 AM"
            },
            {
                "ticket_number": 10244,
                "resident_name": "Priya Nambiar",
                "user_email": "priya@omnicennect.io",
                "hno": "Tower B - Flat 701",
                "category": "Electrical",
                "priority": "P2",
                "emotion": "Frustrated",
                "days_facing_issue": 2,
                "description": "Voltage fluctuation in master bedroom, AC tripping repeatedly.",
                "status": "pending",
                "handleby": "Suresh Patel (Electrician)",
                "contact": "+91 97890 33412",
                "timestamp": "2026-08-23 04:15 PM"
            },
            {
                "ticket_number": 10245,
                "resident_name": "Vikram Sethi",
                "user_email": "vikram@omnicennect.io",
                "hno": "Tower C - Flat 204",
                "category": "Lift/Elevator",
                "priority": "P2",
                "emotion": "Urgent",
                "days_facing_issue": 1,
                "description": "Lift 2 making severe grinding noise and stopping unevenly at Floor 2.",
                "status": "in-progress",
                "handleby": "Otis Tech Team",
                "contact": "+91 98111 88990",
                "timestamp": "2026-08-24 08:00 AM"
            },
            {
                "ticket_number": 10246,
                "resident_name": "Deepika Rao",
                "user_email": "deepika@omnicennect.io",
                "hno": "Tower A - Flat 1104",
                "category": "Sanitation & Cleaning",
                "priority": "P3",
                "emotion": "Neutral",
                "days_facing_issue": 3,
                "description": "Clubhouse corridor trash chute door hinge is loose.",
                "status": "resolved",
                "handleby": "Maintenance Crew",
                "contact": "+91 98401 22345",
                "timestamp": "2026-08-22 11:20 AM"
            },
            {
                "ticket_number": 10247,
                "resident_name": "Karthik Verma",
                "user_email": "karthik@omnicennect.io",
                "hno": "Tower B - Flat 305",
                "category": "Security & Access",
                "priority": "P4",
                "emotion": "Happy",
                "days_facing_issue": 1,
                "description": "Requested RFID visitor pass reconfiguration for parking slot B-12.",
                "status": "resolved",
                "handleby": "Gate Security Desk",
                "contact": "+91 98888 11223",
                "timestamp": "2026-08-21 02:40 PM"
            }
        ]
        problems_collection.insert_many(seed_problems)

    # Ensure all problems have required fields
    for p in problems_collection.find({"priority": {"$exists": False}}):
        problems_collection.update_one(
            {"_id": p["_id"]},
            {"$set": {
                "priority": "P3",
                "emotion": "Neutral",
                "resident_name": p.get("resident_name", "Resident"),
                "handleby": p.get("handleby") or "Duty Technician Team",
                "contact": p.get("contact") or "+91 98401 22345",
                "timestamp": p.get("timestamp") or "2026-08-24 10:00 AM",
                "ticket_number": p.get("ticket_number") or random.randint(10250, 99999)
            }}
        )

    # Upgrade / Seed Events
    if events_collection.count_documents({"ai_suggested": True}) == 0:
        seed_events = [
            {
                "id": "EVT-101",
                "title": "Bollywood Karaoke & Food Truck Night",
                "category": "Social & Cultural",
                "location": "Clubhouse Lawn & Terrace Lounge",
                "date": "Friday, Aug 28, 2026",
                "time": "07:00 PM - 10:30 PM",
                "description": "Sing along to classic and trending hits! Live mocktails, gourmet food trucks, and acoustic performances.",
                "attendees": 48,
                "ai_suggested": True,
                "ai_reason": "Suggested based on high Friday evening resident engagement & pleasant terrace weather forecast.",
                "announcement_text": "This Friday, enjoy Bollywood Karaoke Night at the Clubhouse Lawn and Terrace Lounge starting at 7 PM!",
                "status": "Upcoming"
            },
            {
                "id": "EVT-102",
                "title": "Sunrise Yoga & Sound Bath Healing",
                "category": "Health & Wellness",
                "location": "Central Garden Gazebo",
                "date": "Sunday, Aug 30, 2026",
                "time": "06:30 AM - 08:00 AM",
                "description": "Guided Vinyasa flow followed by Tibetan singing bowl meditation. Refreshing herbal juices provided.",
                "attendees": 32,
                "ai_suggested": True,
                "ai_reason": "Suggested for Sunday morning wellness; past yoga sessions received a 4.9/5 satisfaction rating.",
                "announcement_text": "Rejuvenate your weekend with Sunrise Yoga and Sound Bath healing this Sunday at 6:30 AM in the Central Garden.",
                "status": "Upcoming"
            },
            {
                "id": "EVT-103",
                "title": "Junior Robotics & AI Makers Workshop",
                "category": "Kids & Learning",
                "location": "Community Center Room 1",
                "date": "Saturday, Sep 05, 2026",
                "time": "10:00 AM - 01:00 PM",
                "description": "Hands-on robotics kit building and scratch coding for kids aged 7-14. Free kit included.",
                "attendees": 24,
                "ai_suggested": False,
                "ai_reason": "",
                "announcement_text": "Join the Junior Robotics and AI makers workshop for kids on Saturday, September 5th at Room 1.",
                "status": "Upcoming"
            }
        ]
        events_collection.insert_many(seed_events)

    # Ensure all events have id, location, attendees, and announcement text
    idx = 104
    for e in events_collection.find({"id": {"$exists": False}}):
        evt_id = f"EVT-{idx}"
        title = e.get("title", "Community Event")
        events_collection.update_one(
            {"_id": e["_id"]},
            {"$set": {
                "id": evt_id,
                "location": e.get("location") or "Clubhouse Central Hall",
                "category": e.get("category") or "Social & Cultural",
                "date": e.get("start_date") or "Upcoming Weekend",
                "time": "06:00 PM - 08:00 PM",
                "attendees": e.get("attendees") or 18,
                "ai_suggested": False,
                "announcement_text": f"Join us for {title} at the Clubhouse!",
                "status": e.get("status") or "Upcoming"
            }}
        )
        idx += 1

    if polls_collection.count_documents({}) == 0:
        seed_polls = [
            {
                "id": "POLL-01",
                "title": "Install 10 Additional EV Charging Stations in Basement 2?",
                "description": "Society proposes partnering with Tata Power for dedicated 22kW EV fast chargers.",
                "created_by": "Management Committee",
                "options": [
                    {"label": "Strongly Agree (Yes, needed ASAP)", "votes": 64},
                    {"label": "Agree (Yes, but phased installation)", "votes": 38},
                    {"label": "Neutral / Need cost breakdown", "votes": 12},
                    {"label": "Disagree (Current slots suffice)", "votes": 6}
                ],
                "total_votes": 120,
                "category": "Infrastructure"
            },
            {
                "id": "POLL-02",
                "title": "Preferred Time Slot for Swimming Pool Women-Only Hours?",
                "description": "Voice poll to finalize dedicated morning or evening slots.",
                "created_by": "Resident Welfare Group",
                "options": [
                    {"label": "Morning: 10:00 AM - 11:30 AM", "votes": 45},
                    {"label": "Evening: 04:00 PM - 05:30 PM", "votes": 58},
                    {"label": "Late Afternoon: 02:00 PM - 03:30 PM", "votes": 14}
                ],
                "total_votes": 117,
                "category": "Amenities"
            }
        ]
        polls_collection.insert_many(seed_polls)

    if leaderboard_collection.count_documents({}) == 0:
        seed_leaderboard = [
            {"rank": 1, "name": "Meera Krishnan", "flat": "Tower B - 802", "points": 850, "badge": "🏆 Community Champion", "games_won": 14},
            {"rank": 2, "name": "Aarav Sharma", "flat": "Tower A - 402", "points": 720, "badge": "🥈 Master Quizzer", "games_won": 11},
            {"rank": 3, "name": "Rohan Gupta", "flat": "Tower C - 104", "points": 640, "badge": "🥉 Voice Bingo Pro", "games_won": 9},
            {"rank": 4, "name": "Ananya Joshi", "flat": "Tower A - 903", "points": 510, "badge": "🌟 Active Resident", "games_won": 7},
            {"rank": 5, "name": "Siddharth Roy", "flat": "Tower B - 201", "points": 430, "badge": "🎯 Trivia Enthusiast", "games_won": 5}
        ]
        leaderboard_collection.insert_many(seed_leaderboard)

    if feedback_collection.count_documents({}) == 0:
        seed_feedbacks = [
            {"name": "Aarav Sharma", "category": "Complaint Resolution", "rating": 5, "emotion": "Happy", "comment": "Plumbing team arrived within 15 minutes! Very courteous and fast.", "date": "2026-08-23"},
            {"name": "Sunita Menon", "category": "Terrace Garden Event", "rating": 5, "emotion": "Delighted", "comment": "The karaoke night was so much fun for the entire family!", "date": "2026-08-20"},
            {"name": "Rahul Deshmukh", "category": "Gym Maintenance", "rating": 4, "emotion": "Neutral", "comment": "Treadmill #2 was fixed smoothly, overall good response time.", "date": "2026-08-18"},
            {"name": "Preeti Jain", "category": "Security Support", "rating": 5, "emotion": "Happy", "comment": "Voice visitor approval made gate clearance effortless.", "date": "2026-08-16"}
        ]
        feedback_collection.insert_many(seed_feedbacks)

seed_initial_data()

# -------------------------------------------------------------
# FastAPI App Initialization
# -------------------------------------------------------------
app = FastAPI(title="OmniConnect - Virtual Community Manager", version="2.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
templates.env.globals['range'] = range

# -------------------------------------------------------------
# Pydantic Schemas
# -------------------------------------------------------------
class ComplaintForm(BaseModel):
    issue_type: str
    apartment_number: str
    description: str
    priority: Optional[str] = "P3"
    emotion: Optional[str] = "Neutral"

class StatusUpdateReq(BaseModel):
    ticket_number: int
    status: str

class PollVoteReq(BaseModel):
    poll_id: str
    option_index: int

class EventRSVPReq(BaseModel):
    event_id: str
    name: str
    email: str

class FeedbackModel(BaseModel):
    name: str
    category: str
    rating: int
    emotion: str
    comment: str

# -------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------
def get_complaint_stats():
    all_tickets = list(problems_collection.find({}, {"_id": 0}))
    total = len(all_tickets)
    p1 = len([t for t in all_tickets if t.get("priority") == "P1"])
    p2 = len([t for t in all_tickets if t.get("priority") == "P2"])
    p3 = len([t for t in all_tickets if t.get("priority") == "P3"])
    p4 = len([t for t in all_tickets if t.get("priority") == "P4"])
    active = len([t for t in all_tickets if t.get("status") in ["pending", "in-progress"]])
    resolved = len([t for t in all_tickets if t.get("status") == "resolved"])
    return {
        "total": total,
        "active": active,
        "resolved": resolved,
        "p1": p1,
        "p2": p2,
        "p3": p3,
        "p4": p4,
        "satisfaction": "94.8%"
    }

# -------------------------------------------------------------
# Core Web Page Routes
# -------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
async def home_dashboard(request: Request):
    stats = get_complaint_stats()
    recent_tickets = list(problems_collection.find({}, {"_id": 0}).sort("ticket_number", -1).limit(4))
    upcoming_events = list(events_collection.find({}, {"_id": 0}).limit(3))
    polls = list(polls_collection.find({}, {"_id": 0}).limit(2))
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_tickets": recent_tickets,
        "upcoming_events": upcoming_events,
        "polls": polls,
        "active_page": "dashboard"
    })

@app.get("/complaints", response_class=HTMLResponse)
async def complaints_screen(request: Request):
    stats = get_complaint_stats()
    tickets = list(problems_collection.find({}, {"_id": 0}).sort("ticket_number", -1))
    return templates.TemplateResponse("complaints.html", {
        "request": request,
        "stats": stats,
        "tickets": tickets,
        "active_page": "complaints"
    })

@app.post("/submit_problem")
async def submit_complaint_form(
    problemType: str = Form(...),
    hno: str = Form(...),
    description: str = Form(...),
    contact: Optional[str] = Form("+91 98401 22345"),
    priority: Optional[str] = Form("P3"),
    emotion: Optional[str] = Form("Neutral"),
    days: Optional[int] = Form(1)
):
    ticket_num = random.randint(10250, 99999)
    
    # Smart technician assignment based on category
    tech_map = {
        "Plumbing": "Ramesh Kumar (Plumbing Lead)",
        "Electrical": "Suresh Patel (Electrical Lead)",
        "Lift/Elevator": "Otis Tech Support",
        "Sanitation & Cleaning": "Green Clean Squad",
        "Security & Access": "Gate Security Desk"
    }
    assigned_tech = tech_map.get(problemType, "Duty Technician Team")

    # Priority adjustment based on emotion
    final_priority = priority or "P3"
    if emotion == "Urgent":
        final_priority = "P1"
    elif emotion == "Frustrated":
        final_priority = "P2"

    complaint_data = {
        "ticket_number": ticket_num,
        "resident_name": "Aarav Sharma",
        "user_email": USER_EMAIL,
        "hno": hno,
        "category": problemType,
        "priority": final_priority,
        "emotion": emotion,
        "days_facing_issue": days,
        "description": description,
        "status": "pending",
        "handleby": assigned_tech,
        "contact": contact,
        "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M %p")
    }

    problems_collection.insert_one(complaint_data)
    return RedirectResponse(url="/complaints?success=true", status_code=303)

@app.get("/tracking", response_class=HTMLResponse)
@app.get("/trackdetails", response_class=HTMLResponse)
async def tracking_screen(request: Request, q: Optional[str] = None):
    query_filter = {}
    if q and q.isdigit():
        query_filter = {"ticket_number": int(q)}
    
    tickets = list(problems_collection.find(query_filter, {"_id": 0}).sort("ticket_number", -1))
    return templates.TemplateResponse("tracking.html", {
        "request": request,
        "tickets": tickets,
        "search_query": q or "",
        "active_page": "tracking"
    })

@app.get("/events", response_class=HTMLResponse)
async def events_hub(request: Request):
    events = list(events_collection.find({}, {"_id": 0}))
    ai_suggestions = [e for e in events if e.get("ai_suggested")]
    standard_events = [e for e in events if not e.get("ai_suggested")]
    return templates.TemplateResponse("events.html", {
        "request": request,
        "events": events,
        "ai_suggestions": ai_suggestions,
        "standard_events": standard_events,
        "active_page": "events"
    })

@app.get("/addevent", response_class=HTMLResponse)
async def addevent_form(request: Request):
    return templates.TemplateResponse("addevents.html", {
        "request": request,
        "active_page": "events"
    })

@app.post("/create-event")
async def create_event_action(
    name: str = Form(...),
    category: str = Form("Social & Cultural"),
    location: str = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    description: Optional[str] = Form(""),
    announcement: Optional[str] = Form("")
):
    event_id = f"EVT-{random.randint(104, 999)}"
    announcement_txt = announcement or f"Join us for {name} on {date} at {location}!"
    
    event_data = {
        "id": event_id,
        "title": name,
        "category": category,
        "location": location,
        "date": date,
        "time": time,
        "description": description or "Community event for all residents.",
        "attendees": 1,
        "ai_suggested": False,
        "ai_reason": "",
        "announcement_text": announcement_txt,
        "status": "Upcoming"
    }
    events_collection.insert_one(event_data)
    return RedirectResponse(url="/events?created=true", status_code=303)

@app.get("/polls", response_class=HTMLResponse)
@app.get("/participate", response_class=HTMLResponse)
async def polls_and_games(request: Request):
    polls = list(polls_collection.find({}, {"_id": 0}))
    leaderboard = list(leaderboard_collection.find({}, {"_id": 0}).sort("points", -1))
    return templates.TemplateResponse("polls.html", {
        "request": request,
        "polls": polls,
        "leaderboard": leaderboard,
        "active_page": "polls"
    })

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_dashboard(request: Request):
    stats = get_complaint_stats()
    feedbacks = list(feedback_collection.find({}, {"_id": 0}))
    events = list(events_collection.find({}, {"_id": 0}))
    
    # Emotion distribution breakdown
    all_tickets = list(problems_collection.find({}, {"_id": 0}))
    emotions_count = {
        "Urgent": len([t for t in all_tickets if t.get("emotion") == "Urgent"]),
        "Frustrated": len([t for t in all_tickets if t.get("emotion") == "Frustrated"]),
        "Neutral": len([t for t in all_tickets if t.get("emotion") == "Neutral"]),
        "Happy": len([t for t in all_tickets if t.get("emotion") == "Happy"])
    }

    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "stats": stats,
        "feedbacks": feedbacks,
        "events": events,
        "emotions_count": emotions_count,
        "active_page": "analytics"
    })

@app.get("/feedback", response_class=HTMLResponse)
async def feedback_screen(request: Request):
    events = list(events_collection.find({}, {"_id": 0}))
    return templates.TemplateResponse("feedback.html", {
        "request": request,
        "events": events,
        "active_page": "feedback"
    })

@app.post("/submit_feedback")
async def submit_feedback_action(
    name: str = Form(...),
    category: str = Form(...),
    rating: int = Form(...),
    emotion: str = Form("Happy"),
    comment: str = Form(...)
):
    feedback_data = {
        "name": name,
        "category": category,
        "rating": int(rating),
        "emotion": emotion,
        "comment": comment,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    feedback_collection.insert_one(feedback_data)
    return RedirectResponse(url="/analytics?feedback_received=true", status_code=303)

@app.get("/technician", response_class=HTMLResponse)
async def technician_portal(request: Request):
    tickets = list(problems_collection.find({}, {"_id": 0}).sort("ticket_number", -1))
    stats = get_complaint_stats()
    return templates.TemplateResponse("technician.html", {
        "request": request,
        "tickets": tickets,
        "stats": stats,
        "tech_user": {"name": "Ramesh Kumar", "skill": "Master Plumber & Electrician", "phone": "+91 98401 22345"},
        "active_page": "technician"
    })

@app.get("/manager", response_class=HTMLResponse)
async def manager_portal(request: Request):
    stats = get_complaint_stats()
    tickets = list(problems_collection.find({}, {"_id": 0}).sort("ticket_number", -1).limit(5))
    events = list(events_collection.find({}, {"_id": 0}))
    return templates.TemplateResponse("manager.html", {
        "request": request,
        "stats": stats,
        "tickets": tickets,
        "events": events,
        "active_page": "manager"
    })

# -------------------------------------------------------------
# Authentication Routes
# -------------------------------------------------------------
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
async def handle_login(request: Request, email: str = Form(...), password: str = Form(...)):
    global USER_EMAIL
    USER_EMAIL = email
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@app.post("/register")
async def handle_register(
    userType: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...)
):
    global USER_EMAIL
    USER_EMAIL = email
    return RedirectResponse(url="/dashboard", status_code=303)

# -------------------------------------------------------------
# REST & Voice JSON API Endpoints
# -------------------------------------------------------------

@app.get("/api/ticket-status/{ticket_number}")
async def api_ticket_status(ticket_number: int):
    ticket = problems_collection.find_one({"ticket_number": ticket_number}, {"_id": 0})
    if ticket:
        return {"found": True, **ticket}
    return {"found": False}

@app.post("/update_ticket_status")
async def api_update_ticket_status(req: StatusUpdateReq):
    problems_collection.update_one(
        {"ticket_number": req.ticket_number},
        {"$set": {"status": req.status}}
    )
    return {"message": "Status updated successfully", "ticket_number": req.ticket_number, "status": req.status}

@app.post("/api/polls/vote")
async def api_poll_vote(req: PollVoteReq):
    poll = polls_collection.find_one({"id": req.poll_id})
    if poll and 0 <= req.option_index < len(poll.get("options", [])):
        options = poll["options"]
        options[req.option_index]["votes"] += 1
        total_votes = poll.get("total_votes", 0) + 1
        polls_collection.update_one(
            {"id": req.poll_id},
            {"$set": {"options": options, "total_votes": total_votes}}
        )
        return {"success": True, "options": options, "total_votes": total_votes}
    return JSONResponse(status_code=400, content={"error": "Invalid poll or option"})

@app.post("/api/events/rsvp")
async def api_event_rsvp(req: EventRSVPReq):
    event = events_collection.find_one({"$or": [{"id": req.event_id}, {"title": req.event_id}]})
    if event:
        new_count = event.get("attendees", 0) + 1
        events_collection.update_one({"_id": event["_id"]}, {"$set": {"attendees": new_count}})
        return {"success": True, "attendees": new_count}
    return JSONResponse(status_code=404, content={"error": "Event not found"})

@app.get("/api/export-complaints")
async def export_complaints_csv():
    tickets = list(problems_collection.find({}, {"_id": 0}).sort("ticket_number", -1))
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Ticket ID", "Resident Name", "Location / Flat", "Category", "Priority", "Emotion Tone", "Assigned Technician", "Status", "Timestamp", "Description"])
    
    for t in tickets:
        writer.writerow([
            t.get("ticket_number", ""),
            t.get("resident_name", ""),
            t.get("hno", ""),
            t.get("category", ""),
            t.get("priority", ""),
            t.get("emotion", ""),
            t.get("handleby", ""),
            t.get("status", ""),
            t.get("timestamp", ""),
            t.get("description", "")
        ])
    
    output.seek(0)
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=OmniConnect_Complaints_Report_{date.today()}.csv"
    return response
