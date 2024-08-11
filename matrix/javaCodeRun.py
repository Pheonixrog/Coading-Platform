from time import time as get_time
from dataclasses import dataclass
import subprocess
import os
import tempfile
import psutil

@dataclass
class JavaCodeRun:
    javaCode: str
    inputData: str = ""
    error: str = None
    compileTime: float = -1
    executionTime: float = -1
    memoryUsage: float = -1
    detail: str = None

def compile_and_run_java(java_code: str, input_data: str = "") -> JavaCodeRun:
    returnObj = JavaCodeRun(javaCode=java_code, inputData=input_data)

    with tempfile.TemporaryDirectory() as tmpdir:
        java_file = os.path.join(tmpdir, "Main.java")
        
        with open(java_file, "w") as f:
            f.write(java_code)
        
        def compile():
            compileTime = get_time()
            compile_process = subprocess.run(
                ["javac", java_file],
                capture_output=True,
                text=True
            )
            compileTime = get_time() - compileTime
            returnObj.compileTime = compileTime

            if compile_process.returncode != 0:
                returnObj.error = compile_process.stderr
                return returnObj
        
        if compile() is not None: return returnObj

        input_file = os.path.join(tmpdir, "input.txt")
        with open(input_file, "w") as f:
            f.write(input_data)

        def run():
            # Start tracking memory usage
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss

            executionTime = get_time()
            run_process = subprocess.run(
                ["java", "-cp", tmpdir, "Main"],
                input=open(input_file).read(),
                capture_output=True,
                text=True
            )
            executionTime = get_time() - executionTime
            returnObj.executionTime = executionTime

            # Memory usage after execution
            memory_after = process.memory_info().rss
            returnObj.memoryUsage = memory_after - memory_before
            
            if run_process.returncode != 0:
                returnObj.error = run_process.stderr
                return returnObj

            returnObj.output = run_process.stdout

        if run() is not None: return returnObj
        
        return returnObj

