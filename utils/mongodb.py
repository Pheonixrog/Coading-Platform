from dataclasses import dataclass, field
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

uri = "mongodb+srv://shukladivyansh953:sxxDwR6CsCB9WbYc@j4e.rrdgwlw.mongodb.net/?retryWrites=true&w=majority&appName=J4E"

client = MongoClient(uri)

db = client["coding_platform"]

@dataclass
class Problem:
    _id: ObjectId
    name: str
    description: str
    difficulty: str
    constraints: str
    sample_inputs: list
    sample_outputs: list
    test_cases: list
    created_by: str
    created_at: datetime

    def to_dict(self):
        return {
            "_id": str(self._id),
            "name": self.name,
            "description": self.description,
            "difficulty": self.difficulty,
            "constraints": self.constraints,
            "sample_inputs": self.sample_inputs,
            "sample_outputs": self.sample_outputs,
            "test_cases": self.test_cases,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class User:
    _id: ObjectId
    username: str
    name: str
    email: str
    password: str
    created_at: datetime
    bio: str = "I like Java"
    avatar: str = None
    points: float = 0
    problems_submitted: list[ObjectId] = field(default_factory=list)
    solved_problems: list[ObjectId] = field(default_factory=list)
    def to_dict(self):
        return {
            "_id": str(self._id),
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at.isoformat(),
            "bio": self.bio,
            "avatar": self.avatar,
            "points": self.points,
            "problems_submitted": self.problems_submitted,
            "solved_problems": self.solved_problems
        }

class Database:
    def __init__(self):
        self.problems = db["Problems"]
        self.users = db["Users"]

    def add_user(
        self,
        username: str,
        name: str,
        email: str,
        password: str
    ) -> User:
        if self.users.find_one({"username": username}):
            return "User already exists"
        created_at = datetime.now()
        self.users.insert_one({
            "username": username,
            "name": name,
            "email": email,
            "password": password,
            "created_at": created_at,
            "bio": "I like Java",
            "avatar": None,
            "points": 0,
            "problems_submitted": [],
            "solved_problems": []
        })
        return User(**self.users.find_one({"username": username}))

    def add_problem(
        self,
        name: str,
        description: str,
        difficulty: str,
        constraints: str,
        sample_inputs: list,
        sample_outputs: list,
        test_cases: list,
        created_by: str,
    ) -> Problem:
        created_at = datetime.now()
        self.problems.insert_one({
            "name": name,
            "description": description,
            "difficulty": difficulty,
            "constraints": constraints,
            "sample_inputs": sample_inputs,
            "sample_outputs": sample_outputs,
            "test_cases": test_cases,
            "created_by": created_by,
            "created_at": created_at
        })
        return Problem(**self.problems.find_one({"name": name, "created_by": created_by}))

    def get_user(self, username: str, password: str) -> User:
        user = self.users.find_one({"username": username})
        if user and user["password"] == password:
            return User(**user)
        return "User not found or wrong password"
    def get_user_by_username(self, username: str) -> User:
        user = self.users.find_one({"username": username})
        if user:
            return User(**user)
        return None
    def get_problems(self) -> list[Problem]:
        problems = []
        for problem in self.problems.find():
            problems.append(Problem(**problem))
        return problems

    def get_problems_by_difficulty(self, difficulty: str) -> list[Problem]:
        problems = []
        for problem in self.problems.find({"difficulty": difficulty}):
            problems.append(Problem(**problem))
        return problems

    def get_leaderboard(self) -> list[User]:
        users = self.users.find().sort("points", -1)
        return [User(**user) for user in users]
    def get_problem_by_name(self, problem_name: str) -> Problem:
        problem = self.problems.find_one({"name": problem_name})
        if problem:
            return Problem(**problem)
        return None

    def get_problem_by_id(self, problem_id: str) -> Problem:
        problem = self.problems.find_one({"_id": ObjectId(problem_id)})
        if problem:
            return Problem(**problem)
        return None

    def get_problems(self) -> list[Problem]:
        problems = []
        for problem in self.problems.find():
            problems.append(Problem(**problem))
        return problems

    def update_user_points(self, user: User):
        self.users.update_one(
            {"_id": user._id},
            {"$set": {"points": user.points}}
        )
