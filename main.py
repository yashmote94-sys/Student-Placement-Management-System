from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import models
from database import engine
from dependencies import get_db

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


# DASHBOARD
@app.get("/")
def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    students = db.query(models.User).all()

    total_students = len(students)

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
            package_value = str(s.package)

            package_value = package_value.replace("LPA", "")
            package_value = package_value.replace("lpa", "")
            package_value = package_value.replace("₹", "")
            package_value = package_value.strip()

            packages.append(float(package_value))

        except:
            pass

    avg_cgpa = round(sum(cgpas) / len(cgpas), 2) if cgpas else 0

    highest_package = max(packages) if packages else 0

    placement_percentage = (
        round((placed_students / total_students) * 100, 2)
        if total_students > 0
        else 0
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "total_students": total_students,
            "placed_students": placed_students,
            "internship_count": internship_count,
            "ppo_count": ppo_count,
            "avg_cgpa": avg_cgpa,
            "highest_package": highest_package,
            "placement_percentage": placement_percentage
        }
    )


# STUDENTS LIST
@app.get("/students")
def students(
    request: Request,
    search: str = "",
    db: Session = Depends(get_db)
):
    students_query = db.query(models.User)

    if search:
        students_query = students_query.filter(
            models.User.name.contains(search)
        )

    student_list = students_query.all()

    return templates.TemplateResponse(
        request=request,
        name="students.html",
        context={
            "students": student_list,
            "search": search
        }
    )


# ADD STUDENT PAGE
@app.get("/add-student")
def add_student_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="add_student.html"
    )


# SAVE STUDENT
@app.post("/add-student")
def add_student(
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    branch: str = Form(...),
    cgpa: str = Form(...),
    internship: str = Form(...),
    ppo: str = Form(...),
    placement_status: str = Form(...),
    company_name: str = Form(...),
    package: str = Form(...),
    db: Session = Depends(get_db)
):
    student = models.User(
        name=name,
        email=email,
        role=role,
        branch=branch,
        cgpa=cgpa,
        internship=internship,
        ppo=ppo,
        placement_status=placement_status,
        company_name=company_name,
        package=package
    )

    db.add(student)
    db.commit()

    return RedirectResponse(
        url="/students",
        status_code=303
    )


# EDIT PAGE
@app.get("/edit-student/{student_id}")
def edit_student_page(
    student_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
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


# UPDATE STUDENT
@app.post("/edit-student/{student_id}")
def edit_student(
    student_id: int,
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    branch: str = Form(...),
    cgpa: str = Form(...),
    internship: str = Form(...),
    ppo: str = Form(...),
    placement_status: str = Form(...),
    company_name: str = Form(...),
    package: str = Form(...),
    db: Session = Depends(get_db)
):
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

        db.commit()

    return RedirectResponse(
        url="/students",
        status_code=303
    )


# DELETE STUDENT
@app.get("/delete-student/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = db.query(models.User).filter(
        models.User.id == student_id
    ).first()

    if student:
        db.delete(student)
        db.commit()

    return RedirectResponse(
        url="/students",
        status_code=303
    )