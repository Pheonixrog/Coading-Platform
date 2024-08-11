from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from time import time as get_time
from matrix.javaCodeRun import compile_and_run_java as get_output_java
import subprocess
import os
import tempfile

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/compile-and-run-java", response_class=JSONResponse)
def compile_and_run_java(data: dict):
    java_code = data["java_code"]
    input_data = data.get("input_data", "")
    response = get_output_java(java_code, input_data)
    print(response.__dict__)
    return response.__dict__





