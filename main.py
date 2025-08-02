# from fastapi import FastAPI, Form, Request
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel
# import uuid

# app = FastAPI()

# app.mount("/static", StaticFiles(directory="frontend"), name="static")
# templates = Jinja2Templates(directory="templates")

# technicians = []
# residents = []
# complaints = []
# community_events = []

# class Technician(BaseModel):
#     name: str
#     phone: str
#     skill: str

# class Resident(BaseModel):
#     name: str
#     apartment: str
#     phone: str

# class Complaint(BaseModel):
#     issue_type: str
#     apartment_number: str
#     description: str
#     status: str = "Pending"
#     ticket_id: str = None

# class Event(BaseModel):
#     name: str
#     location: str
#     time: str
#     status: str

# @app.get("/", response_class=HTMLResponse)
# async def root(request: Request):
#     return templates.TemplateResponse("home.html", {"request": request})

# @app.get("/resident", response_class=HTMLResponse)
# async def resident_page(request: Request):
#     return templates.TemplateResponse("resident.html", {"request": request})

# @app.post("/voice-complaint")
# async def voice_complaint(issue_type: str = Form(...), apartment_number: str = Form(...), description: str = Form(...)):
#     ticket_id = str(uuid.uuid4())[:6].upper()
#     complaints.append(Complaint(issue_type=issue_type, apartment_number=apartment_number, description=description, ticket_id=ticket_id))
#     return RedirectResponse(url="/resident", status_code=302)

# @app.get("/track-requests", response_class=HTMLResponse)
# async def track_requests(request: Request):
#     return templates.TemplateResponse("track.html", {"request": request, "complaints": complaints})

# @app.get("/technician", response_class=HTMLResponse)
# async def technician_dashboard(request: Request):
#     return templates.TemplateResponse("technician.html", {"request": request, "complaints": complaints})

# @app.get("/manager", response_class=HTMLResponse)
# async def manager_dashboard(request: Request):
#     return templates.TemplateResponse("manager.html", {"request": request, "events": community_events})

# @app.get("/events", response_class=HTMLResponse)
# async def events_page(request: Request):
#     return templates.TemplateResponse("events.html", {"request": request, "events": community_events})

# @app.get("/treg", response_class=HTMLResponse)
# async def technician_register_form(request: Request):
#     return templates.TemplateResponse("treg.html", {"request": request})

# @app.post("/treg")
# async def register_technician(name: str = Form(...), phone: str = Form(...), skill: str = Form(...)):
#     technicians.append(Technician(name=name, phone=phone, skill=skill))
#     return RedirectResponse(url="/technician", status_code=302)

# @app.get("/rreg", response_class=HTMLResponse)
# async def resident_register_form(request: Request):
#     return templates.TemplateResponse("rreg.html", {"request": request})

# @app.post("/rreg")
# async def register_resident(name: str = Form(...), apartment: str = Form(...), phone: str = Form(...)):
#     residents.append(Resident(name=name, apartment=apartment, phone=phone))
#     return RedirectResponse(url="/resident", status_code=302)

# @app.post("/create-event")
# async def create_event(name: str = Form(...), location: str = Form(...), time: str = Form(...), status: str = Form(...)):
#     community_events.append(Event(name=name, location=location, time=time, status=status))
#     return RedirectResponse(url="/events", status_code=302)


import hashlib
import certifi
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# from googletrans import Translator
# from pydantic import BaseModel
import uuid
import random
from pydantic import BaseModel
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# def connect():
#     print('entered into connection')
#     uri = "mongodb+srv://swethas2005:Hello2005@cluster0.tbxmbbi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
#     client = MongoClient(uri, server_api=ServerApi('1'))
#     try:
#         client.admin.command('ping')
#         print("Pinged your deployment. You successfully connected to MongoDB!")
#         return client
#     except Exception as e:
#         print(e)

  
# client = connect()

USER_EMAIL=''
client = MongoClient(
    "mongodb+srv://swethas2005:Hello2005@cluster0.tbxmbbi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    tls=True,
    tlsCAFile=certifi.where()
)
db = client["shebuilds_db"]
users_collection = db["users"]
problems_collection = db["problems"]
events_collection = db["events"]
participation_collection = db["participate"]

feedback_collection = db["feedback"]

app = FastAPI()
 
# Tell FastAPI to look in "templates/" for HTML files
# templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory storage
technicians = []
residents = []
complaints = []
community_events = []

# -------------------------------
# Models
# -------------------------------
# class Technician(BaseModel):
#     name: str
#     phone: str
#     skill: str

# class Resident(BaseModel):
#     name: str
#     apartment: str
#     phone: str

# class Complaint(BaseModel):
#     issue_type: str
#     apartment_number: str
#     description: str
#     status: str = "Pending"
#     ticket_id: str = None

# class Event(BaseModel):
#     name: str
#     location: str
#     time: str
#     status: str

# -------------------------------
# Routes
# -------------------------------


# @app.post("/submit_problem")
# async def submit_problem(
#     hno: str = Form(...),
#     contact: str = Form(...),
#     problemType: str = Form(...),
#     description: str = Form(...)
# ):
#     data = {
#         "hno": hno,
#         "contact": contact,
#         "problemType": problemType,
#         "description": description
#     }
#     problems_collection.insert_one(data)
#     return RedirectResponse(url="/resident", status_code=303)

# @app.post("/submit_problem")
# async def submit_problem(
#     problemType: str = Form(...),
#     days: int = Form(...),
#     description: str = Form(...)
# ):
#     global USER_EMAIL

#     ticket_number = random.randint(10000, 99999)

#     data = {
#         "user_email": USER_EMAIL,
#         "ticket_number": ticket_number,
#         "category": problemType,
#         "days_facing_issue": days,
#         "description": description,
#         "description": e_description
#         "status": "pending",
#         "handleby": None
#     }
    

#     problems_collection.insert_one(data)

#     return RedirectResponse(url="/trackdetails", status_code=303)


class Participation(BaseModel):
    title: str
    email: str
    registered_on: str

class Event(BaseModel):
    title: str
    description: str
    start_date: str  # in format YYYY-MM-DD
    end_date: str


class Feedback(BaseModel):
    name: str
    message: str

# API to store feedback
@app.post("/submit_feedback")
async def submit_feedback(feedback: Feedback):
    feedback_collection.insert_one(feedback.dict())
    return {"message": "Feedback stored"}



@app.post("/register_event")
def register_event(p: Participation):
    participation_collection.insert_one(p.dict())
    return {"message": "Registration successful"}

@app.post("/add_event")
async def add_event(event: Event):
    events_collection.insert_one(event.dict())
    return {"message": "Event added"}

@app.get("/get_events")
async def get_events():
    events = list(events_collection.find({}, {"_id": 0}))
    return events

@app.post("/submit_problem")
async def submit_problem(
    problemType: str = Form(...),
    days: int = Form(...),
    description: str = Form(...)
):
    global USER_EMAIL

    ticket_number = random.randint(10000, 99999)

    # Translate to English
    try:
        # translator = Translator()
        engdescription= description
    except Exception as e:
        engdescription = description  # fallback if translation fails

    data = {
        "user_email": USER_EMAIL,
        "ticket_number": ticket_number,
        "category": problemType,
        "days_facing_issue": days,
        "description": description,  # translated version
        "engdescription":engdescription,
        "status": "pending",
        "handleby": None
    }

    problems_collection.insert_one(data)

    return RedirectResponse(url="/trackdetails", status_code=303)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.get("/feedback", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("feedback.html", {"request": request, "error": None})


@app.get("/participate", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("participate.html", {"request": request, "error": None})

@app.get("/technician", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("technician.html", {"request": request, "error": None})


@app.get("/resident", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("resident.html", {"request": request, "error": None})


@app.get("/manager", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("manager.html", {"request": request, "error": None})


@app.get("/register", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
async def do_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = users_collection.find_one({"email": email, "password": hashed_password})

    if user:
        user_data = {k: v for k, v in user.items() if k != "_id"}  # Exclude MongoDB ID
        print("Login Success:", user_data)

        # Redirect based on userType
        global USER_EMAIL
        USER_EMAIL=user.get("email","")
        user_type = user.get("userType", "").lower()
        if user_type == "technician":
            return RedirectResponse(url="/technician", status_code=302)
        elif user_type == "resident":
            return RedirectResponse(url="/trackdetails", status_code=302)
        elif user_type == "manager":
            return RedirectResponse(url="/manager", status_code=302)
        else:
            return RedirectResponse(url="/", status_code=302)
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password"
        })
@app.post("/register")
async def register_user(
    userType: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    block: str = Form(""),
    floor: str = Form(""),
    flat: str = Form(""),
    service: str = Form(""),
    specialization: str = Form(""),
    experience: str = Form(""),
    timing: str = Form(""),
    tools: str = Form(""),
    society: str = Form(""),
    role: str = Form(""),
    blocks: str = Form("")
):
    if users_collection.find_one({"email": email}):
        return JSONResponse(status_code=400, content={"message": "Email already registered"})

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    user_data = {
        "userType": userType,
        "name": name,
        "email": email,
        "phone": phone,
        "password": hashed_password
    }

    if userType == "resident":
        user_data.update({
            "block": block,
            "floor": int(floor) if floor.strip().isdigit() else None,
            "flat": flat,
            "service": service
        })
    elif userType == "technician":
        user_data.update({
            "specialization": specialization,
            "experience": int(experience) if experience.strip().isdigit() else None,
            "timing": timing,
            "tools": tools
        })
    elif userType == "manager":
        user_data.update({
            "society": society,
            "role": role,
            "blocks": int(blocks) if blocks.strip().isdigit() else None
        })

    users_collection.insert_one(user_data)
    return RedirectResponse(url="/login", status_code=302)

@app.get("/resident", response_class=HTMLResponse)
async def resident_page(request: Request):
    return templates.TemplateResponse("rhome.html", {"request": request})

@app.post("/voice-complaint")
async def voice_complaint(
    issue_type: str = Form(...),
    apartment_number: str = Form(...),
    description: str = Form(...)
):
    ticket_id = str(uuid.uuid4())[:6].upper()
    complaints.append(Complaint(
        issue_type=issue_type,
        apartment_number=apartment_number,
        description=description,
        ticket_id=ticket_id
    ))
    return RedirectResponse(url="/resident", status_code=302)


@app.post("/problem-list")
async def get_problem_list():
    global USER_EMAIL
    problems_cursor = problems_collection.find({"user_email": USER_EMAIL})
    
    problems = []
    for p in problems_cursor:
        p["_id"] = str(p["_id"])  # Convert ObjectId to string
        problems.append(p)
    
    return JSONResponse(content={"problems": problems})

@app.get("/trackdetails", response_class=HTMLResponse)
async def track_requests(request: Request):
    return templates.TemplateResponse("tracking.html", {"request": request, "complaints": complaints})

@app.get("/technician", response_class=HTMLResponse)
async def technician_dashboard(request: Request):
    return templates.TemplateResponse("thome.html", {"request": request, "complaints": complaints})

@app.get("/manager", response_class=HTMLResponse)
async def manager_dashboard(request: Request):
    return templates.TemplateResponse("mhome.html", {"request": request, "events": community_events})

@app.get("/events", response_class=HTMLResponse)
async def events_page(request: Request):
    return templates.TemplateResponse("events.html", {"request": request, "events": community_events})

@app.get("/treg", response_class=HTMLResponse)
async def technician_register_form(request: Request):
    return templates.TemplateResponse("treg.html", {"request": request})

@app.post("/treg")
async def register_technician(
    name: str = Form(...),
    phone: str = Form(...),
    skill: str = Form(...)
):
    technicians.append(Technician(name=name, phone=phone, skill=skill))
    return RedirectResponse(url="/technician", status_code=302)

@app.get("/rreg", response_class=HTMLResponse)
async def resident_register_form(request: Request):
    return templates.TemplateResponse("rreg.html", {"request": request})

@app.post("/rreg")
async def register_resident(
    name: str = Form(...),
    apartment: str = Form(...),
    phone: str = Form(...)
):
    residents.append(Resident(name=name, apartment=apartment, phone=phone))
    return RedirectResponse(url="/resident", status_code=302)

@app.post("/create-event")
async def create_event(
    name: str = Form(...),
    location: str = Form(...),
    time: str = Form(...),
    status: str = Form(...)
):
    community_events.append(Event(name=name, location=location, time=time, status=status))
    return RedirectResponse(url="/events", status_code=302)





