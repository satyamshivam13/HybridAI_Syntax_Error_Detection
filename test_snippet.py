from src.multi_error_detector import detect_all_errors

code = "def foo():\\n    print('hello world')"
print(code)
print(repr(code))
result = detect_all_errors(code, "test.py")
print("has_errors:", result['has_errors'])
print("errors:", result['errors'])
