"""
augment_dataset.py
==================
Extends the training dataset to 200+ samples per error type.

Targets (samples needed):
  UndeclaredIdentifier  : +153
  UnreachableCode       : +134
  UnusedVariable        : +122
  NoError               : +117
  DuplicateDefinition   : +116
  UnclosedString        : +110
  NameError             : +100
  MutableDefault        : +100
  LineTooLong           : +100
  MissingImport         : +98
  WildcardImport        : +97
  IndentationError      : +96
  ImportError           : +96
  InfiniteLoop          : +95
  UnmatchedBracket      : +95
  MissingInclude        : +89
  InvalidAssignment     : +30

Usage:
    python augment_dataset.py
    python augment_dataset.py --output dataset/merged/all_errors_v3.csv
    python augment_dataset.py --preview   # show counts without writing
"""

import csv
import os
import argparse
import random
from collections import Counter

# ─────────────────────────────────────────────────────────────────────────────
# NEW SAMPLES — diverse, varied, realistic
# Each entry: (language, error_type, buggy_code)
# ─────────────────────────────────────────────────────────────────────────────

NEW_SAMPLES = []

# =============================================================================
# UndeclaredIdentifier (+153 needed)
# =============================================================================
UNDECLARED = [
    # Python
    ("Python","UndeclaredIdentifier","result = calculate(10, 5)\nprint(result)"),
    ("Python","UndeclaredIdentifier","for item in inventory:\n    print(item.price)"),
    ("Python","UndeclaredIdentifier","total = sum(prices)\nprint(average)"),
    ("Python","UndeclaredIdentifier","if user.is_admin:\n    grant_access()"),
    ("Python","UndeclaredIdentifier","df = pd.DataFrame(data)\nprint(df.head())"),
    ("Python","UndeclaredIdentifier","response = requests.get(url)\nprint(response.json())"),
    ("Python","UndeclaredIdentifier","x = math.sqrt(16)\nprint(x)"),
    ("Python","UndeclaredIdentifier","config = load_config()\nprint(settings.debug)"),
    ("Python","UndeclaredIdentifier","values = [1, 2, 3]\nprint(total_sum)"),
    ("Python","UndeclaredIdentifier","name = input('Enter name: ')\nprint(greeting)"),
    ("Python","UndeclaredIdentifier","data = fetch_data()\nresult = process(raw_data)"),
    ("Python","UndeclaredIdentifier","numbers = [1,2,3,4,5]\nprint(maximum)"),
    ("Python","UndeclaredIdentifier","user_input = input()\nif validated:\n    proceed()"),
    ("Python","UndeclaredIdentifier","matrix = [[1,2],[3,4]]\nprint(determinant)"),
    ("Python","UndeclaredIdentifier","def compute():\n    return result + offset"),
    # Java
    ("Java","UndeclaredIdentifier","public class Main {\n    public static void main(String[] args) {\n        System.out.println(count);\n    }\n}"),
    ("Java","UndeclaredIdentifier","public class Main {\n    public static void main(String[] args) {\n        result = 42;\n        System.out.println(result);\n    }\n}"),
    ("Java","UndeclaredIdentifier","public class Main {\n    public static void main(String[] args) {\n        int sum = a + b;\n        System.out.println(sum);\n    }\n}"),
    ("Java","UndeclaredIdentifier","public class Main {\n    public static void main(String[] args) {\n        if (isValid) {\n            System.out.println(\"Valid\");\n        }\n    }\n}"),
    ("Java","UndeclaredIdentifier","public class Main {\n    public static void main(String[] args) {\n        for (int i = 0; i < maxSize; i++) {\n            System.out.println(i);\n        }\n    }\n}"),
    ("Java","UndeclaredIdentifier","public class Calculator {\n    public int add(int a, int b) {\n        return a + b + offset;\n    }\n}"),
    ("Java","UndeclaredIdentifier","public class Main {\n    public static void main(String[] args) {\n        String result = getName();\n        System.out.println(result);\n    }\n}"),
    ("Java","UndeclaredIdentifier","public class Main {\n    public static void main(String[] args) {\n        int x = value * 2;\n        System.out.println(x);\n    }\n}"),
    # C
    ("C","UndeclaredIdentifier","#include <stdio.h>\nint main() {\n    printf(\"%d\\n\", count);\n    return 0;\n}"),
    ("C","UndeclaredIdentifier","#include <stdio.h>\nint main() {\n    int result = x + y;\n    printf(\"%d\\n\", result);\n    return 0;\n}"),
    ("C","UndeclaredIdentifier","#include <stdio.h>\nint main() {\n    for (int i = 0; i < max; i++) {\n        printf(\"%d\\n\", i);\n    }\n    return 0;\n}"),
    ("C","UndeclaredIdentifier","#include <stdio.h>\nvoid process() {\n    printf(\"%s\\n\", message);\n}"),
    ("C","UndeclaredIdentifier","#include <stdio.h>\nint main() {\n    if (flag) {\n        printf(\"Active\\n\");\n    }\n    return 0;\n}"),
    ("C","UndeclaredIdentifier","#include <stdio.h>\nint main() {\n    int total = base + tax;\n    printf(\"%d\\n\", total);\n    return 0;\n}"),
    # C++
    ("C++","UndeclaredIdentifier","#include <iostream>\nusing namespace std;\nint main() {\n    cout << count << endl;\n    return 0;\n}"),
    ("C++","UndeclaredIdentifier","#include <iostream>\nusing namespace std;\nint main() {\n    int result = x * factor;\n    cout << result << endl;\n    return 0;\n}"),
    ("C++","UndeclaredIdentifier","#include <iostream>\nusing namespace std;\nvoid display() {\n    cout << message << endl;\n}"),
    ("C++","UndeclaredIdentifier","#include <iostream>\nusing namespace std;\nint main() {\n    for (int i = 0; i < limit; i++) {\n        cout << i << endl;\n    }\n    return 0;\n}"),
    ("C++","UndeclaredIdentifier","#include <iostream>\nusing namespace std;\nint main() {\n    if (isReady) {\n        cout << \"Ready\" << endl;\n    }\n    return 0;\n}"),
]
NEW_SAMPLES.extend(UNDECLARED)

# =============================================================================
# UnreachableCode (+134 needed)
# =============================================================================
UNREACHABLE = [
    # Python
    ("Python","UnreachableCode","def get_value():\n    return 42\n    print('done')"),
    ("Python","UnreachableCode","def check(x):\n    if x > 0:\n        return True\n    else:\n        return False\n    return None"),
    ("Python","UnreachableCode","def process():\n    return result\n    cleanup()"),
    ("Python","UnreachableCode","for i in range(10):\n    break\n    print(i)"),
    ("Python","UnreachableCode","while True:\n    break\n    do_work()"),
    ("Python","UnreachableCode","def calculate(x):\n    return x * 2\n    x = x + 1\n    return x"),
    ("Python","UnreachableCode","def validate(data):\n    if not data:\n        raise ValueError('empty')\n        return False"),
    ("Python","UnreachableCode","def find_max(lst):\n    return max(lst)\n    result = sorted(lst)[-1]\n    return result"),
    ("Python","UnreachableCode","def greet(name):\n    return f'Hello {name}'\n    print(f'Greeting {name}')"),
    ("Python","UnreachableCode","for item in items:\n    if item < 0:\n        continue\n        print('skipped')"),
    ("Python","UnreachableCode","def connect():\n    return connection\n    connection.close()"),
    ("Python","UnreachableCode","def safe_divide(a, b):\n    if b == 0:\n        raise ZeroDivisionError()\n        return 0\n    return a / b"),
    # Java
    ("Java","UnreachableCode","public class Main {\n    public static int getValue() {\n        return 42;\n        System.out.println(\"done\");\n    }\n}"),
    ("Java","UnreachableCode","public class Main {\n    public static void main(String[] args) {\n        return;\n        System.out.println(\"unreachable\");\n    }\n}"),
    ("Java","UnreachableCode","public class Main {\n    public static boolean check(int x) {\n        if (x > 0) return true;\n        else return false;\n        return false;\n    }\n}"),
    ("Java","UnreachableCode","public class Main {\n    public static void process() {\n        throw new RuntimeException();\n        cleanup();\n    }\n}"),
    ("Java","UnreachableCode","public class Main {\n    public static int compute(int x) {\n        return x * 2;\n        int y = x + 1;\n        return y;\n    }\n}"),
    ("Java","UnreachableCode","public class Main {\n    public static void main(String[] args) {\n        for (int i = 0; i < 10; i++) {\n            break;\n            System.out.println(i);\n        }\n    }\n}"),
    # C
    ("C","UnreachableCode","int getValue() {\n    return 42;\n    printf(\"done\\n\");\n}"),
    ("C","UnreachableCode","int main() {\n    return 0;\n    printf(\"unreachable\\n\");\n}"),
    ("C","UnreachableCode","void process() {\n    return;\n    cleanup();\n}"),
    ("C","UnreachableCode","int compute(int x) {\n    return x * 2;\n    x = x + 1;\n    return x;\n}"),
    ("C","UnreachableCode","int main() {\n    for (int i = 0; i < 10; i++) {\n        break;\n        printf(\"%d\\n\", i);\n    }\n    return 0;\n}"),
    # C++
    ("C++","UnreachableCode","int getValue() {\n    return 42;\n    cout << \"done\" << endl;\n}"),
    ("C++","UnreachableCode","int main() {\n    return 0;\n    cout << \"unreachable\" << endl;\n}"),
    ("C++","UnreachableCode","void process() {\n    throw runtime_error(\"error\");\n    cleanup();\n}"),
    ("C++","UnreachableCode","int compute(int x) {\n    return x * 2;\n    x = x + 1;\n    return x;\n}"),
    ("C++","UnreachableCode","int main() {\n    for (int i = 0; i < 10; i++) {\n        break;\n        cout << i << endl;\n    }\n    return 0;\n}"),
]
NEW_SAMPLES.extend(UNREACHABLE)

# =============================================================================
# UnusedVariable (+122 needed)
# =============================================================================
UNUSED = [
    ("Python","UnusedVariable","def process(data):\n    temp = data * 2\n    result = data + 1\n    return result"),
    ("Python","UnusedVariable","def calculate():\n    unused = 42\n    return 0"),
    ("Python","UnusedVariable","x = 10\ny = 20\nprint(x)"),
    ("Python","UnusedVariable","def get_name():\n    prefix = 'Mr'\n    name = 'Alice'\n    return name"),
    ("Python","UnusedVariable","for i in range(10):\n    count = i * 2\n    print(i)"),
    ("Python","UnusedVariable","def fetch():\n    cache = {}\n    return requests.get(url)"),
    ("Python","UnusedVariable","a = 1\nb = 2\nc = 3\nprint(a + b)"),
    ("Python","UnusedVariable","def parse(text):\n    words = text.split()\n    length = len(text)\n    return words"),
    ("Python","UnusedVariable","def connect(host, port):\n    timeout = 30\n    return socket.connect(host, port)"),
    ("Python","UnusedVariable","class Config:\n    def __init__(self):\n        self.version = '1.0'\n        self.debug = False\n        self.unused = None"),
    ("Python","UnusedVariable","def transform(data):\n    original = data.copy()\n    return [x * 2 for x in data]"),
    ("Python","UnusedVariable","numbers = [1,2,3,4,5]\ntotal = sum(numbers)\naverage = total / len(numbers)\nmaximum = max(numbers)\nprint(average)"),
    # Java
    ("Java","UnusedVariable","public class Main {\n    public static void main(String[] args) {\n        int unused = 42;\n        System.out.println(\"hello\");\n    }\n}"),
    ("Java","UnusedVariable","public class Main {\n    public static int compute(int x) {\n        int temp = x * 2;\n        int result = x + 1;\n        return result;\n    }\n}"),
    ("Java","UnusedVariable","public class Main {\n    public static void main(String[] args) {\n        String name = \"Alice\";\n        int age = 30;\n        System.out.println(name);\n    }\n}"),
    ("Java","UnusedVariable","public class Main {\n    public static void process() {\n        int counter = 0;\n        int total = 100;\n        System.out.println(total);\n    }\n}"),
    # C
    ("C","UnusedVariable","int main() {\n    int unused = 42;\n    printf(\"hello\\n\");\n    return 0;\n}"),
    ("C","UnusedVariable","int compute(int x) {\n    int temp = x * 2;\n    int result = x + 1;\n    return result;\n}"),
    ("C","UnusedVariable","int main() {\n    int a = 5;\n    int b = 10;\n    int c = 15;\n    printf(\"%d\\n\", a + b);\n    return 0;\n}"),
    # C++
    ("C++","UnusedVariable","int main() {\n    int unused = 42;\n    cout << \"hello\" << endl;\n    return 0;\n}"),
    ("C++","UnusedVariable","int compute(int x) {\n    int temp = x * 2;\n    int result = x + 1;\n    return result;\n}"),
    ("C++","UnusedVariable","int main() {\n    string name = \"Alice\";\n    int age = 30;\n    cout << name << endl;\n    return 0;\n}"),
]
NEW_SAMPLES.extend(UNUSED)

# =============================================================================
# NoError (+117 needed) — valid code that should return NoError
# =============================================================================
NOERROR = [
    ("Python","NoError","def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)"),
    ("Python","NoError","class Stack:\n    def __init__(self):\n        self.items = []\n    def push(self, item):\n        self.items.append(item)\n    def pop(self):\n        return self.items.pop()"),
    ("Python","NoError","import json\nwith open('data.json') as f:\n    data = json.load(f)\nprint(data)"),
    ("Python","NoError","numbers = [3,1,4,1,5,9,2,6]\nnumbers.sort()\nprint(numbers)"),
    ("Python","NoError","def binary_search(arr, target):\n    left, right = 0, len(arr)-1\n    while left <= right:\n        mid = (left+right)//2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid+1\n        else:\n            right = mid-1\n    return -1"),
    ("Python","NoError","from collections import defaultdict\ngraph = defaultdict(list)\ngraph['a'].append('b')"),
    ("Python","NoError","import os\nfiles = [f for f in os.listdir('.') if f.endswith('.py')]\nprint(len(files))"),
    ("Python","NoError","def merge_dicts(*dicts):\n    result = {}\n    for d in dicts:\n        result.update(d)\n    return result"),
    ("Python","NoError","try:\n    with open('config.txt') as f:\n        config = f.read()\nexcept FileNotFoundError:\n    config = '{}'"),
    ("Python","NoError","class Node:\n    def __init__(self, val):\n        self.val = val\n        self.next = None"),
    ("Python","NoError","data = {'name': 'Alice', 'scores': [95, 87, 92]}\navg = sum(data['scores']) / len(data['scores'])\nprint(f\"{data['name']}: {avg:.1f}\")"),
    ("Python","NoError","def is_palindrome(s):\n    s = s.lower().replace(' ', '')\n    return s == s[::-1]"),
    ("Python","NoError","import re\npattern = re.compile(r'\\d+')\nmatches = pattern.findall('abc 123 def 456')\nprint(matches)"),
    ("Python","NoError","matrix = [[1,2,3],[4,5,6],[7,8,9]]\ntransposed = [[row[i] for row in matrix] for i in range(3)]"),
    ("Python","NoError","from functools import reduce\nnumbers = [1,2,3,4,5]\nproduct = reduce(lambda x,y: x*y, numbers)\nprint(product)"),
    ("Python","NoError","def count_words(text):\n    words = text.lower().split()\n    counts = {}\n    for word in words:\n        counts[word] = counts.get(word, 0) + 1\n    return counts"),
    ("Python","NoError","import datetime\nnow = datetime.datetime.now()\nprint(now.strftime('%Y-%m-%d'))"),
    ("Python","NoError","class Queue:\n    def __init__(self):\n        self.items = []\n    def enqueue(self, x):\n        self.items.append(x)\n    def dequeue(self):\n        return self.items.pop(0)\n    def is_empty(self):\n        return len(self.items) == 0"),
    ("Python","NoError","def flatten(lst):\n    result = []\n    for item in lst:\n        if isinstance(item, list):\n            result.extend(flatten(item))\n        else:\n            result.append(item)\n    return result"),
    ("Python","NoError","squares = {x: x**2 for x in range(1, 11)}\nprint(squares)"),
    # Java
    ("Java","NoError","public class Calculator {\n    public int add(int a, int b) { return a + b; }\n    public int subtract(int a, int b) { return a - b; }\n    public int multiply(int a, int b) { return a * b; }\n}"),
    ("Java","NoError","import java.util.ArrayList;\npublic class Main {\n    public static void main(String[] args) {\n        ArrayList<Integer> list = new ArrayList<>();\n        list.add(1);\n        list.add(2);\n        System.out.println(list.size());\n    }\n}"),
    ("Java","NoError","public class Fibonacci {\n    public static int fib(int n) {\n        if (n <= 1) return n;\n        return fib(n-1) + fib(n-2);\n    }\n    public static void main(String[] args) {\n        System.out.println(fib(10));\n    }\n}"),
    ("Java","NoError","import java.util.Arrays;\npublic class Main {\n    public static void main(String[] args) {\n        int[] arr = {5, 3, 1, 4, 2};\n        Arrays.sort(arr);\n        System.out.println(Arrays.toString(arr));\n    }\n}"),
    # C
    ("C","NoError","#include <stdio.h>\n#include <stdlib.h>\nint main() {\n    int *arr = malloc(5 * sizeof(int));\n    for (int i = 0; i < 5; i++) arr[i] = i;\n    free(arr);\n    return 0;\n}"),
    ("C","NoError","#include <stdio.h>\n#include <string.h>\nint main() {\n    char str[] = \"hello\";\n    printf(\"%d\\n\", strlen(str));\n    return 0;\n}"),
    ("C","NoError","#include <stdio.h>\nint factorial(int n) {\n    if (n <= 1) return 1;\n    return n * factorial(n-1);\n}\nint main() {\n    printf(\"%d\\n\", factorial(5));\n    return 0;\n}"),
    # C++
    ("C++","NoError","#include <iostream>\n#include <vector>\n#include <algorithm>\nusing namespace std;\nint main() {\n    vector<int> v = {3,1,4,1,5,9};\n    sort(v.begin(), v.end());\n    for (int x : v) cout << x << ' ';\n    return 0;\n}"),
    ("C++","NoError","#include <iostream>\n#include <map>\nusing namespace std;\nint main() {\n    map<string,int> scores;\n    scores[\"Alice\"] = 95;\n    scores[\"Bob\"] = 87;\n    for (auto& p : scores) cout << p.first << \":\" << p.second << endl;\n    return 0;\n}"),
    ("C++","NoError","#include <iostream>\nusing namespace std;\nclass Rectangle {\npublic:\n    double width, height;\n    Rectangle(double w, double h) : width(w), height(h) {}\n    double area() { return width * height; }\n};\nint main() {\n    Rectangle r(3.0, 4.0);\n    cout << r.area() << endl;\n    return 0;\n}"),
]
NEW_SAMPLES.extend(NOERROR)

# =============================================================================
# DuplicateDefinition (+116 needed)
# =============================================================================
DUPLICATE = [
    ("Python","DuplicateDefinition","def calculate(x):\n    return x * 2\n\ndef calculate(x):\n    return x + 2"),
    ("Python","DuplicateDefinition","class Animal:\n    pass\n\nclass Animal:\n    def speak(self):\n        print('...')"),
    ("Python","DuplicateDefinition","MAX = 100\nMIN = 0\nMAX = 200"),
    ("Python","DuplicateDefinition","def process(data):\n    return data\n\ndef validate(data):\n    return True\n\ndef process(data):\n    return data.strip()"),
    ("Python","DuplicateDefinition","class Config:\n    DEBUG = True\n    DEBUG = False"),
    ("Python","DuplicateDefinition","def get_name():\n    return 'Alice'\n\ndef get_age():\n    return 30\n\ndef get_name():\n    return 'Bob'"),
    ("Python","DuplicateDefinition","x = 10\ny = 20\nx = 30\nz = x + y"),
    ("Python","DuplicateDefinition","class User:\n    def __init__(self, name):\n        self.name = name\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age"),
    ("Python","DuplicateDefinition","import os\nimport sys\nimport os"),
    ("Python","DuplicateDefinition","def sort_data(data):\n    return sorted(data)\n\ndef filter_data(data):\n    return [x for x in data if x > 0]\n\ndef sort_data(data):\n    return data[::-1]"),
    ("Python","DuplicateDefinition","PI = 3.14159\nE = 2.71828\nPI = 3.14"),
    ("Python","DuplicateDefinition","class Database:\n    def connect(self):\n        pass\n    def query(self):\n        pass\n    def connect(self):\n        return True"),
    # Java
    ("Java","DuplicateDefinition","public class Main {\n    public static int value = 10;\n    public static int value = 20;\n    public static void main(String[] args) {\n        System.out.println(value);\n    }\n}"),
    ("Java","DuplicateDefinition","public class Main {\n    public static void print() {\n        System.out.println(\"first\");\n    }\n    public static void print() {\n        System.out.println(\"second\");\n    }\n    public static void main(String[] args) {\n        print();\n    }\n}"),
    ("Java","DuplicateDefinition","public class Shape {\n    private int width;\n    private int height;\n    private int width;\n}"),
    # C
    ("C","DuplicateDefinition","#include <stdio.h>\nint x = 10;\nint x = 20;\nint main() {\n    printf(\"%d\\n\", x);\n    return 0;\n}"),
    ("C","DuplicateDefinition","#include <stdio.h>\nvoid greet() { printf(\"Hello\\n\"); }\nvoid greet() { printf(\"Hi\\n\"); }\nint main() {\n    greet();\n    return 0;\n}"),
    ("C","DuplicateDefinition","#include <stdio.h>\n#define MAX 100\n#define MAX 200\nint main() {\n    printf(\"%d\\n\", MAX);\n    return 0;\n}"),
    # C++
    ("C++","DuplicateDefinition","#include <iostream>\nusing namespace std;\nint counter = 0;\nint counter = 10;\nint main() {\n    cout << counter << endl;\n    return 0;\n}"),
    ("C++","DuplicateDefinition","#include <iostream>\nusing namespace std;\nvoid display() { cout << \"first\" << endl; }\nvoid display() { cout << \"second\" << endl; }\nint main() {\n    display();\n    return 0;\n}"),
]
NEW_SAMPLES.extend(DUPLICATE)

# =============================================================================
# UnclosedString (+110 needed)
# =============================================================================
UNCLOSED = [
    ("Python","UnclosedString","print('Hello World)"),
    ("Python","UnclosedString","name = \"Alice\nprint(name)"),
    ("Python","UnclosedString","message = 'Welcome to Python\nprint(message)"),
    ("Python","UnclosedString","title = \"Chapter 1: Introduction\nprint(title)"),
    ("Python","UnclosedString","path = '/home/user/documents\nopen(path)"),
    ("Python","UnclosedString","greeting = 'Hello ' + name + '!\nprint(greeting)"),
    ("Python","UnclosedString","query = \"SELECT * FROM users WHERE name = 'Alice\"\ndb.execute(query)"),
    ("Python","UnclosedString","url = 'https://api.example.com/data\nresponse = requests.get(url)"),
    ("Python","UnclosedString","error_msg = \"File not found: \" + filename + \"\nraise FileNotFoundError(error_msg)"),
    ("Python","UnclosedString","pattern = r'\\d+\\.\\d+\nre.findall(pattern, text)"),
    ("Python","UnclosedString","label = 'Score: ' + str(score) + ' points\nprint(label)"),
    ("Python","UnclosedString","csv_line = str(id) + ',' + name + ',' + str(age) + '\nwriter.write(csv_line)"),
    # Java
    ("Java","UnclosedString","public class Main {\n    public static void main(String[] args) {\n        String msg = \"Hello World;\n        System.out.println(msg);\n    }\n}"),
    ("Java","UnclosedString","public class Main {\n    public static void main(String[] args) {\n        String name = \"Alice;\n        System.out.println(\"Hello \" + name);\n    }\n}"),
    ("Java","UnclosedString","public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Welcome to Java);\n    }\n}"),
    # C
    ("C","UnclosedString","#include <stdio.h>\nint main() {\n    printf(\"Hello, World!\\n);\n    return 0;\n}"),
    ("C","UnclosedString","#include <stdio.h>\nint main() {\n    char *msg = \"Unclosed string;\n    printf(\"%s\\n\", msg);\n    return 0;\n}"),
    ("C","UnclosedString","#include <stdio.h>\nint main() {\n    printf(\"Value: %d\\n, 42);\n    return 0;\n}"),
    # C++
    ("C++","UnclosedString","#include <iostream>\nusing namespace std;\nint main() {\n    string msg = \"Hello World;\n    cout << msg << endl;\n    return 0;\n}"),
    ("C++","UnclosedString","#include <iostream>\nusing namespace std;\nint main() {\n    cout << \"Welcome to C++; << endl;\n    return 0;\n}"),
]
NEW_SAMPLES.extend(UNCLOSED)

# =============================================================================
# NameError (+100 needed)
# =============================================================================
NAMEERROR = [
    ("Python","NameError","print(undefined_variable)"),
    ("Python","NameError","result = unknown_function(10)"),
    ("Python","NameError","x = UndefinedClass()"),
    ("Python","NameError","for item in uninitialized_list:\n    print(item)"),
    ("Python","NameError","if nonexistent_flag:\n    process()"),
    ("Python","NameError","total = sum + extra_amount"),
    ("Python","NameError","print(fist_name)"),
    ("Python","NameError","data = loaad_data()"),
    ("Python","NameError","result = calculte(x, y)"),
    ("Python","NameError","value = get_reslt()"),
    ("Python","NameError","items = fetch_form_db()"),
    ("Python","NameError","user = Usr('Alice', 30)"),
    ("Python","NameError","config = load_cofig('app.ini')"),
    ("Python","NameError","response = reequests.get(url)"),
    ("Python","NameError","df = panda.DataFrame(data)"),
    ("Python","NameError","import math\nresult = math.squart(16)"),
    ("Python","NameError","numbers = [1,2,3]\nprint(numbres)"),
    ("Python","NameError","def greet(name):\n    return f'Hello {naem}'"),
    ("Python","NameError","class Dog:\n    def bark(self):\n        print(selff.name)"),
    ("Python","NameError","try:\n    result = int('abc')\nexcept ValueEror:\n    result = 0"),
]
NEW_SAMPLES.extend(NAMEERROR)

# =============================================================================
# MutableDefault (+100 needed)
# =============================================================================
MUTABLE = [
    ("Python","MutableDefault","def append_item(item, lst=[]):\n    lst.append(item)\n    return lst"),
    ("Python","MutableDefault","def add_entry(key, value, cache={}):\n    cache[key] = value\n    return cache"),
    ("Python","MutableDefault","def collect(item, results=[]):\n    results.append(item)\n    return results"),
    ("Python","MutableDefault","def process(data, output=[]):\n    output.append(data * 2)\n    return output"),
    ("Python","MutableDefault","def register(name, users=[]):\n    users.append(name)\n    return users"),
    ("Python","MutableDefault","def track(event, log=[]):\n    log.append(event)\n    return log"),
    ("Python","MutableDefault","def store(item, storage={}):\n    storage[id(item)] = item\n    return storage"),
    ("Python","MutableDefault","def add_tag(tag, tags=set()):\n    tags.add(tag)\n    return tags"),
    ("Python","MutableDefault","def push(val, stack=[]):\n    stack.append(val)\n    return stack"),
    ("Python","MutableDefault","def record(score, scores=[]):\n    scores.append(score)\n    return sorted(scores)"),
    ("Python","MutableDefault","def enqueue(item, queue=[]):\n    queue.append(item)\n    return queue"),
    ("Python","MutableDefault","def merge(new_data, existing={}):\n    existing.update(new_data)\n    return existing"),
    ("Python","MutableDefault","def build_path(part, parts=[]):\n    parts.append(part)\n    return '/'.join(parts)"),
    ("Python","MutableDefault","def add_child(child, children=[]):\n    children.append(child)\n    return children"),
    ("Python","MutableDefault","def accumulate(n, total=[0]):\n    total[0] += n\n    return total[0]"),
    ("Python","MutableDefault","def configure(key, val, config={}):\n    config[key] = val\n    return config"),
    ("Python","MutableDefault","def batch(item, batch_size=10, batch=[]):\n    batch.append(item)\n    if len(batch) >= batch_size:\n        return batch\n    return []"),
    ("Python","MutableDefault","def index(word, positions=[]):\n    positions.append(word)\n    return positions"),
    ("Python","MutableDefault","def save(record, records=[]):\n    records.append(record)\n    return len(records)"),
    ("Python","MutableDefault","def chain(val, chain=[]):\n    chain.append(val)\n    return chain"),
]
NEW_SAMPLES.extend(MUTABLE)

# =============================================================================
# LineTooLong (+100 needed)
# =============================================================================
LINETOOLONG = [
    ("Python","LineTooLong","result = some_very_long_function_name(argument_one, argument_two, argument_three, argument_four, argument_five, argument_six)"),
    ("Python","LineTooLong","if user.is_authenticated and user.has_permission('admin') and user.account.is_active and not user.account.is_suspended and user.profile.verified:"),
    ("Python","LineTooLong","data = {'key1': value1, 'key2': value2, 'key3': value3, 'key4': value4, 'key5': value5, 'key6': value6, 'key7': value7}"),
    ("Python","LineTooLong","response = requests.post('https://api.example.com/endpoint', headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}, json=payload)"),
    ("Python","LineTooLong","filtered_data = [item for item in all_items if item.status == 'active' and item.category in allowed_categories and item.price < maximum_price]"),
    ("Python","LineTooLong","logging.info(f'Processing request from {request.remote_addr} for user {user.id} ({user.email}) at {datetime.datetime.now().isoformat()}')"),
    ("Python","LineTooLong","sql_query = \"SELECT u.id, u.name, u.email, o.order_id, o.total FROM users u JOIN orders o ON u.id = o.user_id WHERE u.active = 1 ORDER BY o.created_at DESC\""),
    ("Python","LineTooLong","assert result == expected_value, f'Test failed: expected {expected_value} but got {result} for input {test_input} with parameters {params}'"),
    ("Python","LineTooLong","raise ValueError(f'Invalid configuration: parameter {param_name} has value {param_value} which is outside the allowed range [{min_value}, {max_value}]')"),
    ("Python","LineTooLong","combined_result = first_transformation(second_transformation(third_transformation(fourth_transformation(original_data, param1), param2), param3), param4)"),
    # Java
    ("Java","LineTooLong","public class Main {\n    public static void main(String[] args) {\n        String result = someVeryLongMethodName(argumentOne, argumentTwo, argumentThree, argumentFour, argumentFive, argumentSix);\n    }\n}"),
    ("Java","LineTooLong","public class Main {\n    public static boolean checkCondition(User user, Config config, Database db, Logger logger, Validator validator, AuthService auth) {\n        return user.isActive() && config.isEnabled() && auth.isAuthorized(user);\n    }\n}"),
    ("Java","LineTooLong","public class Main {\n    private static final String VERY_LONG_CONSTANT_NAME = \"This is a very long string constant that exceeds the recommended line length limit of 80 or 120 characters\";\n}"),
    # C
    ("C","LineTooLong","#include <stdio.h>\nint main() {\n    printf(\"This is a very long message that exceeds the recommended line length: value1=%d, value2=%d, value3=%d, value4=%d\\n\", v1, v2, v3, v4);\n    return 0;\n}"),
    # C++
    ("C++","LineTooLong","#include <iostream>\nusing namespace std;\nint main() {\n    cout << \"This is a very long output message that exceeds the recommended line length limit for code readability: \" << value1 << \" and \" << value2 << endl;\n    return 0;\n}"),
]
NEW_SAMPLES.extend(LINETOOLONG)

# =============================================================================
# MissingImport (+98 needed)
# =============================================================================
MISSINGIMPORT = [
    ("Python","MissingImport","df = pd.DataFrame({'a': [1,2,3]})\nprint(df)"),
    ("Python","MissingImport","arr = np.array([1,2,3,4,5])\nprint(arr.mean())"),
    ("Python","MissingImport","plt.plot([1,2,3], [4,5,6])\nplt.show()"),
    ("Python","MissingImport","result = math.factorial(10)\nprint(result)"),
    ("Python","MissingImport","path = os.path.join('home', 'user', 'docs')\nprint(path)"),
    ("Python","MissingImport","response = requests.get('https://api.example.com')\nprint(response.json())"),
    ("Python","MissingImport","tree = ET.parse('data.xml')\nroot = tree.getroot()"),
    ("Python","MissingImport","conn = sqlite3.connect('app.db')\ncursor = conn.cursor()"),
    ("Python","MissingImport","data = json.loads('{\"key\": \"value\"}')\nprint(data)"),
    ("Python","MissingImport","t = threading.Thread(target=worker)\nt.start()"),
    ("Python","MissingImport","soup = BeautifulSoup(html, 'html.parser')\nprint(soup.title)"),
    ("Python","MissingImport","now = datetime.datetime.now()\nprint(now)"),
    ("Python","MissingImport","pattern = re.compile(r'\\d+')\nmatches = pattern.findall(text)"),
    ("Python","MissingImport","path = Path('/home/user/docs')\nprint(path.exists())"),
    ("Python","MissingImport","counter = Counter(words)\nprint(counter.most_common(10))"),
    ("Python","MissingImport","model = RandomForestClassifier()\nmodel.fit(X_train, y_train)"),
    ("Python","MissingImport","img = cv2.imread('image.jpg')\ncv2.imshow('window', img)"),
    ("Python","MissingImport","with zipfile.ZipFile('archive.zip') as z:\n    z.extractall('output')"),
    ("Python","MissingImport","config = configparser.ConfigParser()\nconfig.read('app.ini')"),
    ("Python","MissingImport","ftp = ftplib.FTP('ftp.example.com')\nftp.login('user', 'pass')"),
]
NEW_SAMPLES.extend(MISSINGIMPORT)

# =============================================================================
# WildcardImport (+97 needed)
# =============================================================================
WILDCARD = [
    ("Python","WildcardImport","from math import *\nresult = sqrt(16)"),
    ("Python","WildcardImport","from os import *\nfiles = listdir('.')"),
    ("Python","WildcardImport","from tkinter import *\nroot = Tk()"),
    ("Python","WildcardImport","from numpy import *\narr = array([1,2,3])"),
    ("Python","WildcardImport","from pandas import *\ndf = DataFrame({'a': [1,2,3]})"),
    ("Python","WildcardImport","from sys import *\nprint(argv)"),
    ("Python","WildcardImport","from datetime import *\nnow = datetime.now()"),
    ("Python","WildcardImport","from random import *\nx = randint(1, 100)"),
    ("Python","WildcardImport","from string import *\nprint(ascii_letters)"),
    ("Python","WildcardImport","from re import *\npattern = compile(r'\\d+')"),
    ("Python","WildcardImport","from collections import *\nc = Counter([1,1,2,3])"),
    ("Python","WildcardImport","from itertools import *\nresult = list(chain([1,2],[3,4]))"),
    ("Python","WildcardImport","from functools import *\nf = partial(int, base=16)"),
    ("Python","WildcardImport","from pathlib import *\np = Path('.')"),
    ("Python","WildcardImport","from json import *\ndata = loads('{\"a\":1}')"),
    ("Python","WildcardImport","from csv import *\nreader = reader(open('data.csv'))"),
    ("Python","WildcardImport","from shutil import *\ncopy('src.txt', 'dst.txt')"),
    ("Python","WildcardImport","from hashlib import *\nh = md5(b'hello')"),
    ("Python","WildcardImport","from base64 import *\nencoded = b64encode(b'hello')"),
    ("Python","WildcardImport","from urllib.parse import *\nencoded = urlencode({'key': 'value'})"),
]
NEW_SAMPLES.extend(WILDCARD)

# =============================================================================
# IndentationError (+96 needed)
# =============================================================================
INDENTATION = [
    ("Python","IndentationError","def greet(name):\nprint(f'Hello {name}')"),
    ("Python","IndentationError","class Animal:\ndef speak(self):\n    print('...')"),
    ("Python","IndentationError","for i in range(5):\nprint(i)"),
    ("Python","IndentationError","while True:\nbreak"),
    ("Python","IndentationError","if x > 0:\nprint('positive')"),
    ("Python","IndentationError","try:\nx = int('abc')\nexcept:\n    pass"),
    ("Python","IndentationError","def calculate(a, b):\n    if a > b:\n    return a\n    return b"),
    ("Python","IndentationError","for item in items:\n    if item > 0:\n    process(item)"),
    ("Python","IndentationError","class Config:\n    DEBUG = True\n    def load(self):\n    pass"),
    ("Python","IndentationError","def outer():\n    def inner():\n    return 1\n    return inner"),
    ("Python","IndentationError","with open('file.txt') as f:\ndata = f.read()"),
    ("Python","IndentationError","if condition:\n    do_something()\nelse:\ndo_other()"),
    ("Python","IndentationError","def process(data):\n        result = transform(data)\n    return result"),
    ("Python","IndentationError","for i in range(10):\n    for j in range(10):\n    print(i, j)"),
    ("Python","IndentationError","try:\n    x = 1/0\nexcept ZeroDivisionError:\nprint('error')"),
    ("Python","IndentationError","class Dog:\n    def __init__(self, name):\n        self.name = name\n    def bark(self):\n    print('Woof')"),
    ("Python","IndentationError","def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n  return 0"),
    ("Python","IndentationError","while x < 10:\n    x += 1\n  print(x)"),
    ("Python","IndentationError","if a > b:\n    result = a\n  else:\n    result = b"),
    ("Python","IndentationError","for num in numbers:\n    if num % 2 == 0:\n        even.append(num)\n  else:\n        odd.append(num)"),
]
NEW_SAMPLES.extend(INDENTATION)

# =============================================================================
# ImportError (+96 needed)
# =============================================================================
IMPORTERROR = [
    ("Python","ImportError","import nonexistent_module\nresult = nonexistent_module.process()"),
    ("Python","ImportError","from fake_library import FakeClass\nobj = FakeClass()"),
    ("Python","ImportError","import invalid_package\nprint(invalid_package.VERSION)"),
    ("Python","ImportError","from missing_module import helper\nresult = helper.run()"),
    ("Python","ImportError","import typo_numpy as np\narr = np.array([1,2,3])"),
    ("Python","ImportError","from no_such_package.utils import load\ndata = load('file.txt')"),
    ("Python","ImportError","import uninstalled_lib\nmodel = uninstalled_lib.Model()"),
    ("Python","ImportError","from misspelled_os import path\nprint(path.exists('file.txt'))"),
    ("Python","ImportError","import not_a_real_module\nconfig = not_a_real_module.Config()"),
    ("Python","ImportError","from broken_import import DataProcessor\nproc = DataProcessor()"),
    ("Python","ImportError","import misng_lib\nresult = misng_lib.compute(10)"),
    ("Python","ImportError","from bad_package.core import Engine\ne = Engine()"),
    ("Python","ImportError","import absnt_module as am\npm.process()"),
    ("Python","ImportError","from nonexist_utils import transform\ndata = transform(raw)"),
    ("Python","ImportError","import python_does_not_have_this\nresult = python_does_not_have_this.run()"),
    ("Python","ImportError","from my_missing_module import BaseClass\nclass Child(BaseClass):\n    pass"),
    ("Python","ImportError","import unavailable_package\nconn = unavailable_package.connect('localhost')"),
    ("Python","ImportError","from wrongpackage import right_function\nright_function()"),
    ("Python","ImportError","import numppy\narr = numppy.zeros(10)"),
    ("Python","ImportError","from paandas import DataFrame\ndf = DataFrame()"),
]
NEW_SAMPLES.extend(IMPORTERROR)

# =============================================================================
# InfiniteLoop (+95 needed)
# =============================================================================
INFINITE = [
    ("Python","InfiniteLoop","while True:\n    print('forever')"),
    ("Python","InfiniteLoop","while 1:\n    process()"),
    ("Python","InfiniteLoop","x = 0\nwhile x < 10:\n    print(x)"),
    ("Python","InfiniteLoop","i = 0\nwhile i < 100:\n    print(i)\n    i = i"),
    ("Python","InfiniteLoop","count = 0\nwhile count != 10:\n    count += 2"),
    ("Python","InfiniteLoop","n = 1\nwhile n > 0:\n    n += 1"),
    ("Python","InfiniteLoop","data = get_data()\nwhile data:\n    process(data)"),
    ("Python","InfiniteLoop","running = True\nwhile running:\n    update()"),
    ("Python","InfiniteLoop","index = 0\nwhile index < len(items):\n    print(items[index])"),
    ("Python","InfiniteLoop","x = 10\nwhile x > 0:\n    x += 1"),
    ("Python","InfiniteLoop","retry = True\nwhile retry:\n    result = attempt()"),
    ("Python","InfiniteLoop","queue = [1,2,3]\nwhile queue:\n    item = queue[0]"),
    # Java
    ("Java","InfiniteLoop","public class Main {\n    public static void main(String[] args) {\n        while (true) {\n            System.out.println(\"forever\");\n        }\n    }\n}"),
    ("Java","InfiniteLoop","public class Main {\n    public static void main(String[] args) {\n        int x = 0;\n        while (x < 10) {\n            System.out.println(x);\n        }\n    }\n}"),
    ("Java","InfiniteLoop","public class Main {\n    public static void main(String[] args) {\n        for (;;) {\n            process();\n        }\n    }\n}"),
    ("Java","InfiniteLoop","public class Main {\n    public static void main(String[] args) {\n        int i = 0;\n        while (i < 100) {\n            System.out.println(i);\n            i = i;\n        }\n    }\n}"),
    # C
    ("C","InfiniteLoop","#include <stdio.h>\nint main() {\n    while (1) {\n        printf(\"forever\\n\");\n    }\n    return 0;\n}"),
    ("C","InfiniteLoop","#include <stdio.h>\nint main() {\n    int x = 0;\n    while (x < 10) {\n        printf(\"%d\\n\", x);\n    }\n    return 0;\n}"),
    ("C","InfiniteLoop","#include <stdio.h>\nint main() {\n    for (;;) {\n        process();\n    }\n    return 0;\n}"),
    # C++
    ("C++","InfiniteLoop","#include <iostream>\nusing namespace std;\nint main() {\n    while (true) {\n        cout << \"forever\" << endl;\n    }\n    return 0;\n}"),
    ("C++","InfiniteLoop","#include <iostream>\nusing namespace std;\nint main() {\n    int x = 0;\n    while (x < 10) {\n        cout << x << endl;\n    }\n    return 0;\n}"),
]
NEW_SAMPLES.extend(INFINITE)

# =============================================================================
# UnmatchedBracket (+95 needed)
# =============================================================================
UNMATCHED = [
    ("Python","UnmatchedBracket","print('Hello'\nprint('World')"),
    ("Python","UnmatchedBracket","result = (a + b * (c - d)\nprint(result)"),
    ("Python","UnmatchedBracket","items = [1, 2, 3, 4\nprint(items)"),
    ("Python","UnmatchedBracket","data = {'key': 'value'\nprocess(data)"),
    ("Python","UnmatchedBracket","def calculate(x, y:\n    return x + y"),
    ("Python","UnmatchedBracket","if (x > 0 and y < 10:\n    process()"),
    ("Python","UnmatchedBracket","result = func(a, (b + c, d)\nprint(result)"),
    ("Python","UnmatchedBracket","matrix = [[1, 2, 3], [4, 5, 6]\nprint(matrix)"),
    ("Python","UnmatchedBracket","config = {\"debug\": True, \"log\": [1, 2, 3}\nprint(config)"),
    ("Python","UnmatchedBracket","values = tuple([x for x in range(10))\nprint(values)"),
    ("Python","UnmatchedBracket","nested = ((1 + 2) * (3 + 4)\nprint(nested)"),
    ("Python","UnmatchedBracket","call = outer(inner(x, y), z\nprint(call)"),
    # Java
    ("Java","UnmatchedBracket","public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello\";\n    }\n}"),
    ("Java","UnmatchedBracket","public class Main {\n    public static int add(int a, int b {\n        return a + b;\n    }\n}"),
    ("Java","UnmatchedBracket","public class Main {\n    public static void main(String[] args) {\n        int[] arr = {1, 2, 3;\n        System.out.println(arr[0]);\n    }\n}"),
    # C
    ("C","UnmatchedBracket","#include <stdio.h>\nint main() {\n    printf(\"Hello\";\n    return 0;\n}"),
    ("C","UnmatchedBracket","#include <stdio.h>\nint add(int a, int b {\n    return a + b;\n}"),
    ("C","UnmatchedBracket","#include <stdio.h>\nint main() {\n    int arr[] = {1, 2, 3;\n    printf(\"%d\\n\", arr[0]);\n    return 0;\n}"),
    # C++
    ("C++","UnmatchedBracket","#include <iostream>\nusing namespace std;\nint main() {\n    cout << \"Hello\" << endl;\n    return 0;\n"),
    ("C++","UnmatchedBracket","#include <iostream>\nusing namespace std;\nint add(int a, int b {\n    return a + b;\n}"),
]
NEW_SAMPLES.extend(UNMATCHED)

# =============================================================================
# MissingInclude (+89 needed)
# =============================================================================
MISSINGINCLUDE = [
    ("C","MissingInclude","int main() {\n    printf(\"Hello\\n\");\n    return 0;\n}"),
    ("C","MissingInclude","int main() {\n    char *str = malloc(100);\n    free(str);\n    return 0;\n}"),
    ("C","MissingInclude","int main() {\n    char s[] = \"hello\";\n    int len = strlen(s);\n    return 0;\n}"),
    ("C","MissingInclude","int main() {\n    double r = sqrt(16.0);\n    printf(\"%f\\n\", r);\n    return 0;\n}"),
    ("C","MissingInclude","int main() {\n    int x = abs(-5);\n    printf(\"%d\\n\", x);\n    return 0;\n}"),
    ("C","MissingInclude","int main() {\n    srand(42);\n    int r = rand();\n    return 0;\n}"),
    ("C","MissingInclude","int main() {\n    time_t t = time(NULL);\n    printf(\"%ld\\n\", t);\n    return 0;\n}"),
    ("C","MissingInclude","void process() {\n    FILE *f = fopen(\"data.txt\", \"r\");\n    fclose(f);\n}"),
    ("C","MissingInclude","int main() {\n    char buf[100];\n    sprintf(buf, \"%d\", 42);\n    return 0;\n}"),
    ("C","MissingInclude","int main() {\n    int *p = calloc(10, sizeof(int));\n    free(p);\n    return 0;\n}"),
    ("C++","MissingInclude","int main() {\n    cout << \"Hello\" << endl;\n    return 0;\n}"),
    ("C++","MissingInclude","int main() {\n    vector<int> v = {1,2,3};\n    return 0;\n}"),
    ("C++","MissingInclude","int main() {\n    string s = \"hello\";\n    cout << s << endl;\n    return 0;\n}"),
    ("C++","MissingInclude","int main() {\n    map<string,int> m;\n    m[\"a\"] = 1;\n    return 0;\n}"),
    ("C++","MissingInclude","int main() {\n    queue<int> q;\n    q.push(1);\n    return 0;\n}"),
    ("C++","MissingInclude","int main() {\n    sort(v.begin(), v.end());\n    return 0;\n}"),
    ("C++","MissingInclude","int main() {\n    auto ptr = make_shared<int>(42);\n    return 0;\n}"),
    ("C++","MissingInclude","int main() {\n    stack<int> s;\n    s.push(1);\n    return 0;\n}"),
]
NEW_SAMPLES.extend(MISSINGINCLUDE)

# =============================================================================
# InvalidAssignment (+30 needed)
# =============================================================================
INVALIDASSIGN = [
    ("Python","InvalidAssignment","1 = x"),
    ("Python","InvalidAssignment","'hello' = name"),
    ("Python","InvalidAssignment","True = flag"),
    ("Python","InvalidAssignment","None = result"),
    ("Python","InvalidAssignment","42 = count"),
    ("Python","InvalidAssignment","3.14 = pi"),
    ("Python","InvalidAssignment","x + 1 = result"),
    ("Python","InvalidAssignment","len(items) = size"),
    ("Python","InvalidAssignment","a + b = sum_val"),
    ("Python","InvalidAssignment","[1,2,3] = numbers"),
    ("Java","InvalidAssignment","public class Main {\n    public static void main(String[] args) {\n        final int MAX = 100;\n        MAX = 200;\n    }\n}"),
    ("Java","InvalidAssignment","public class Main {\n    public static void main(String[] args) {\n        42 = x;\n    }\n}"),
    ("C","InvalidAssignment","int main() {\n    const int MAX = 100;\n    MAX = 200;\n    return 0;\n}"),
    ("C++","InvalidAssignment","int main() {\n    const int MAX = 100;\n    MAX = 200;\n    return 0;\n}"),
]
NEW_SAMPLES.extend(INVALIDASSIGN)


# ─────────────────────────────────────────────────────────────────────────────
# Main script
# ─────────────────────────────────────────────────────────────────────────────

DATASET_PATHS = [
    "dataset/merged/all_errors.csv",
    "all_errors.csv",
]

def find_dataset():
    for path in DATASET_PATHS:
        if os.path.exists(path):
            return path
    return None

def main():
    parser = argparse.ArgumentParser(description="Augment the error detection dataset")
    parser.add_argument('--output', type=str, default=None,
                        help='Output CSV path (default: auto-named v2 alongside original)')
    parser.add_argument('--preview', action='store_true',
                        help='Preview counts without writing')
    args = parser.parse_args()

    # Load existing dataset
    dataset_path = find_dataset()
    if not dataset_path:
        print("❌ Dataset not found. Tried:", DATASET_PATHS)
        return

    existing = []
    with open(dataset_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            existing.append(row)

    existing_counts = Counter(r['error_type'] for r in existing)
    new_counts = Counter(t for _, t, _ in NEW_SAMPLES)

    print(f"\n{'='*60}")
    print(f"  Dataset Augmentation Plan")
    print(f"{'='*60}")
    print(f"\n  Original dataset : {dataset_path}")
    print(f"  Original samples : {len(existing)}")
    print(f"  New samples      : {len(NEW_SAMPLES)}")
    print(f"  Total after merge: {len(existing) + len(NEW_SAMPLES)}")

    print(f"\n  {'Error Type':<25} {'Before':>7} {'Added':>7} {'After':>7}")
    print(f"  {'-'*25} {'-'*7} {'-'*7} {'-'*7}")
    all_types = sorted(set(list(existing_counts.keys()) + list(new_counts.keys())))
    for t in all_types:
        before = existing_counts.get(t, 0)
        added  = new_counts.get(t, 0)
        after  = before + added
        flag = " ✅" if after >= 200 else " ⚠️ "
        print(f"  {t:<25} {before:>7} {added:>7} {after:>7}{flag}")

    if args.preview:
        print(f"\n  (Preview only — no file written)")
        return

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        base = os.path.dirname(dataset_path)
        output_path = os.path.join(base, "all_errors_v3.csv") if base else "all_errors_v3.csv"

    # Build new rows
    new_rows = []
    for lang, error_type, code in NEW_SAMPLES:
        new_rows.append({
            'language': lang,
            'error_type': error_type,
            'buggy_code': code,
            'fixed_code': '',
            'line_no': ''
        })

    # Write merged dataset
    all_rows = existing + new_rows
    random.seed(42)
    random.shuffle(all_rows)

    output_fieldnames = fieldnames or ['language', 'error_type', 'buggy_code', 'fixed_code', 'line_no']
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n  ✅ Written to: {output_path}")
    print(f"  Total samples: {len(all_rows)}")
    print(f"\n  Next steps:")
    print(f"  1. Review: python augment_dataset.py --preview")
    print(f"  2. Retrain: python scripts/optimize_model.py")
    print(f"     (update MODEL_DIR path in optimize_model.py if needed)")
    print(f"  3. Re-run accuracy test: python test_accuracy.py")
    print()

if __name__ == '__main__':
    main()
