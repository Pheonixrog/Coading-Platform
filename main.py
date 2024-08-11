from fastapi import FastAPI, Form, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from utils.javaCodeRun import compile_and_run_java as get_output_java
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from utils.mongodb import Database
from pydantic import BaseModel

db = Database()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key='pizzaa')
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ProblemSolution(BaseModel):
    solution_code: str
    input_data: str
    problem_id: str

@app.route("/", methods=["GET", "POST"])
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.route("/playground", methods=["GET", "POST"])
def read_playground(request: Request):
    return templates.TemplateResponse("playground.html", {"request": request})

@app.route("/problems", methods=["GET", "POST"])
def read_problems(request: Request):
    problems = db.get_problems()
    return templates.TemplateResponse("problems.html", {"request": request, "problems": problems})

@app.api_route("/problems/{problem_name}", methods=["GET", "POST"])
async def read_problem(request: Request, problem_name: str):
    print(problem_name)
    problem = db.get_problem_by_name(problem_name)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return templates.TemplateResponse("problem_detail.html", {"request": request, "problem": problem})


@app.route("/context", methods=["GET", "POST"])
def read_context(request: Request):
    return templates.TemplateResponse("context.html", {"request": request})

@app.get("/loginpg")
def read_w(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=JSONResponse)
def login(request: Request, data: dict):
    user = db.get_user(data["username"], data["password"])
    if type(user) == str:
        return {"error": user}
    else:
        request.session["username"] = user.username
        return {"success": "Login successful"}

@app.post("/register", response_class=JSONResponse)
def register(request: Request, data: dict):
    user = db.add_user(data["username"], data["name"], data["email"], data["password"])
    if type(user) == str:
        return {"error": user}
    else:
        request.session["username"] = user.username
        return {"success": "Registration successful"}

@app.post("/compile-and-run-java", response_class=JSONResponse)
def compile_and_run_java(data: dict):
    java_code = data["java_code"]
    input_data = data.get("input_data", "")
    response = get_output_java(java_code, input_data)
    print(response.__dict__)
    return response.__dict__

@app.post("/submit-solution", response_class=JSONResponse)
def submit_solution(solution: ProblemSolution, request: Request):
    problem = db.get_problem_by_id(solution.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    response = get_output_java(solution.solution_code, solution.input_data)

    # Validate the solution against the problem's test cases
    # This is a simple example; you may want to add more comprehensive checks
    for test_case in problem.test_cases:
        expected_output = test_case['output']
        actual_output = get_output_java(solution.solution_code, test_case['input']).output
        if expected_output.strip() != actual_output.strip():
            return {"success": False, "message": "Solution is incorrect"}

    # Update user points if solution is correct
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="User not authenticated")
    user = db.get_user_by_username(username)
    user.points += len(problem.difficulty) * 10  # Example point calculation
    db.update_user_points(user)

    return {"success": True, "message": "Solution is correct"}

@app.get("/get-problems", response_class=JSONResponse)
def get_problems():
    problems = db.get_problems()
    return [problem.to_dict() for problem in problems]

@app.route("/leaderboard", methods=["GET", "POST"])
def read_leaderboard(request: Request):
    return templates.TemplateResponse("leaderboard.html", {"request": request})

@app.get("/get-leaderboard", response_class=JSONResponse)
def get_leaderboard():
    users = db.get_leaderboard()
    return [user.to_dict() for user in users]