from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

import models
from database import engine
from dependencies import get_db

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="placement_portal_secret"
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


# Create default login users
db = next(get_db())

if db.query(models.LoginUser).count() == 0:

    db.add(
        models.LoginUser(
            username="admin",
            password="admin123",
            role="Admin"
        )
    )

    db.add(
        models.LoginUser(
            username="trainer",
            password="trainer123",
            role="Trainer"
        )
    )

    db.add(
        models.LoginUser(
            username="student",
            password="student123",
            role="Student"
        )
    )

    db.commit()


# ======================
# LOGIN PAGE
# ======================

@app.get("/login")
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


# ======================
# LOGIN
# ======================

@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    user = db.query(models.LoginUser).filter(
        models.LoginUser.username == username,
        models.LoginUser.password == password
    ).first()

    if not user:

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Invalid Username or Password"
            }
        )

    request.session["username"] = user.username
    request.session["role"] = user.role

    return RedirectResponse(
        url="/",
        status_code=303
    )


# ======================
# LOGOUT
# ======================

@app.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303
    )

# ======================
# DASHBOARD
# ======================

@app.get("/")
def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):

    if "username" not in request.session:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    users = db.query(models.User).all()

    students = [
        u for u in users
        if u.role == "Student"
    ]

    trainers = [
        u for u in users
        if u.role == "Trainer"
    ]

    admins = [
        u for u in users
        if u.role == "Admin"
    ]

    total_students = len(students)
    total_trainers = len(trainers)
    total_admins = len(admins)

    internship_count = len(
        [s for s in students if s.internship == "Yes"]
    )

    ppo_count = len(
        [s for s in students if s.ppo == "Yes"]
    )

    placed_students = len(
        [s for s in students if s.placement_status == "Placed"]
    )

    cgpas = []
    packages = []

    for s in students:

        try:
            cgpas.append(float(s.cgpa))
        except:
            pass

        try:
           package = str(s.package).replace("LPA", "").strip()
           packages.append(float(package))
        except:
            pass

    avg_cgpa = round(
        sum(cgpas) / len(cgpas), 2
    ) if cgpas else 0

    highest_package = max(packages) if packages else 0

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={

            "username": request.session.get("username"),
            "role": request.session.get("role"),

            "total_students": total_students,
            "total_trainers": total_trainers,
            "total_admins": total_admins,

            "internship_count": internship_count,
            "ppo_count": ppo_count,
            "placed_students": placed_students,

            "avg_cgpa": avg_cgpa,
            "highest_package": highest_package
        }
    )

# ======================
# STUDENTS PAGE
# ======================

@app.get("/students")
def students(
    request: Request,
    db: Session = Depends(get_db)
):

    if "username" not in request.session:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    students = db.query(models.User).filter(
        models.User.role == "Student"
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="students.html",
        context={
            "students": students,
            "role": request.session.get("role"),
            "username": request.session.get("username")
        }
    )


# ======================
# TRAINERS PAGE
# ======================

@app.get("/trainers")
def trainers(
    request: Request,
    db: Session = Depends(get_db)
):

    if "username" not in request.session:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    trainers = db.query(models.User).filter(
        models.User.role == "Trainer"
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="trainers.html",
        context={
            "trainers": trainers,
            "role": request.session.get("role"),
            "username": request.session.get("username")
        }
    )


# ======================
# ADMINS PAGE
# ======================

@app.get("/admins")
def admins(
    request: Request,
    db: Session = Depends(get_db)
):

    if "username" not in request.session:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    admins = db.query(models.User).filter(
        models.User.role == "Admin"
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="admins.html",
        context={
            "admins": admins,
            "role": request.session.get("role"),
            "username": request.session.get("username")
        }
    )

# ======================
# ADD RECORD PAGE
# ======================

@app.get("/add-student")
def add_student_page(
    request: Request
):

    if "username" not in request.session:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    if request.session.get("role") != "Admin":
        return RedirectResponse(
            url="/",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="add_student.html"
    )


# ======================
# SAVE RECORD
# ======================

@app.post("/add-student")
def add_student(
    request: Request,

    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),

    branch: str = Form(""),
    cgpa: str = Form(""),
    internship: str = Form(""),
    ppo: str = Form(""),
    placement_status: str = Form(""),
    company_name: str = Form(""),
    package: str = Form(""),

    department: str = Form(""),
    subject: str = Form(""),
    experience: str = Form(""),
    batch_assigned: str = Form(""),

    employee_id: str = Form(""),
    designation: str = Form(""),

    db: Session = Depends(get_db)
):

    if request.session.get("role") != "Admin":
        return RedirectResponse(
            url="/",
            status_code=303
        )

    user = models.User(
        name=name,
        email=email,
        role=role,

        branch=branch,
        cgpa=cgpa,
        internship=internship,
        ppo=ppo,
        placement_status=placement_status,
        company_name=company_name,
        package=package,

        department=department,
        subject=subject,
        experience=experience,
        batch_assigned=batch_assigned,

        employee_id=employee_id,
        designation=designation
    )

    db.add(user)
    db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )


# ======================
# EDIT PAGE
# ======================

@app.get("/edit-student/{student_id}")
def edit_student_page(
    student_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    if request.session.get("role") not in ["Admin", "Trainer"]:
        return RedirectResponse(
            url="/",
            status_code=303
        )

    student = db.query(models.User).filter(
        models.User.id == student_id
    ).first()

    return templates.TemplateResponse(
        request=request,
        name="edit_student.html",
        context={
            "student": student
        }
    )


# ======================
# UPDATE RECORD
# ======================

@app.post("/edit-student/{student_id}")
def edit_student(
    student_id: int,
    request: Request,

    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),

    branch: str = Form(""),
    cgpa: str = Form(""),
    internship: str = Form(""),
    ppo: str = Form(""),
    placement_status: str = Form(""),
    company_name: str = Form(""),
    package: str = Form(""),

    department: str = Form(""),
    subject: str = Form(""),
    experience: str = Form(""),
    batch_assigned: str = Form(""),

    employee_id: str = Form(""),
    designation: str = Form(""),

    db: Session = Depends(get_db)
):

    if request.session.get("role") not in ["Admin", "Trainer"]:
        return RedirectResponse(
            url="/",
            status_code=303
        )

    student = db.query(models.User).filter(
        models.User.id == student_id
    ).first()

    if student:

        student.name = name
        student.email = email
        student.role = role

        student.branch = branch
        student.cgpa = cgpa
        student.internship = internship
        student.ppo = ppo
        student.placement_status = placement_status
        student.company_name = company_name
        student.package = package

        student.department = department
        student.subject = subject
        student.experience = experience
        student.batch_assigned = batch_assigned

        student.employee_id = employee_id
        student.designation = designation

        db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )


# ======================
# DELETE RECORD
# ======================

@app.get("/delete-student/{student_id}")
def delete_student(
    student_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    if request.session.get("role") != "Admin":
        return RedirectResponse(
            url="/",
            status_code=303
        )

    student = db.query(models.User).filter(
        models.User.id == student_id
    ).first()

    if student:
        db.delete(student)
        db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )


# ======================
# DELETE ALL RECORDS
# ======================

@app.get("/delete-all")
def delete_all(
    request: Request,
    db: Session = Depends(get_db)
):

    if request.session.get("role") != "Admin":
        return RedirectResponse(
            url="/",
            status_code=303
        )

    db.query(models.User).delete()
    db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )
