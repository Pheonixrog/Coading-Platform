
import requests
from rich import print
java_code = """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
"""

response = requests.post("http://localhost:8000/compile-and-run-java", json={"java_code": java_code})

if response.status_code == 200:
    print("Output:", response.json())
else:
    print("Error:", response.text)