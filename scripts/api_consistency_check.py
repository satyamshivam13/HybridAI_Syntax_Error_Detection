from fastapi.testclient import TestClient

import api
from src.error_engine import detect_errors


cases = [
    ("Python", "def test():\nprint('Hello')"),
    ("JavaScript", "let x = 10;\nconsole.log(x);"),
    (
        "Java",
        "public class Main {\n public static void main(String[] args){\n int a = \"x\";\n }\n}",
    ),
]

client = TestClient(api.app)

for language, code in cases:
    engine = detect_errors(code, language_override=language)
    response = client.post("/check", json={"code": code, "language": language})
    body = response.json()
    print(
        language,
        "engine=", engine["predicted_error"],
        "api=", body.get("predicted_error"),
        "match=", engine["predicted_error"] == body.get("predicted_error"),
    )
