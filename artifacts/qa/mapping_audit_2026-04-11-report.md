# OmniSyntax Mapping Audit Report (2026-04-11)

## 1) Coverage Table

- Total cases: **240**
- Pass / Fail: **194 / 46**
- False Positives: **0**
- False Negatives: **29**
- Misclassified (wrong non-NoError): **17**

| Language | Error Type | Status | Positives (3) | Negative (NoError) |
|---|---|---|---:|---:|
| Python | DanglingPointer | Missing | 0/3 | 1/1 |
| Python | DivisionByZero | Covered | 3/3 | 1/1 |
| Python | DuplicateDefinition | Missing | 0/3 | 1/1 |
| Python | ImportError | Weak | 1/3 | 1/1 |
| Python | IndentationError | Covered | 3/3 | 1/1 |
| Python | InfiniteLoop | Weak | 2/3 | 1/1 |
| Python | InvalidAssignment | Weak | 2/3 | 1/1 |
| Python | LineTooLong | Missing | 0/3 | 1/1 |
| Python | MissingDelimiter | Covered | 3/3 | 1/1 |
| Python | MissingImport | Missing | 0/3 | 1/1 |
| Python | MutableDefault | Covered | 3/3 | 1/1 |
| Python | NameError | Covered | 3/3 | 1/1 |
| Python | TypeMismatch | Missing | 0/3 | 1/1 |
| Python | UnclosedString | Covered | 3/3 | 1/1 |
| Python | UndeclaredIdentifier | Missing | 0/3 | 1/1 |
| Python | UnmatchedBracket | Covered | 3/3 | 1/1 |
| Python | UnreachableCode | Covered | 3/3 | 1/1 |
| Python | UnusedVariable | Missing | 0/3 | 1/1 |
| Python | WildcardImport | Covered | 3/3 | 1/1 |
| Java | DivisionByZero | Covered | 3/3 | 1/1 |
| Java | DuplicateDefinition | Weak | 2/3 | 1/1 |
| Java | ImportError | Missing | 0/3 | 1/1 |
| Java | InfiniteLoop | Covered | 3/3 | 1/1 |
| Java | InvalidAssignment | Missing | 0/3 | 1/1 |
| Java | LineTooLong | Missing | 0/3 | 1/1 |
| Java | MissingDelimiter | Covered | 3/3 | 1/1 |
| Java | MissingImport | Covered | 3/3 | 1/1 |
| Java | TypeMismatch | Covered | 3/3 | 1/1 |
| Java | UnclosedString | Covered | 3/3 | 1/1 |
| Java | UndeclaredIdentifier | Covered | 3/3 | 1/1 |
| Java | UnmatchedBracket | Covered | 3/3 | 1/1 |
| Java | UnreachableCode | Weak | 2/3 | 1/1 |
| Java | UnusedVariable | Missing | 0/3 | 1/1 |
| C | DivisionByZero | Covered | 3/3 | 1/1 |
| C | InfiniteLoop | Covered | 3/3 | 1/1 |
| C | MissingDelimiter | Covered | 3/3 | 1/1 |
| C | MissingInclude | Covered | 3/3 | 1/1 |
| C | TypeMismatch | Covered | 3/3 | 1/1 |
| C | UnclosedString | Covered | 3/3 | 1/1 |
| C | UndeclaredIdentifier | Covered | 3/3 | 1/1 |
| C | UnmatchedBracket | Covered | 3/3 | 1/1 |
| C | UnreachableCode | Weak | 1/3 | 1/1 |
| C++ | DanglingPointer | Covered | 3/3 | 1/1 |
| C++ | DivisionByZero | Covered | 3/3 | 1/1 |
| C++ | InfiniteLoop | Covered | 3/3 | 1/1 |
| C++ | MissingDelimiter | Covered | 3/3 | 1/1 |
| C++ | MissingInclude | Covered | 3/3 | 1/1 |
| C++ | TypeMismatch | Covered | 3/3 | 1/1 |
| C++ | UnclosedString | Covered | 3/3 | 1/1 |
| C++ | UndeclaredIdentifier | Weak | 2/3 | 1/1 |
| C++ | UnmatchedBracket | Covered | 3/3 | 1/1 |
| C++ | UnreachableCode | Weak | 1/3 | 1/1 |
| JavaScript | DivisionByZero | Covered | 3/3 | 1/1 |
| JavaScript | DuplicateDefinition | Covered | 3/3 | 1/1 |
| JavaScript | InfiniteLoop | Covered | 3/3 | 1/1 |
| JavaScript | MissingDelimiter | Covered | 3/3 | 1/1 |
| JavaScript | UnclosedString | Covered | 3/3 | 1/1 |
| JavaScript | UndeclaredIdentifier | Covered | 3/3 | 1/1 |
| JavaScript | UnmatchedBracket | Covered | 3/3 | 1/1 |
| JavaScript | UnreachableCode | Weak | 1/3 | 1/1 |

## 2) Test Case Suite

Matrix format: **Language -> Error Type -> Test Case -> Expected Output -> Actual Output**

### Python

#### DanglingPointer

- Case `Python-DanglingPointer-normal1`: expected `DanglingPointer`, actual `NoError`, status **FAIL**
```
import ctypes

def bad_ptr():
    value = ctypes.c_int(10)
    return ctypes.pointer(value)
```
- Case `Python-DanglingPointer-normal2`: expected `DanglingPointer`, actual `NoError`, status **FAIL**
```
import ctypes

buf = ctypes.c_int(3)
ptr = ctypes.pointer(buf)
print(ptr.contents.value)
```
- Case `Python-DanglingPointer-edge`: expected `DanglingPointer`, actual `ImportError`, status **FAIL**
```
import ctypes

def g():
    local = ctypes.c_int(5)
    p = ctypes.pointer(local)
    return p
```
- Case `Python-DanglingPointer-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### DivisionByZero

- Case `Python-DivisionByZero-normal1`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
```
x = 10 / 0
```
- Case `Python-DivisionByZero-normal2`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
```
rem = 5 % 0
```
- Case `Python-DivisionByZero-edge`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
```
def f():
    return (3 + 2) / 0.0
```
- Case `Python-DivisionByZero-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### DuplicateDefinition

- Case `Python-DuplicateDefinition-normal1`: expected `DuplicateDefinition`, actual `NoError`, status **FAIL**
```
def helper():
    return 1

def helper():
    return 2
```
- Case `Python-DuplicateDefinition-normal2`: expected `DuplicateDefinition`, actual `NoError`, status **FAIL**
```
class A:
    pass

class A:
    pass
```
- Case `Python-DuplicateDefinition-edge`: expected `DuplicateDefinition`, actual `NoError`, status **FAIL**
```
def f():
    return 1

def g():
    return 2

def f():
    return 3
```
- Case `Python-DuplicateDefinition-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### ImportError

- Case `Python-ImportError-normal1`: expected `ImportError`, actual `ImportError`, status **PASS**
```
import this_package_does_not_exist
print('x')
```
- Case `Python-ImportError-normal2`: expected `ImportError`, actual `NoError`, status **FAIL**
```
from ghostlib import parser
```
- Case `Python-ImportError-edge`: expected `ImportError`, actual `NoError`, status **FAIL**
```
import importlib
mod = importlib.import_module('imaginary_pkg_123')
```
- Case `Python-ImportError-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### IndentationError

- Case `Python-IndentationError-normal1`: expected `IndentationError`, actual `IndentationError`, status **PASS**
- Observed rule types: `IndentationError, SyntaxError`
```
def f():
print('x')
```
- Case `Python-IndentationError-normal2`: expected `IndentationError`, actual `IndentationError`, status **PASS**
- Observed rule types: `IndentationError`
```
if True:
    x = 1
      y = 2
```
- Case `Python-IndentationError-edge`: expected `IndentationError`, actual `IndentationError`, status **PASS**
- Observed rule types: `IndentationError`
```
def g():
    if True:
        x = 1
      return x
```
- Case `Python-IndentationError-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### InfiniteLoop

- Case `Python-InfiniteLoop-normal1`: expected `InfiniteLoop`, actual `InfiniteLoop`, status **PASS**
```
while True:
    pass
```
- Case `Python-InfiniteLoop-normal2`: expected `InfiniteLoop`, actual `NoError`, status **FAIL**
```
while 1:
    continue
```
- Case `Python-InfiniteLoop-edge`: expected `InfiniteLoop`, actual `InfiniteLoop`, status **PASS**
```
i = 0
while True:
    i += 1
```
- Case `Python-InfiniteLoop-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### InvalidAssignment

- Case `Python-InvalidAssignment-normal1`: expected `InvalidAssignment`, actual `InvalidAssignment`, status **PASS**
- Observed rule types: `SyntaxError`
```
a + b = 3
```
- Case `Python-InvalidAssignment-normal2`: expected `InvalidAssignment`, actual `InvalidAssignment`, status **PASS**
- Observed rule types: `SyntaxError`
```
1 = x
```
- Case `Python-InvalidAssignment-edge`: expected `InvalidAssignment`, actual `NoError`, status **FAIL**
```
(x, y) = 1
```
- Case `Python-InvalidAssignment-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### LineTooLong

- Case `Python-LineTooLong-normal1`: expected `LineTooLong`, actual `NoError`, status **FAIL**
```
message = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
print(message)
```
- Case `Python-LineTooLong-normal2`: expected `LineTooLong`, actual `NoError`, status **FAIL**
```
url = 'https://example.com/path/path/path/path/path/path/path/path/path/path/path/path/path/path/path/path/path/path/path/path/path/path/path/path/path/'
print(url)
```
- Case `Python-LineTooLong-edge`: expected `LineTooLong`, actual `NoError`, status **FAIL**
```
data = {'text': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'}
print(data)
```
- Case `Python-LineTooLong-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### MissingDelimiter

- Case `Python-MissingDelimiter-normal1`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
def add(a, b)
    return a + b
```
- Case `Python-MissingDelimiter-normal2`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
if True
    x = 1
```
- Case `Python-MissingDelimiter-edge`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
for i in range(3)
    print(i)
```
- Case `Python-MissingDelimiter-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### MissingImport

- Case `Python-MissingImport-normal1`: expected `MissingImport`, actual `NameError`, status **FAIL**
- Observed rule types: `NameError`
```
result = math.sqrt(16)
print(result)
```
- Case `Python-MissingImport-normal2`: expected `MissingImport`, actual `NameError`, status **FAIL**
- Observed rule types: `NameError`
```
today = datetime.datetime.now()
```
- Case `Python-MissingImport-edge`: expected `MissingImport`, actual `NameError`, status **FAIL**
- Observed rule types: `NameError`
```
arr = np.array([1, 2, 3])
```
- Case `Python-MissingImport-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### MutableDefault

- Case `Python-MutableDefault-normal1`: expected `MutableDefault`, actual `MutableDefault`, status **PASS**
- Observed rule types: `MutableDefault`
```
def add_item(item, bucket=[]):
    bucket.append(item)
    return bucket
```
- Case `Python-MutableDefault-normal2`: expected `MutableDefault`, actual `MutableDefault`, status **PASS**
- Observed rule types: `MutableDefault`
```
def merge(k, v, cache={}):
    cache[k] = v
    return cache
```
- Case `Python-MutableDefault-edge`: expected `MutableDefault`, actual `MutableDefault`, status **PASS**
- Observed rule types: `MutableDefault`
```
def tags(x, s=set()):
    s.add(x)
    return s
```
- Case `Python-MutableDefault-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### NameError

- Case `Python-NameError-normal1`: expected `NameError`, actual `NameError`, status **PASS**
- Observed rule types: `NameError`
```
def area(r):
    return pi * r * r
```
- Case `Python-NameError-normal2`: expected `NameError`, actual `NameError`, status **PASS**
- Observed rule types: `NameError`
```
total = price + tax
```
- Case `Python-NameError-edge`: expected `NameError`, actual `NameError`, status **PASS**
- Observed rule types: `NameError`
```
def f():
    if False:
        value = 1
    return value2
```
- Case `Python-NameError-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### TypeMismatch

- Case `Python-TypeMismatch-normal1`: expected `TypeMismatch`, actual `NoError`, status **FAIL**
```
x: int = '42'
print(x)
```
- Case `Python-TypeMismatch-normal2`: expected `TypeMismatch`, actual `NoError`, status **FAIL**
```
def f(v: int) -> int:
    return 'bad'
```
- Case `Python-TypeMismatch-edge`: expected `TypeMismatch`, actual `NoError`, status **FAIL**
```
items: list[int] = ['a']
```
- Case `Python-TypeMismatch-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### UnclosedString

- Case `Python-UnclosedString-normal1`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `UnclosedString`
```
name = "Alice
print(name)
```
- Case `Python-UnclosedString-normal2`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `UnclosedString`
```
msg = 'hello
```
- Case `Python-UnclosedString-edge`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `UnclosedString`
```
query = f"User: {42}
print(query)
```
- Case `Python-UnclosedString-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### UndeclaredIdentifier

- Case `Python-UndeclaredIdentifier-normal1`: expected `UndeclaredIdentifier`, actual `NameError`, status **FAIL**
- Observed rule types: `NameError`
```
def calc():
    return missing_value + 1
```
- Case `Python-UndeclaredIdentifier-normal2`: expected `UndeclaredIdentifier`, actual `NameError`, status **FAIL**
- Observed rule types: `NameError`
```
print(user_name)
```
- Case `Python-UndeclaredIdentifier-edge`: expected `UndeclaredIdentifier`, actual `NameError`, status **FAIL**
- Observed rule types: `NameError`
```
class S:
    def m(self):
        return not_defined_here
```
- Case `Python-UndeclaredIdentifier-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### UnmatchedBracket

- Case `Python-UnmatchedBracket-normal1`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `SyntaxError, UnclosedString, UnmatchedBracket`
```
items = [1, 2, 3
```
- Case `Python-UnmatchedBracket-normal2`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `UnclosedString, UnmatchedBracket`
```
print((1 + 2]
```
- Case `Python-UnmatchedBracket-edge`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `UnclosedString, UnmatchedBracket`
```
config = {'a': 1, 'b': (2, 3}
```
- Case `Python-UnmatchedBracket-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### UnreachableCode

- Case `Python-UnreachableCode-normal1`: expected `UnreachableCode`, actual `UnreachableCode`, status **PASS**
```
def f():
    return 1
    print('never')
```
- Case `Python-UnreachableCode-normal2`: expected `UnreachableCode`, actual `UnreachableCode`, status **PASS**
```
def g(x):
    if x:
        raise ValueError('x')
        x += 1
```
- Case `Python-UnreachableCode-edge`: expected `UnreachableCode`, actual `UnreachableCode`, status **PASS**
```
def h():
    for i in range(1):
        break
        print(i)
```
- Case `Python-UnreachableCode-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### UnusedVariable

- Case `Python-UnusedVariable-normal1`: expected `UnusedVariable`, actual `NoError`, status **FAIL**
```
def f():
    tmp = 10
    return 1
```
- Case `Python-UnusedVariable-normal2`: expected `UnusedVariable`, actual `NoError`, status **FAIL**
```
x = 3
y = 4
print(x)
```
- Case `Python-UnusedVariable-edge`: expected `UnusedVariable`, actual `NoError`, status **FAIL**
```
for i in range(3):
    shadow = i
print('done')
```
- Case `Python-UnusedVariable-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

#### WildcardImport

- Case `Python-WildcardImport-normal1`: expected `WildcardImport`, actual `WildcardImport`, status **PASS**
- Observed rule types: `WildcardImport`
```
from math import *
value = sqrt(9)
```
- Case `Python-WildcardImport-normal2`: expected `WildcardImport`, actual `WildcardImport`, status **PASS**
- Observed rule types: `WildcardImport`
```
from collections import *
count = Counter([1, 1, 2])
```
- Case `Python-WildcardImport-edge`: expected `WildcardImport`, actual `WildcardImport`, status **PASS**
- Observed rule types: `WildcardImport`
```
from datetime import *
today = date.today()
```
- Case `Python-WildcardImport-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
def add(a, b):
    return a + b

print(add(2, 3))
```

### Java

#### DivisionByZero

- Case `Java-DivisionByZero-normal1`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
- Observed rule types: `DivisionByZero`
```
public class Main {
    public static void main(String[] args) {
        int z = 10 / 0;
    }
}
```
- Case `Java-DivisionByZero-normal2`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
- Observed rule types: `DivisionByZero`
```
public class Main {
    public static void main(String[] args) {
        int z = 10 % 0;
    }
}
```
- Case `Java-DivisionByZero-edge`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
- Observed rule types: `DivisionByZero`
```
public class Main {
    public static void main(String[] args) {
        int d = 0;
        int z = 10 / d;
    }
}
```
- Case `Java-DivisionByZero-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
public class Main {
    public static void main(String[] args) {
        int x = 1;
        System.out.println(x);
    }
}
```

#### DuplicateDefinition

- Case `Java-DuplicateDefinition-normal1`: expected `DuplicateDefinition`, actual `DuplicateDefinition`, status **PASS**
```
public class Main {
    static int f() { return 1; }
    static int f() { return 2; }
}
```
- Case `Java-DuplicateDefinition-normal2`: expected `DuplicateDefinition`, actual `DuplicateDefinition`, status **PASS**
```
public class Main {
    static void log() {}
    static void log() {}
}
```
- Case `Java-DuplicateDefinition-edge`: expected `DuplicateDefinition`, actual `NoError`, status **FAIL**
```
public class Main {
    int x;
    int x;
}
```
- Case `Java-DuplicateDefinition-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
public class Main {
    public static void main(String[] args) {
        int x = 1;
        System.out.println(x);
    }
}
```

#### ImportError

- Case `Java-ImportError-normal1`: expected `ImportError`, actual `NoError`, status **FAIL**
```
import foo.bar.Baz;
public class Main { public static void main(String[] args) {} }
```
- Case `Java-ImportError-normal2`: expected `ImportError`, actual `NoError`, status **FAIL**
```
import java.util.DoesNotExist;
public class Main { public static void main(String[] args) {} }
```
- Case `Java-ImportError-edge`: expected `ImportError`, actual `NoError`, status **FAIL**
```
import not.real.Package;
public class Main { public static void main(String[] args) {} }
```
- Case `Java-ImportError-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
public class Main {
    public static void main(String[] args) {
        int x = 1;
        System.out.println(x);
    }
}
```

#### InfiniteLoop

- Case `Java-InfiniteLoop-normal1`: expected `InfiniteLoop`, actual `InfiniteLoop`, status **PASS**
- Observed rule types: `InfiniteLoop`
```
public class Main {
    public static void main(String[] args) {
        while(true) {}
    }
}
```
- Case `Java-InfiniteLoop-normal2`: expected `InfiniteLoop`, actual `InfiniteLoop`, status **PASS**
- Observed rule types: `InfiniteLoop`
```
public class Main {
    public static void main(String[] args) {
        for(;;) {}
    }
}
```
- Case `Java-InfiniteLoop-edge`: expected `InfiniteLoop`, actual `InfiniteLoop`, status **PASS**
- Observed rule types: `InfiniteLoop`
```
public class Main {
    public static void main(String[] args) {
        while (true) { if (Math.random() > 2) break; }
    }
}
```
- Case `Java-InfiniteLoop-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
public class Main {
    public static void main(String[] args) {
        int x = 1;
        System.out.println(x);
    }
}
```

#### InvalidAssignment

- Case `Java-InvalidAssignment-normal1`: expected `InvalidAssignment`, actual `NoError`, status **FAIL**
```
public class Main {
    public static void main(String[] args) {
        final int x = 1;
        x = 2;
    }
}
```
- Case `Java-InvalidAssignment-normal2`: expected `InvalidAssignment`, actual `NoError`, status **FAIL**
```
public class Main {
    public static void main(String[] args) {
        5 = 3;
    }
}
```
- Case `Java-InvalidAssignment-edge`: expected `InvalidAssignment`, actual `UndeclaredIdentifier`, status **FAIL**
- Observed rule types: `UndeclaredIdentifier`
```
public class Main {
    public static void main(String[] args) {
        int[] arr = {1,2};
        arr = 3;
    }
}
```
- Case `Java-InvalidAssignment-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
public class Main {
    public static void main(String[] args) {
        int x = 1;
        System.out.println(x);
    }
}
```

#### LineTooLong

- Case `Java-LineTooLong-normal1`: expected `LineTooLong`, actual `NoError`, status **FAIL**
```
public class Main { public static void main(String[] args) { String s = "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"; System.out.println(s); } }
```
- Case `Java-LineTooLong-normal2`: expected `LineTooLong`, actual `UnmatchedBracket`, status **FAIL**
- Observed rule types: `UnmatchedBracket`
```
public class Main { public static void main(String[] args) { int x = 1; // aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa } }
```
- Case `Java-LineTooLong-edge`: expected `LineTooLong`, actual `NoError`, status **FAIL**
```
public class Main { public static void main(String[] args) { String q = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" + "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"; } }
```
- Case `Java-LineTooLong-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
public class Main {
    public static void main(String[] args) {
        int x = 1;
        System.out.println(x);
    }
}
```

#### MissingDelimiter

- Case `Java-MissingDelimiter-normal1`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
public class Main {
    public static void main(String[] args) {
        int x = 1
    }
}
```
- Case `Java-MissingDelimiter-normal2`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
public class Main {
    public static void main(String[] args) {
        System.out.println(1)
    }
}
```
- Case `Java-MissingDelimiter-edge`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
public class Main {
    public static void main(String[] args) {
        int x = 1 System.out.println(x);
    }
}
```
- Case `Java-MissingDelimiter-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
public class Main {
    public static void main(String[] args) {
        int x = 1;
        System.out.println(x);
    }
}
```

#### MissingImport

- Case `Java-MissingImport-normal1`: expected `MissingImport`, actual `MissingImport`, status **PASS**
- Observed rule types: `MissingImport`
```
public class Main {
    public static void main(String[] args) {
        ArrayList<Integer> xs = new ArrayList<>();
    }
}
```
- Case `Java-MissingImport-normal2`: expected `MissingImport`, actual `MissingImport`, status **PASS**
- Observed rule types: `MissingImport`
```
public class Main {
    public static void main(String[] args) {
        List<String> xs = new ArrayList<>();
    }
}
```
- Case `Java-MissingImport-edge`: expected `MissingImport`, actual `MissingImport`, status **PASS**
- Observed rule types: `MissingImport`
```
public class Main {
    public static void main(String[] args) {
        HashMap<String, Integer> m = new HashMap<>();
    }
}
```
- Case `Java-MissingImport-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
public class Main {
    public static void main(String[] args) {
        int x = 1;
        System.out.println(x);
    }
}
```

#### TypeMismatch

- Case `Java-TypeMismatch-normal1`: expected `TypeMismatch`, actual `TypeMismatch`, status **PASS**
- Observed rule types: `TypeMismatch`
```
public class Main {
    public static void main(String[] args) {
        int n = "5";
    }
}
```
- Case `Java-TypeMismatch-normal2`: expected `TypeMismatch`, actual `TypeMismatch`, status **PASS**
- Observed rule types: `TypeMismatch`
```
public class Main {
    public static void main(String[] args) {
        String s = 99;
    }
}
```
- Case `Java-TypeMismatch-edge`: expected `TypeMismatch`, actual `TypeMismatch`, status **PASS**
- Observed rule types: `TypeMismatch`
```
public class Main {
    public static void main(String[] args) {
        boolean ok = "true";
    }
}
```
- Case `Java-TypeMismatch-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
public class Main {
    public static void main(String[] args) {
        int x = 1;
        System.out.println(x);
    }
}
```

#### UnclosedString

- Case `Java-UnclosedString-normal1`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `MissingDelimiter, UnclosedString`
```
public class Main {
    public static void main(String[] args) {
        String s = "hello;
    }
}
```
- Case `Java-UnclosedString-normal2`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `UnclosedString`
```
public class Main {
    public static void main(String[] args) {
        System.out.println("x);
    }
}
```
- Case `Java-UnclosedString-edge`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `MissingDelimiter, UnclosedString`
```
public class Main {
    public static void main(String[] args) {
        String q = "value: " + 10;
        String x = "unterminated;
    }
}
```
- Case `Java-UnclosedString-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
public class Main {
    public static void main(String[] args) {
        int x = 1;
        System.out.println(x);
    }
}
```

#### UndeclaredIdentifier

- Case `Java-UndeclaredIdentifier-normal1`: expected `UndeclaredIdentifier`, actual `UndeclaredIdentifier`, status **PASS**
- Observed rule types: `UndeclaredIdentifier`
```
public class Main {
    public static void main(String[] args) {
        System.out.println(total);
    }
}
```
- Case `Java-UndeclaredIdentifier-normal2`: expected `UndeclaredIdentifier`, actual `UndeclaredIdentifier`, status **PASS**
- Observed rule types: `UndeclaredIdentifier`
```
public class Main {
    public static void main(String[] args) {
        int x = y + 1;
    }
}
```
- Case `Java-UndeclaredIdentifier-edge`: expected `UndeclaredIdentifier`, actual `UndeclaredIdentifier`, status **PASS**
- Observed rule types: `UndeclaredIdentifier`
```
public class Main {
    public static void main(String[] args) {
        if (flag) {
            System.out.println(1);
        }
    }
}
```
- Case `Java-UndeclaredIdentifier-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
public class Main {
    public static void main(String[] args) {
        int x = 1;
        System.out.println(x);
    }
}
```

#### UnmatchedBracket

- Case `Java-UnmatchedBracket-normal1`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `UnmatchedBracket`
```
public class Main {
    public static void main(String[] args) {
        if (true) {
            System.out.println(1);
    }
}
```
- Case `Java-UnmatchedBracket-normal2`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `UnmatchedBracket`
```
public class Main {
    public static void main(String[] args {
        System.out.println(1);
    }
}
```
- Case `Java-UnmatchedBracket-edge`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `UnmatchedBracket`
```
public class Main {
    public static void main(String[] args) {
        System.out.println(1));
    }
}
```
- Case `Java-UnmatchedBracket-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
public class Main {
    public static void main(String[] args) {
        int x = 1;
        System.out.println(x);
    }
}
```

#### UnreachableCode

- Case `Java-UnreachableCode-normal1`: expected `UnreachableCode`, actual `UnreachableCode`, status **PASS**
- Observed rule types: `UnreachableCode`
```
public class Main {
    static int f() {
        return 1;
        int x = 2;
    }
}
```
- Case `Java-UnreachableCode-normal2`: expected `UnreachableCode`, actual `UnreachableCode`, status **PASS**
- Observed rule types: `UnreachableCode`
```
public class Main {
    static void f() {
        throw new RuntimeException();
        System.out.println(1);
    }
}
```
- Case `Java-UnreachableCode-edge`: expected `UnreachableCode`, actual `InfiniteLoop`, status **FAIL**
- Observed rule types: `InfiniteLoop, UnreachableCode`
```
public class Main {
    static void f() {
        while (true) {
            continue;
            int y = 1;
        }
    }
}
```
- Case `Java-UnreachableCode-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
public class Main {
    public static void main(String[] args) {
        int x = 1;
        System.out.println(x);
    }
}
```

#### UnusedVariable

- Case `Java-UnusedVariable-normal1`: expected `UnusedVariable`, actual `NoError`, status **FAIL**
```
public class Main {
    public static void main(String[] args) {
        int temp = 1;
        System.out.println("ok");
    }
}
```
- Case `Java-UnusedVariable-normal2`: expected `UnusedVariable`, actual `NoError`, status **FAIL**
```
public class Main {
    public static void main(String[] args) {
        String name = "x";
    }
}
```
- Case `Java-UnusedVariable-edge`: expected `UnusedVariable`, actual `NoError`, status **FAIL**
```
public class Main {
    public static void main(String[] args) {
        int i = 0;
        while (i < 1) { break; }
    }
}
```
- Case `Java-UnusedVariable-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
public class Main {
    public static void main(String[] args) {
        int x = 1;
        System.out.println(x);
    }
}
```

### C

#### DivisionByZero

- Case `C-DivisionByZero-normal1`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
- Observed rule types: `DivisionByZero`
```
int main() {
    int z = 10 / 0;
    return z;
}
```
- Case `C-DivisionByZero-normal2`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
- Observed rule types: `DivisionByZero`
```
int main() {
    int z = 10 % 0;
    return z;
}
```
- Case `C-DivisionByZero-edge`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
- Observed rule types: `DivisionByZero`
```
int main() {
    int d = 0;
    int z = 10 / d;
    return z;
}
```
- Case `C-DivisionByZero-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <stdio.h>
int main() {
    int x = 1;
    printf("%d\n", x);
    return 0;
}
```

#### InfiniteLoop

- Case `C-InfiniteLoop-normal1`: expected `InfiniteLoop`, actual `InfiniteLoop`, status **PASS**
- Observed rule types: `InfiniteLoop`
```
int main() {
    while(1) {}
}
```
- Case `C-InfiniteLoop-normal2`: expected `InfiniteLoop`, actual `InfiniteLoop`, status **PASS**
- Observed rule types: `InfiniteLoop`
```
int main() {
    for(;;) {}
}
```
- Case `C-InfiniteLoop-edge`: expected `InfiniteLoop`, actual `InfiniteLoop`, status **PASS**
- Observed rule types: `InfiniteLoop`
```
int main() {
    while(true) {}
}
```
- Case `C-InfiniteLoop-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <stdio.h>
int main() {
    int x = 1;
    printf("%d\n", x);
    return 0;
}
```

#### MissingDelimiter

- Case `C-MissingDelimiter-normal1`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
int main() {
    int x = 1
    return x;
}
```
- Case `C-MissingDelimiter-normal2`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
#include <stdio.h>
int main() {
    printf("hi")
    return 0;
}
```
- Case `C-MissingDelimiter-edge`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
#include <stdio.h>
int main() {
    int x = 1 printf("%d", x);
    return 0;
}
```
- Case `C-MissingDelimiter-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <stdio.h>
int main() {
    int x = 1;
    printf("%d\n", x);
    return 0;
}
```

#### MissingInclude

- Case `C-MissingInclude-normal1`: expected `MissingInclude`, actual `MissingInclude`, status **PASS**
- Observed rule types: `MissingInclude`
```
int main() {
    printf("hi");
    return 0;
}
```
- Case `C-MissingInclude-normal2`: expected `MissingInclude`, actual `MissingInclude`, status **PASS**
- Observed rule types: `MissingInclude`
```
int main() {
    int *p = malloc(sizeof(int));
    return 0;
}
```
- Case `C-MissingInclude-edge`: expected `MissingInclude`, actual `MissingInclude`, status **PASS**
- Observed rule types: `MissingInclude`
```
int main() {
    int n = strlen("abc");
    return n;
}
```
- Case `C-MissingInclude-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <stdio.h>
int main() {
    int x = 1;
    printf("%d\n", x);
    return 0;
}
```

#### TypeMismatch

- Case `C-TypeMismatch-normal1`: expected `TypeMismatch`, actual `TypeMismatch`, status **PASS**
- Observed rule types: `TypeMismatch`
```
int main() {
    int x = "10";
    return 0;
}
```
- Case `C-TypeMismatch-normal2`: expected `TypeMismatch`, actual `TypeMismatch`, status **PASS**
- Observed rule types: `TypeMismatch`
```
int main() {
    char c = 'ab';
    return 0;
}
```
- Case `C-TypeMismatch-edge`: expected `TypeMismatch`, actual `TypeMismatch`, status **PASS**
- Observed rule types: `TypeMismatch`
```
int main() {
    double d = "3.14";
    return 0;
}
```
- Case `C-TypeMismatch-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <stdio.h>
int main() {
    int x = 1;
    printf("%d\n", x);
    return 0;
}
```

#### UnclosedString

- Case `C-UnclosedString-normal1`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `UnclosedString`
```
#include <stdio.h>
int main() {
    printf("hello);
    return 0;
}
```
- Case `C-UnclosedString-normal2`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `MissingDelimiter, UnclosedString`
```
int main() {
    char *s = "abc;
    return 0;
}
```
- Case `C-UnclosedString-edge`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `UnclosedString`
```
#include <stdio.h>
int main() {
    fprintf(stdout, "value=%d, x);
    return 0;
}
```
- Case `C-UnclosedString-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <stdio.h>
int main() {
    int x = 1;
    printf("%d\n", x);
    return 0;
}
```

#### UndeclaredIdentifier

- Case `C-UndeclaredIdentifier-normal1`: expected `UndeclaredIdentifier`, actual `UndeclaredIdentifier`, status **PASS**
- Observed rule types: `UndeclaredIdentifier`
```
int main() {
    return y;
}
```
- Case `C-UndeclaredIdentifier-normal2`: expected `UndeclaredIdentifier`, actual `UndeclaredIdentifier`, status **PASS**
- Observed rule types: `UndeclaredIdentifier`
```
int main() {
    int x = z + 1;
    return x;
}
```
- Case `C-UndeclaredIdentifier-edge`: expected `UndeclaredIdentifier`, actual `UndeclaredIdentifier`, status **PASS**
- Observed rule types: `UndeclaredIdentifier`
```
#include <stdio.h>
int main() {
    printf("%d", value);
    return 0;
}
```
- Case `C-UndeclaredIdentifier-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <stdio.h>
int main() {
    int x = 1;
    printf("%d\n", x);
    return 0;
}
```

#### UnmatchedBracket

- Case `C-UnmatchedBracket-normal1`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `UnmatchedBracket`
```
int main() {
    int x = 1;
```
- Case `C-UnmatchedBracket-normal2`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `UnmatchedBracket`
```
int main( {
    return 0;
}
```
- Case `C-UnmatchedBracket-edge`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `UnmatchedBracket`
```
int main() {
    if (1) {
        return 0;
    }
}}
```
- Case `C-UnmatchedBracket-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <stdio.h>
int main() {
    int x = 1;
    printf("%d\n", x);
    return 0;
}
```

#### UnreachableCode

- Case `C-UnreachableCode-normal1`: expected `UnreachableCode`, actual `UnreachableCode`, status **PASS**
- Observed rule types: `UnreachableCode`
```
int main() {
    return 0;
    int x = 1;
}
```
- Case `C-UnreachableCode-normal2`: expected `UnreachableCode`, actual `InfiniteLoop`, status **FAIL**
- Observed rule types: `InfiniteLoop, UnreachableCode`
```
int main() {
    while (1) {
        break;
        int y = 2;
    }
    return 0;
}
```
- Case `C-UnreachableCode-edge`: expected `UnreachableCode`, actual `InfiniteLoop`, status **FAIL**
- Observed rule types: `InfiniteLoop, UnreachableCode`
```
int main() {
    while (1) {
        continue;
        int z = 3;
    }
}
```
- Case `C-UnreachableCode-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <stdio.h>
int main() {
    int x = 1;
    printf("%d\n", x);
    return 0;
}
```

### C++

#### DanglingPointer

- Case `C++-DanglingPointer-normal1`: expected `DanglingPointer`, actual `DanglingPointer`, status **PASS**
- Observed rule types: `DanglingPointer`
```
int* bad() {
    int x = 5;
    return &x;
}
int main() {
    int* p = bad();
    return *p;
}
```
- Case `C++-DanglingPointer-normal2`: expected `DanglingPointer`, actual `DanglingPointer`, status **PASS**
- Observed rule types: `DanglingPointer`
```
int* leak() {
    int local = 10;
    return &local;
}
int main() {
    int* q = leak();
    int v = *q;
    return v;
}
```
- Case `C++-DanglingPointer-edge`: expected `DanglingPointer`, actual `DanglingPointer`, status **PASS**
- Observed rule types: `DanglingPointer, UnreachableCode`
```
int* risky() {
    int n = 3;
    return &n;
}
int main() {
    int* ptr = risky();
    if (ptr) return *ptr;
    return 0;
}
```
- Case `C++-DanglingPointer-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <iostream>
int main() {
    int x = 1;
    std::cout << x << std::endl;
    return 0;
}
```

#### DivisionByZero

- Case `C++-DivisionByZero-normal1`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
- Observed rule types: `DivisionByZero`
```
int main() {
    int z = 10 / 0;
    return z;
}
```
- Case `C++-DivisionByZero-normal2`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
- Observed rule types: `DivisionByZero`
```
int main() {
    int z = 10 % 0;
    return z;
}
```
- Case `C++-DivisionByZero-edge`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
- Observed rule types: `DivisionByZero`
```
int main() {
    int d = 0;
    int z = 10 / d;
    return z;
}
```
- Case `C++-DivisionByZero-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <iostream>
int main() {
    int x = 1;
    std::cout << x << std::endl;
    return 0;
}
```

#### InfiniteLoop

- Case `C++-InfiniteLoop-normal1`: expected `InfiniteLoop`, actual `InfiniteLoop`, status **PASS**
- Observed rule types: `InfiniteLoop`
```
int main() {
    while(1) {}
}
```
- Case `C++-InfiniteLoop-normal2`: expected `InfiniteLoop`, actual `InfiniteLoop`, status **PASS**
- Observed rule types: `InfiniteLoop`
```
int main() {
    for(;;) {}
}
```
- Case `C++-InfiniteLoop-edge`: expected `InfiniteLoop`, actual `InfiniteLoop`, status **PASS**
- Observed rule types: `InfiniteLoop`
```
int main() {
    while(true) {}
}
```
- Case `C++-InfiniteLoop-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <iostream>
int main() {
    int x = 1;
    std::cout << x << std::endl;
    return 0;
}
```

#### MissingDelimiter

- Case `C++-MissingDelimiter-normal1`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
#include <iostream>
int main() {
    int x = 1
    return x;
}
```
- Case `C++-MissingDelimiter-normal2`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
#include <iostream>
int main() {
    std::cout << 1
    return 0;
}
```
- Case `C++-MissingDelimiter-edge`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
#include <iostream>
int main() {
    int x = 1 std::cout << x;
    return 0;
}
```
- Case `C++-MissingDelimiter-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <iostream>
int main() {
    int x = 1;
    std::cout << x << std::endl;
    return 0;
}
```

#### MissingInclude

- Case `C++-MissingInclude-normal1`: expected `MissingInclude`, actual `MissingInclude`, status **PASS**
- Observed rule types: `MissingInclude`
```
int main() {
    std::cout << 1;
    return 0;
}
```
- Case `C++-MissingInclude-normal2`: expected `MissingInclude`, actual `MissingInclude`, status **PASS**
- Observed rule types: `MissingInclude`
```
int main() {
    cout << 1;
    return 0;
}
```
- Case `C++-MissingInclude-edge`: expected `MissingInclude`, actual `MissingInclude`, status **PASS**
- Observed rule types: `MissingInclude`
```
int main() {
    int n = strlen("abc");
    return n;
}
```
- Case `C++-MissingInclude-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <iostream>
int main() {
    int x = 1;
    std::cout << x << std::endl;
    return 0;
}
```

#### TypeMismatch

- Case `C++-TypeMismatch-normal1`: expected `TypeMismatch`, actual `TypeMismatch`, status **PASS**
- Observed rule types: `TypeMismatch`
```
int main() {
    int x = "10";
    return 0;
}
```
- Case `C++-TypeMismatch-normal2`: expected `TypeMismatch`, actual `TypeMismatch`, status **PASS**
- Observed rule types: `TypeMismatch`
```
int main() {
    char c = 'ab';
    return 0;
}
```
- Case `C++-TypeMismatch-edge`: expected `TypeMismatch`, actual `TypeMismatch`, status **PASS**
- Observed rule types: `TypeMismatch`
```
int main() {
    double d = "3.14";
    return 0;
}
```
- Case `C++-TypeMismatch-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <iostream>
int main() {
    int x = 1;
    std::cout << x << std::endl;
    return 0;
}
```

#### UnclosedString

- Case `C++-UnclosedString-normal1`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `MissingDelimiter, UnclosedString`
```
#include <iostream>
int main() {
    std::cout << "hello;
    return 0;
}
```
- Case `C++-UnclosedString-normal2`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `MissingDelimiter, UnclosedString`
```
int main() {
    const char* s = "abc;
    return 0;
}
```
- Case `C++-UnclosedString-edge`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `MissingInclude, UnclosedString`
```
#include <cstdio>
int main() {
    printf("value=%d, x);
    return 0;
}
```
- Case `C++-UnclosedString-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <iostream>
int main() {
    int x = 1;
    std::cout << x << std::endl;
    return 0;
}
```

#### UndeclaredIdentifier

- Case `C++-UndeclaredIdentifier-normal1`: expected `UndeclaredIdentifier`, actual `UndeclaredIdentifier`, status **PASS**
- Observed rule types: `UndeclaredIdentifier`
```
#include <iostream>
int main() {
    std::cout << y;
    return 0;
}
```
- Case `C++-UndeclaredIdentifier-normal2`: expected `UndeclaredIdentifier`, actual `UndeclaredIdentifier`, status **PASS**
- Observed rule types: `UndeclaredIdentifier`
```
int main() {
    int x = z + 1;
    return x;
}
```
- Case `C++-UndeclaredIdentifier-edge`: expected `UndeclaredIdentifier`, actual `MissingInclude`, status **FAIL**
- Observed rule types: `MissingInclude, UndeclaredIdentifier`
```
#include <cstdio>
int main() {
    printf("%d", value);
    return 0;
}
```
- Case `C++-UndeclaredIdentifier-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <iostream>
int main() {
    int x = 1;
    std::cout << x << std::endl;
    return 0;
}
```

#### UnmatchedBracket

- Case `C++-UnmatchedBracket-normal1`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `UnmatchedBracket`
```
int main() {
    int x = 1;
```
- Case `C++-UnmatchedBracket-normal2`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `UnmatchedBracket`
```
int main( {
    return 0;
}
```
- Case `C++-UnmatchedBracket-edge`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `UnmatchedBracket`
```
int main() {
    if (true) {
        return 0;
    }
}}
```
- Case `C++-UnmatchedBracket-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <iostream>
int main() {
    int x = 1;
    std::cout << x << std::endl;
    return 0;
}
```

#### UnreachableCode

- Case `C++-UnreachableCode-normal1`: expected `UnreachableCode`, actual `UnreachableCode`, status **PASS**
- Observed rule types: `UnreachableCode`
```
int main() {
    return 0;
    int x = 1;
}
```
- Case `C++-UnreachableCode-normal2`: expected `UnreachableCode`, actual `InfiniteLoop`, status **FAIL**
- Observed rule types: `InfiniteLoop, UnreachableCode`
```
int main() {
    while (1) {
        break;
        int y = 2;
    }
    return 0;
}
```
- Case `C++-UnreachableCode-edge`: expected `UnreachableCode`, actual `InfiniteLoop`, status **FAIL**
- Observed rule types: `InfiniteLoop, UnreachableCode`
```
int main() {
    while (1) {
        continue;
        int z = 3;
    }
}
```
- Case `C++-UnreachableCode-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
#include <iostream>
int main() {
    int x = 1;
    std::cout << x << std::endl;
    return 0;
}
```

### JavaScript

#### DivisionByZero

- Case `JavaScript-DivisionByZero-normal1`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
- Observed rule types: `DivisionByZero`
```
let z = 10 / 0;
```
- Case `JavaScript-DivisionByZero-normal2`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
- Observed rule types: `DivisionByZero`
```
let r = 10 % 0;
```
- Case `JavaScript-DivisionByZero-edge`: expected `DivisionByZero`, actual `DivisionByZero`, status **PASS**
- Observed rule types: `DivisionByZero`
```
let d = 0;
let z = 10 / d;
```
- Case `JavaScript-DivisionByZero-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
function add(a, b) {
    return a + b;
}
console.log(add(2, 3));
```

#### DuplicateDefinition

- Case `JavaScript-DuplicateDefinition-normal1`: expected `DuplicateDefinition`, actual `DuplicateDefinition`, status **PASS**
- Observed rule types: `DuplicateDefinition`
```
let a = 1;
let a = 2;
```
- Case `JavaScript-DuplicateDefinition-normal2`: expected `DuplicateDefinition`, actual `DuplicateDefinition`, status **PASS**
- Observed rule types: `DuplicateDefinition`
```
const n = 1;
const n = 3;
```
- Case `JavaScript-DuplicateDefinition-edge`: expected `DuplicateDefinition`, actual `DuplicateDefinition`, status **PASS**
- Observed rule types: `DuplicateDefinition`
```
let z = 1;
{ let z = 2; }
let z = 3;
```
- Case `JavaScript-DuplicateDefinition-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
function add(a, b) {
    return a + b;
}
console.log(add(2, 3));
```

#### InfiniteLoop

- Case `JavaScript-InfiniteLoop-normal1`: expected `InfiniteLoop`, actual `InfiniteLoop`, status **PASS**
- Observed rule types: `InfiniteLoop`
```
while(true) {}
```
- Case `JavaScript-InfiniteLoop-normal2`: expected `InfiniteLoop`, actual `InfiniteLoop`, status **PASS**
- Observed rule types: `InfiniteLoop`
```
for(;;) {}
```
- Case `JavaScript-InfiniteLoop-edge`: expected `InfiniteLoop`, actual `InfiniteLoop`, status **PASS**
- Observed rule types: `InfiniteLoop`
```
while(1) {}
```
- Case `JavaScript-InfiniteLoop-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
function add(a, b) {
    return a + b;
}
console.log(add(2, 3));
```

#### MissingDelimiter

- Case `JavaScript-MissingDelimiter-normal1`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
let x = ;
console.log(x);
```
- Case `JavaScript-MissingDelimiter-normal2`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
const user = 1 console.log(user);
```
- Case `JavaScript-MissingDelimiter-edge`: expected `MissingDelimiter`, actual `MissingDelimiter`, status **PASS**
- Observed rule types: `MissingDelimiter`
```
const profile = {};
profile..name = 'a';
```
- Case `JavaScript-MissingDelimiter-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
function add(a, b) {
    return a + b;
}
console.log(add(2, 3));
```

#### UnclosedString

- Case `JavaScript-UnclosedString-normal1`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `UnclosedString`
```
const s = "hello;
console.log(s);
```
- Case `JavaScript-UnclosedString-normal2`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `UnclosedString`
```
console.log('x);
```
- Case `JavaScript-UnclosedString-edge`: expected `UnclosedString`, actual `UnclosedString`, status **PASS**
- Observed rule types: `UnclosedString, UndeclaredIdentifier`
```
const t = `hello ${name;
```
- Case `JavaScript-UnclosedString-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
function add(a, b) {
    return a + b;
}
console.log(add(2, 3));
```

#### UndeclaredIdentifier

- Case `JavaScript-UndeclaredIdentifier-normal1`: expected `UndeclaredIdentifier`, actual `UndeclaredIdentifier`, status **PASS**
- Observed rule types: `UndeclaredIdentifier`
```
console.log(total);
```
- Case `JavaScript-UndeclaredIdentifier-normal2`: expected `UndeclaredIdentifier`, actual `UndeclaredIdentifier`, status **PASS**
- Observed rule types: `UndeclaredIdentifier`
```
let x = y + 1;
```
- Case `JavaScript-UndeclaredIdentifier-edge`: expected `UndeclaredIdentifier`, actual `UndeclaredIdentifier`, status **PASS**
- Observed rule types: `UndeclaredIdentifier`
```
function f() {
  return missingVar;
}
```
- Case `JavaScript-UndeclaredIdentifier-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
function add(a, b) {
    return a + b;
}
console.log(add(2, 3));
```

#### UnmatchedBracket

- Case `JavaScript-UnmatchedBracket-normal1`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `UnmatchedBracket`
```
function f() {
  console.log(1);
```
- Case `JavaScript-UnmatchedBracket-normal2`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `UnmatchedBracket`
```
if (true] {
  console.log(1);
}
```
- Case `JavaScript-UnmatchedBracket-edge`: expected `UnmatchedBracket`, actual `UnmatchedBracket`, status **PASS**
- Observed rule types: `UnmatchedBracket`
```
const arr = [1, 2, 3;
```
- Case `JavaScript-UnmatchedBracket-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
function add(a, b) {
    return a + b;
}
console.log(add(2, 3));
```

#### UnreachableCode

- Case `JavaScript-UnreachableCode-normal1`: expected `UnreachableCode`, actual `UnreachableCode`, status **PASS**
- Observed rule types: `UnreachableCode`
```
function f() {
  return 1;
  console.log('never');
}
```
- Case `JavaScript-UnreachableCode-normal2`: expected `UnreachableCode`, actual `UndeclaredIdentifier`, status **FAIL**
- Observed rule types: `UndeclaredIdentifier, UnreachableCode`
```
function g() {
  throw new Error('x');
  let y = 1;
}
```
- Case `JavaScript-UnreachableCode-edge`: expected `UnreachableCode`, actual `InfiniteLoop`, status **FAIL**
- Observed rule types: `InfiniteLoop, UnreachableCode`
```
function h() {
  while (true) {
    continue;
    let z = 1;
  }
}
```
- Case `JavaScript-UnreachableCode-negative`: expected `NoError`, actual `NoError`, status **PASS**
```
function add(a, b) {
    return a + b;
}
console.log(add(2, 3));
```

## 3) Failure Analysis

### False Positives

- None in this run.

### False Negatives

- Python / ImportError / normal2: expected `ImportError`, predicted `NoError`
- Python / ImportError / edge: expected `ImportError`, predicted `NoError`
- Python / InfiniteLoop / normal2: expected `InfiniteLoop`, predicted `NoError`
- Python / DuplicateDefinition / normal1: expected `DuplicateDefinition`, predicted `NoError`
- Python / DuplicateDefinition / normal2: expected `DuplicateDefinition`, predicted `NoError`
- Python / DuplicateDefinition / edge: expected `DuplicateDefinition`, predicted `NoError`
- Python / UnusedVariable / normal1: expected `UnusedVariable`, predicted `NoError`
- Python / UnusedVariable / normal2: expected `UnusedVariable`, predicted `NoError`
- Python / UnusedVariable / edge: expected `UnusedVariable`, predicted `NoError`
- Python / LineTooLong / normal1: expected `LineTooLong`, predicted `NoError`
- Python / LineTooLong / normal2: expected `LineTooLong`, predicted `NoError`
- Python / LineTooLong / edge: expected `LineTooLong`, predicted `NoError`
- Python / TypeMismatch / normal1: expected `TypeMismatch`, predicted `NoError`
- Python / TypeMismatch / normal2: expected `TypeMismatch`, predicted `NoError`
- Python / TypeMismatch / edge: expected `TypeMismatch`, predicted `NoError`
- Python / DanglingPointer / normal1: expected `DanglingPointer`, predicted `NoError`
- Python / DanglingPointer / normal2: expected `DanglingPointer`, predicted `NoError`
- Python / InvalidAssignment / edge: expected `InvalidAssignment`, predicted `NoError`
- Java / ImportError / normal1: expected `ImportError`, predicted `NoError`
- Java / ImportError / normal2: expected `ImportError`, predicted `NoError`
- Java / ImportError / edge: expected `ImportError`, predicted `NoError`
- Java / InvalidAssignment / normal1: expected `InvalidAssignment`, predicted `NoError`
- Java / InvalidAssignment / normal2: expected `InvalidAssignment`, predicted `NoError`
- Java / LineTooLong / normal1: expected `LineTooLong`, predicted `NoError`
- Java / LineTooLong / edge: expected `LineTooLong`, predicted `NoError`
- Java / DuplicateDefinition / edge: expected `DuplicateDefinition`, predicted `NoError`
- Java / UnusedVariable / normal1: expected `UnusedVariable`, predicted `NoError`
- Java / UnusedVariable / normal2: expected `UnusedVariable`, predicted `NoError`
- Java / UnusedVariable / edge: expected `UnusedVariable`, predicted `NoError`

### Misclassifications

- Python / MissingImport: expected `MissingImport`, predicted `NameError` (**x3**)
- Python / DuplicateDefinition: expected `DuplicateDefinition`, predicted `NoError` (**x3**)
- Python / UnusedVariable: expected `UnusedVariable`, predicted `NoError` (**x3**)
- Python / LineTooLong: expected `LineTooLong`, predicted `NoError` (**x3**)
- Python / TypeMismatch: expected `TypeMismatch`, predicted `NoError` (**x3**)
- Python / UndeclaredIdentifier: expected `UndeclaredIdentifier`, predicted `NameError` (**x3**)
- Java / ImportError: expected `ImportError`, predicted `NoError` (**x3**)
- Java / UnusedVariable: expected `UnusedVariable`, predicted `NoError` (**x3**)
- Python / ImportError: expected `ImportError`, predicted `NoError` (**x2**)
- Python / DanglingPointer: expected `DanglingPointer`, predicted `NoError` (**x2**)
- Java / InvalidAssignment: expected `InvalidAssignment`, predicted `NoError` (**x2**)
- Java / LineTooLong: expected `LineTooLong`, predicted `NoError` (**x2**)
- C / UnreachableCode: expected `UnreachableCode`, predicted `InfiniteLoop` (**x2**)
- C++ / UnreachableCode: expected `UnreachableCode`, predicted `InfiniteLoop` (**x2**)
- Python / InfiniteLoop: expected `InfiniteLoop`, predicted `NoError` (**x1**)
- Python / DanglingPointer: expected `DanglingPointer`, predicted `ImportError` (**x1**)
- Python / InvalidAssignment: expected `InvalidAssignment`, predicted `NoError` (**x1**)
- Java / UnreachableCode: expected `UnreachableCode`, predicted `InfiniteLoop` (**x1**)
- Java / InvalidAssignment: expected `InvalidAssignment`, predicted `UndeclaredIdentifier` (**x1**)
- Java / LineTooLong: expected `LineTooLong`, predicted `UnmatchedBracket` (**x1**)
- Java / DuplicateDefinition: expected `DuplicateDefinition`, predicted `NoError` (**x1**)
- C++ / UndeclaredIdentifier: expected `UndeclaredIdentifier`, predicted `MissingInclude` (**x1**)
- JavaScript / UnreachableCode: expected `UnreachableCode`, predicted `UndeclaredIdentifier` (**x1**)
- JavaScript / UnreachableCode: expected `UnreachableCode`, predicted `InfiniteLoop` (**x1**)

### Conflict / Ambiguity Patterns

- Java / UnreachableCode / edge: expected `UnreachableCode`, predicted `InfiniteLoop`, rule-types=['InfiniteLoop', 'UnreachableCode']
- C / UnreachableCode / normal2: expected `UnreachableCode`, predicted `InfiniteLoop`, rule-types=['InfiniteLoop', 'UnreachableCode']
- C / UnreachableCode / edge: expected `UnreachableCode`, predicted `InfiniteLoop`, rule-types=['InfiniteLoop', 'UnreachableCode']
- C++ / UndeclaredIdentifier / edge: expected `UndeclaredIdentifier`, predicted `MissingInclude`, rule-types=['MissingInclude', 'UndeclaredIdentifier']
- C++ / UnreachableCode / normal2: expected `UnreachableCode`, predicted `InfiniteLoop`, rule-types=['InfiniteLoop', 'UnreachableCode']
- C++ / UnreachableCode / edge: expected `UnreachableCode`, predicted `InfiniteLoop`, rule-types=['InfiniteLoop', 'UnreachableCode']
- JavaScript / UnreachableCode / normal2: expected `UnreachableCode`, predicted `UndeclaredIdentifier`, rule-types=['UndeclaredIdentifier', 'UnreachableCode']
- JavaScript / UnreachableCode / edge: expected `UnreachableCode`, predicted `InfiniteLoop`, rule-types=['InfiniteLoop', 'UnreachableCode']

## 4) Improvement Recommendations

### Critical
- Python MissingImport is currently overshadowed by NameError in valid AST code; prioritize explicit module-symbol dependency patterns before NameError shortcut.
- Priority selection currently biases InfiniteLoop above UnreachableCode in C-like languages; unreachable diagnostics are lost in common `break/continue` patterns.
- Python semantic categories mapped in taxonomy (DuplicateDefinition, UnusedVariable, LineTooLong, TypeMismatch, UndeclaredIdentifier) have no reliable rule path in degraded mode.

### Medium
- Java/C/C++/JS UnreachableCode should be block-aware to avoid over-trigger and to preserve specificity.
- C++ UndeclaredIdentifier should not be suppressed by MissingInclude when both occur; return both with confidence-based ordering in all-errors mode.
- InvalidAssignment and ImportError taxonomy entries for Java/Python need dedicated detectors or should be downgraded/renamed in label schema.

### Low
- Add confidence decay when multiple rule types are on same line and message overlap indicates cascading parse errors.
- Add language-specific edge tests for `while(1)` style loops in Java/JS to reduce semantic ambiguity.

## 5) Final Score

- Accuracy: **8.08/10**
- Coverage: **7.42/10**
- Robustness: **6.27/10**
- Production Readiness: **7.31/10**