#!/usr/bin/env python3
"""
NoError Sample Generator
Generates valid code samples for training the model to recognize correct code
"""

import csv
import random

# Python NoError Samples
PYTHON_NOERROR = [
    # Basic assignments
    "x = 10",
    "y = 20",
    "name = 'Alice'",
    'message = "Hello World"',
    "result = 42",
    "pi = 3.14159",
    "is_valid = True",
    "items = None",
    
    # Arithmetic
    "total = a + b",
    "product = x * y",
    "quotient = x / y",
    "remainder = x % y",
    "power = x ** 2",
    "result = (a + b) * c",
    "average = sum(numbers) / len(numbers)",
    
    # String operations
    "full_name = first + ' ' + last",
    "greeting = f'Hello {name}'",
    "text = 'line1\\nline2\\nline3'",
    "upper = text.upper()",
    "length = len(message)",
    
    # Lists
    "numbers = [1, 2, 3, 4, 5]",
    "names = ['Alice', 'Bob', 'Charlie']",
    "mixed = [1, 'two', 3.0, True]",
    "empty = []",
    "matrix = [[1, 2], [3, 4]]",
    "squares = [x**2 for x in range(10)]",
    
    # Dictionaries
    "person = {'name': 'Alice', 'age': 30}",
    "scores = {'math': 95, 'english': 87}",
    "empty_dict = {}",
    "data = dict(a=1, b=2, c=3)",
    
    # Sets and Tuples
    "unique = {1, 2, 3, 4, 5}",
    "coordinates = (10, 20)",
    "triple = (1, 2, 3)",
    
    # Simple functions
    "def hello():\\n    print('Hello')",
    "def add(a, b):\\n    return a + b",
    "def greet(name):\\n    return f'Hello {name}'",
    "def square(x):\\n    return x * x",
    "def is_positive(n):\\n    return n > 0",
    
    # Control flow
    "if x > 0:\\n    print('positive')",
    "if x > 0:\\n    print('pos')\\nelse:\\n    print('neg')",
    "for i in range(10):\\n    print(i)",
    "for item in items:\\n    process(item)",
    "while x < 10:\\n    x += 1",
    "for i, val in enumerate(data):\\n    print(i, val)",
    
    # Classes
    "class Dog:\\n    pass",
    "class Cat:\\n    def meow(self):\\n        print('Meow')",
    "class Person:\\n    def __init__(self, name):\\n        self.name = name",
    
    # Imports
    "import os",
    "import sys",
    "import math",
    "from os import path",
    "from math import pi, sqrt",
    "import numpy as np",
    
    # With statements
    "with open('file.txt', 'r') as f:\\n    data = f.read()",
    
    # Try-except
    "try:\\n    x = int(input())\\nexcept ValueError:\\n    x = 0",
    
    # Lambda
    "square = lambda x: x**2",
    "add = lambda a, b: a + b",
    
    # Type hints
    "def add(a: int, b: int) -> int:\\n    return a + b",
    
    # Complete simple programs
    "def main():\\n    print('Hello, World!')\\n\\nif __name__ == '__main__':\\n    main()",
    "import os\\n\\ndef get_path():\\n    return os.getcwd()\\n\\nprint(get_path())",
]

# Java NoError Samples
JAVA_NOERROR = [
    # Hello World
    'public class Main {\\n    public static void main(String[] args) {\\n        System.out.println("Hello");\\n    }\\n}',
    
    # Variable declarations
    'public class Main {\\n    public static void main(String[] args) {\\n        int x = 10;\\n        int y = 20;\\n        System.out.println(x + y);\\n    }\\n}',
    
    'public class Main {\\n    public static void main(String[] args) {\\n        String name = "Alice";\\n        System.out.println("Hello " + name);\\n    }\\n}',
    
    # Methods
    'public class Main {\\n    public static int add(int a, int b) {\\n        return a + b;\\n    }\\n    public static void main(String[] args) {\\n        System.out.println(add(5, 3));\\n    }\\n}',
    
    # Loops
    'public class Main {\\n    public static void main(String[] args) {\\n        for (int i = 0; i < 10; i++) {\\n            System.out.println(i);\\n        }\\n    }\\n}',
    
    'public class Main {\\n    public static void main(String[] args) {\\n        int i = 0;\\n        while (i < 5) {\\n            System.out.println(i);\\n            i++;\\n        }\\n    }\\n}',
    
    # If statements
    'public class Main {\\n    public static void main(String[] args) {\\n        int x = 10;\\n        if (x > 5) {\\n            System.out.println("Greater");\\n        }\\n    }\\n}',
    
    # Arrays
    'public class Main {\\n    public static void main(String[] args) {\\n        int[] numbers = {1, 2, 3, 4, 5};\\n        System.out.println(numbers[0]);\\n    }\\n}',
    
    # Classes
    'class Dog {\\n    String name;\\n    void bark() {\\n        System.out.println("Woof");\\n    }\\n}',
]

# C NoError Samples
C_NOERROR = [
    # Hello World
    '#include <stdio.h>\\nint main() {\\n    printf("Hello, World!\\\\n");\\n    return 0;\\n}',
    
    # Variables
    '#include <stdio.h>\\nint main() {\\n    int x = 10;\\n    int y = 20;\\n    printf("%d\\\\n", x + y);\\n    return 0;\\n}',
    
    # Functions
    '#include <stdio.h>\\nint add(int a, int b) {\\n    return a + b;\\n}\\nint main() {\\n    printf("%d\\\\n", add(5, 3));\\n    return 0;\\n}',
    
    # Loops
    '#include <stdio.h>\\nint main() {\\n    for (int i = 0; i < 10; i++) {\\n        printf("%d\\\\n", i);\\n    }\\n    return 0;\\n}',
    
    # If statements
    '#include <stdio.h>\\nint main() {\\n    int x = 10;\\n    if (x > 5) {\\n        printf("Greater\\\\n");\\n    }\\n    return 0;\\n}',
    
    # Arrays
    '#include <stdio.h>\\nint main() {\\n    int arr[5] = {1, 2, 3, 4, 5};\\n    printf("%d\\\\n", arr[0]);\\n    return 0;\\n}',
    
    # Pointers
    '#include <stdio.h>\\nint main() {\\n    int x = 42;\\n    int *p = &x;\\n    printf("%d\\\\n", *p);\\n    return 0;\\n}',
]

# C++ NoError Samples
CPP_NOERROR = [
    # Hello World
    '#include <iostream>\\nusing namespace std;\\nint main() {\\n    cout << "Hello, World!" << endl;\\n    return 0;\\n}',
    
    # Variables
    '#include <iostream>\\nusing namespace std;\\nint main() {\\n    int x = 10;\\n    int y = 20;\\n    cout << x + y << endl;\\n    return 0;\\n}',
    
    # Functions
    '#include <iostream>\\nusing namespace std;\\nint add(int a, int b) {\\n    return a + b;\\n}\\nint main() {\\n    cout << add(5, 3) << endl;\\n    return 0;\\n}',
    
    # Loops
    '#include <iostream>\\nusing namespace std;\\nint main() {\\n    for (int i = 0; i < 10; i++) {\\n        cout << i << endl;\\n    }\\n    return 0;\\n}',
    
    # Classes
    '#include <iostream>\\nusing namespace std;\\nclass Dog {\\npublic:\\n    void bark() {\\n        cout << "Woof!" << endl;\\n    }\\n};\\nint main() {\\n    Dog d;\\n    d.bark();\\n    return 0;\\n}',
    
    # Vectors
    '#include <iostream>\\n#include <vector>\\nusing namespace std;\\nint main() {\\n    vector<int> v = {1, 2, 3};\\n    cout << v[0] << endl;\\n    return 0;\\n}',
    
    # Strings
    '#include <iostream>\\n#include <string>\\nusing namespace std;\\nint main() {\\n    string name = "Alice";\\n    cout << "Hello " << name << endl;\\n    return 0;\\n}',
]

def generate_noerror_samples(output_file='noerror_samples.csv'):
    """Generate CSV file with NoError samples"""
    
    samples = []
    
    # Add Python samples
    for code in PYTHON_NOERROR:
        samples.append({
            'buggy_code': code,
            'error_type': 'NoError',
            'language': 'Python'
        })
    
    # Add Java samples
    for code in JAVA_NOERROR:
        samples.append({
            'buggy_code': code,
            'error_type': 'NoError',
            'language': 'Java'
        })
    
    # Add C samples
    for code in C_NOERROR:
        samples.append({
            'buggy_code': code,
            'error_type': 'NoError',
            'language': 'C'
        })
    
    # Add C++ samples
    for code in CPP_NOERROR:
        samples.append({
            'buggy_code': code,
            'error_type': 'NoError',
            'language': 'C++'
        })
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['buggy_code', 'error_type', 'language'])
        writer.writeheader()
        writer.writerows(samples)
    
    # Print summary
    print(f"\\n{'='*60}")
    print(f"NoError Sample Generation Complete")
    print(f"{'='*60}")
    print(f"\\nTotal samples: {len(samples)}")
    print(f"  Python : {len(PYTHON_NOERROR)}")
    print(f"  Java   : {len(JAVA_NOERROR)}")
    print(f"  C      : {len(C_NOERROR)}")
    print(f"  C++    : {len(CPP_NOERROR)}")
    print(f"\\nOutput file: {output_file}")
    print(f"\\nNext steps:")
    print(f"  1. Review the generated samples")
    print(f"  2. Add to dataset: cp {output_file} dataset/active/")
    print(f"  3. Merge datasets: cat dataset/active/*.csv > dataset/merged/all_errors_v2.csv")
    print(f"  4. Retrain model: python scripts/optimize_model.py")
    print()

if __name__ == '__main__':
    generate_noerror_samples()