import os
import sqlite3
from flask import Flask
from models import db, Subject, Chapter, Quiz, Question, CodeChallenge, TestCase, ChallengeTemplate, User

def seed_data(app=None):
    if app is None:
        app = Flask(__name__)
        BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(BASE_DIR, 'instance', 'quiz_app.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

    with app.app_context():
        # Find admin user
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("No admin user found! Please run init_db or launch app first.")
            return
        admin_id = admin.id

        subjects_data = {
            "Python": {
                "theory": """# Python Programming Language

Python is a high-level, interpreted, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.

## Key Features
* **Simple Syntax**: Readable, English-like syntax makes it easy to learn.
* **Dynamically Typed**: Variable types do not need to be declared explicitly.
* **Rich Ecosystem**: Hundreds of thousands of libraries for Web, AI, Science, and Scripting.

### Python Variable Types Comparison

| Type | Mutability | Declaration Example | Common Use Case |
| --- | --- | --- | --- |
| `list` | Mutable | `my_list = [1, 2, 3]` | Ordered collections of items |
| `tuple` | Immutable | `my_tuple = (1, 2, 3)` | Fixed records, coordinates |
| `dict` | Mutable | `my_dict = {"a": 1, "b": 2}` | Key-value mapping, database records |
| `set` | Mutable | `my_set = {1, 2, 3}` | Unique item collections, membership tests |

### Example Code
Here is how you define a function that checks if a number is even:
```python
def is_even(number):
    # Modulo operator returns remainder
    return number % 2 == 0

print(is_even(4)) # Outputs: True
```
""",
                "quizzes": [
                    {
                        "title": "Python Basics Quiz",
                        "description": "Test your knowledge on basic Python concepts like data structures and loops.",
                        "time_limit": 15,
                        "questions": [
                            {
                                "question": "Which of the following data types in Python is immutable?",
                                "a": "List", "b": "Dictionary", "c": "Tuple", "d": "Set",
                                "correct": "C", "points": 2, "hint": "Think about values that cannot be modified after creation.",
                                "explanation": "Tuples are immutable sequence types in Python, meaning once created, elements cannot be altered."
                            },
                            {
                                "question": "What is the output of print(type([]) in Python?",
                                "a": "<class 'dict'>", "b": "<class 'list'>", "c": "<class 'tuple'>", "d": "<class 'set'>",
                                "correct": "B", "points": 1, "hint": "Square brackets define this type.",
                                "explanation": "Square brackets [] denote a list literal in Python."
                            },
                            {
                                "question": "How do you start a comments section in a Python file?",
                                "a": "// comment", "b": "/* comment */", "c": "# comment", "d": "<!-- comment -->",
                                "correct": "C", "points": 1, "hint": "It is a single hash character.",
                                "explanation": "The hash character (#) starts a single line comment in Python."
                            }
                        ]
                    }
                ],
                "challenges": [
                    {
                        "title": "Reverse String",
                        "description": "Write a Python function to reverse a given string. The function will receive a single string via input/stdin and should print the reversed string to stdout.",
                        "difficulty": "Easy",
                        "time_limit": 5,
                        "memory_limit": 256,
                        "template": "def reverse_string(s):\n    return s[::-1]\n\nimport sys\nline = sys.stdin.read().strip()\nprint(reverse_string(line))",
                        "testcases": [
                            {"input": "hello", "output": "olleh", "hidden": False},
                            {"input": "python", "output": "nohtyp", "hidden": False},
                            {"input": "antigravity", "output": "ytivargitna", "hidden": True}
                        ]
                    },
                    {
                        "title": "Sum of Digits",
                        "description": "Write a function that accepts an integer via stdin and prints the sum of its digits to stdout. (e.g. 123 -> 6)",
                        "difficulty": "Medium",
                        "time_limit": 5,
                        "memory_limit": 256,
                        "template": "import sys\nnum_str = sys.stdin.read().strip()\n# Calculate sum\ntotal = sum(int(d) for d in num_str if d.isdigit())\nprint(total)",
                        "testcases": [
                            {"input": "123", "output": "6", "hidden": False},
                            {"input": "999", "output": "27", "hidden": False},
                            {"input": "1002", "output": "3", "hidden": True}
                        ]
                    }
                ],
                "daily": {
                    "quiz": {
                        "title": "Python Daily MCQ",
                        "description": "Test your Python syntax alignment.",
                        "time_limit": 10,
                        "questions": [
                            {
                                "question": "What is the correct syntax to create a list comprehension that squares numbers from 0 to 4?",
                                "a": "[x**2 for x in range(5)]", "b": "[x*2 for x in range(4)]", "c": "{x**2 for x in range(5)}", "d": "[x^2 for x in range(5)]",
                                "correct": "A", "points": 3, "hint": "Python range(N) goes from 0 to N-1, and exponent is double asterisk.",
                                "explanation": "Double asterisk is the exponent operator, and list comprehension uses square brackets."
                            }
                        ]
                    },
                    "challenge": {
                        "title": "Square of a Number",
                        "description": "Accept a integer from stdin and print its square to stdout.",
                        "difficulty": "Easy",
                        "time_limit": 5,
                        "memory_limit": 256,
                        "template": "import sys\nval = int(sys.stdin.read().strip())\nprint(val * val)",
                        "testcases": [
                            {"input": "5", "output": "25", "hidden": False},
                            {"input": "12", "output": "144", "hidden": False},
                            {"input": "-3", "output": "9", "hidden": True}
                        ]
                    }
                }
            },
            "JAVA": {
                "theory": """# Java Programming Language

Java is a class-based, object-oriented, general-purpose programming language designed to have as few implementation dependencies as possible. It is famous for its 'Write Once, Run Anywhere' (WORA) philosophy.

## Core Concepts
* **OOP Principle**: Everything is inside classes. Encapsulation, Polymorphism, Inheritance, and Abstraction.
* **Strongly Typed**: Variable types must be declared explicitly.
* **Platform Independence**: Java compiles to Bytecode which runs on the Java Virtual Machine (JVM).

### Primitive Data Types in Java

| Type | Size (bits) | Default Value | Range Example |
| --- | --- | --- | --- |
| `int` | 32 | 0 | `-2,147,483,648` to `2,147,483,647` |
| `double` | 64 | 0.0d | Double precision decimals |
| `boolean` | 1 | false | `true` or `false` |
| `char` | 16 | '\\u0000' | Single Unicode characters |

### Example Code
A simple Hello World class in Java:
```java
public class HelloWorld {
    public static void main(String[] args) {
        // Print statement
        System.out.println("Hello, World!");
    }
}
```
""",
                "quizzes": [
                    {
                        "title": "Java Basics & OOP Quiz",
                        "description": "Test your knowledge on key OOP principles and basics in Java.",
                        "time_limit": 20,
                        "questions": [
                            {
                                "question": "Which OOP concept in Java allows code reuse by inheriting attributes and methods of a parent class?",
                                "a": "Polymorphism", "b": "Encapsulation", "c": "Inheritance", "d": "Abstraction",
                                "correct": "C", "points": 2, "hint": "Look at the keyword 'extends'.",
                                "explanation": "Inheritance allows a subclass to inherit fields and methods from a superclass using the 'extends' keyword."
                            },
                            {
                                "question": "What is the size of double primitive data type in Java?",
                                "a": "32 bits", "b": "64 bits", "c": "16 bits", "d": "128 bits",
                                "correct": "B", "points": 1, "hint": "It has twice the precision of float.",
                                "explanation": "The double primitive data type is a double-precision 64-bit IEEE 754 floating point."
                            }
                        ]
                    }
                ],
                "challenges": [
                    {
                        "title": "Is Palindrome",
                        "description": "Write a program that accepts a word from stdin and prints 'true' if it is a palindrome, and 'false' otherwise.",
                        "difficulty": "Easy",
                        "time_limit": 10,
                        "memory_limit": 256,
                        "template": "import java.util.Scanner;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNext()) {\n            String s = sc.next();\n            String rev = new StringBuilder(s).reverse().toString();\n            System.out.print(s.equalsIgnoreCase(rev) ? \"true\" : \"false\");\n        }\n    }\n}",
                        "testcases": [
                            {"input": "radar", "output": "true", "hidden": False},
                            {"input": "java", "output": "false", "hidden": False},
                            {"input": "racecar", "output": "true", "hidden": True}
                        ]
                    }
                ],
                "daily": {
                    "quiz": {
                        "title": "Java Daily Challenge Quiz",
                        "description": "Daily JVM concept review.",
                        "time_limit": 10,
                        "questions": [
                            {
                                "question": "Which of these is NOT a wrapper class in Java?",
                                "a": "Integer", "b": "Double", "c": "Boolean", "d": "int",
                                "correct": "D", "points": 2, "hint": "Wrapper classes are object representations and begin with capital letters.",
                                "explanation": "'int' is a primitive type, not a wrapper class. Its corresponding wrapper class is 'Integer'."
                            }
                        ]
                    },
                    "challenge": {
                        "title": "Cube of a Number",
                        "description": "Accept an integer from stdin and print its cube (num^3).",
                        "difficulty": "Easy",
                        "time_limit": 5,
                        "memory_limit": 256,
                        "template": "import java.util.Scanner;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextInt()) {\n            int n = sc.nextInt();\n            System.out.print(n * n * n);\n        }\n    }\n}",
                        "testcases": [
                            {"input": "3", "output": "27", "hidden": False},
                            {"input": "5", "output": "125", "hidden": False},
                            {"input": "-2", "output": "-8", "hidden": True}
                        ]
                    }
                }
            },
            "PHP": {
                "theory": """# PHP: Hypertext Preprocessor

PHP is a popular general-purpose scripting language that is especially suited to web development. It is fast, flexible, and pragmatic.

## Key Concepts
* **Server-side execution**: Code runs on the server, generating HTML sent to the client.
* **Variable prefixes**: All variables in PHP start with a dollar sign `$`.
* **Weakly Typed**: PHP dynamically converts variables to appropriate types when needed.

### PHP Superglobals Comparison

| Superglobal | Source of Data | Common Web Use Case |
| --- | --- | --- |
| `$_GET` | URL Query parameters | Filter search terms, pagination |
| `$_POST` | HTTP POST request payload | Submit forms, create records |
| `$_SESSION` | Server-side session storage | Retain logged in user state |
| `$_SERVER` | Web server environment variables | Check request methods, server headers |

### Example Code
How to define a simple class with properties in PHP:
```php
<?php
class User {
    public $name;
    
    public function __construct($name) {
        $this->name = $name;
    }
    
    public function greet() {
        return "Hello, " . $this->name;
    }
}

$user = new User("Gemini");
echo $user->greet();
?>
```
""",
                "quizzes": [
                    {
                        "title": "PHP Web Scripting Quiz",
                        "description": "Verify your understanding of PHP arrays, variables, and web forms.",
                        "time_limit": 15,
                        "questions": [
                            {
                                "question": "Which character must all variable names start with in PHP?",
                                "a": "@", "b": "&", "c": "$", "d": "#",
                                "correct": "C", "points": 1, "hint": "Think about currencies.",
                                "explanation": "All variables in PHP are prefixed with a dollar sign ($)."
                            },
                            {
                                "question": "Which PHP superglobal is used to collect form data submitted via HTTP POST requests?",
                                "a": "$_GET", "b": "$_POST", "c": "$_SERVER", "d": "$_REQUEST",
                                "correct": "B", "points": 1, "hint": "Matches the request method name.",
                                "explanation": "$_POST collects parameters sent in the HTTP request body."
                            }
                        ]
                    }
                ],
                "challenges": [
                    {
                        "title": "String Length Counter",
                        "description": "Write a PHP script to read a line from stdin and print the length of the string to stdout.",
                        "difficulty": "Easy",
                        "time_limit": 5,
                        "memory_limit": 256,
                        "template": "<?php\n$line = trim(fgets(STDIN));\necho strlen($line);\n?>",
                        "testcases": [
                            {"input": "php", "output": "3", "hidden": False},
                            {"input": "hello world", "output": "11", "hidden": False},
                            {"input": "webdev", "output": "6", "hidden": True}
                        ]
                    }
                ],
                "daily": {
                    "quiz": {
                        "title": "PHP Daily Quiz",
                        "description": "Variables and loops in PHP.",
                        "time_limit": 10,
                        "questions": [
                            {
                                "question": "What is the correct way to concatenate two strings in PHP?",
                                "a": "+ operator", "b": ". operator", "c": "concat() function", "d": "strcat() function",
                                "correct": "B", "points": 2, "hint": "It is a dot character.",
                                "explanation": "The dot (.) operator is used for string concatenation in PHP."
                            }
                        ]
                    },
                    "challenge": {
                        "title": "Double value",
                        "description": "Read an integer from stdin and print double its value.",
                        "difficulty": "Easy",
                        "time_limit": 5,
                        "memory_limit": 256,
                        "template": "<?php\n$val = intval(trim(fgets(STDIN)));\necho $val * 2;\n?>",
                        "testcases": [
                            {"input": "5", "output": "10", "hidden": False},
                            {"input": "-2", "output": "-4", "hidden": False},
                            {"input": "100", "output": "200", "hidden": True}
                        ]
                    }
                }
            },
            "C": {
                "theory": """# C Programming Language

C is a procedural programming language. It was initially developed by Dennis Ritchie in the year 1972 at Bell Labs.

## Core Properties
* **Low-Level Access**: Directly access system memory using pointer variables.
* **Static compilation**: Code is compiled directly into machine architecture machine binary.
* **No garbage collection**: Programmers must manage memory manually using `malloc` and `free`.

### C Storage Classes Comparison

| Storage Class | Scope | Lifetime | Initial Value |
| --- | --- | --- | --- |
| `auto` | Local | Function Block | Garbage |
| `register` | Local | Function Block (in CPU register) | Garbage |
| `static` | Local / Global | Program execution lifespan | Zero |
| `extern` | Global | Program execution lifespan | Zero |

### Example Code
A simple program showing memory allocation in C:
```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    int *ptr = (int*) malloc(sizeof(int));
    if (ptr != NULL) {
        *ptr = 42;
        printf("Value: %d\\n", *ptr);
        // Free allocated memory
        free(ptr);
    }
    return 0;
}
```
""",
                "quizzes": [
                    {
                        "title": "C Syntax & Memory Quiz",
                        "description": "Test your low-level memory allocation and pointer syntax knowledge.",
                        "time_limit": 20,
                        "questions": [
                            {
                                "question": "Which function in C is used to dynamically allocate memory?",
                                "a": "free()", "b": "malloc()", "c": "alloc()", "d": "new",
                                "correct": "B", "points": 2, "hint": "Short for memory allocation.",
                                "explanation": "malloc() allocates a requested size of bytes and returns a void pointer."
                            },
                            {
                                "question": "What does a pointer variable in C store?",
                                "a": "Value of another variable", "b": "Memory address of another variable", "c": "Data type name", "d": "Compiler settings",
                                "correct": "B", "points": 1, "hint": "It points to a location in memory.",
                                "explanation": "A pointer variable holds the memory address of another variable."
                            }
                        ]
                    }
                ],
                "challenges": [
                    {
                        "title": "Factorial",
                        "description": "Write a C program to calculate the factorial of an integer from stdin and print the integer result.",
                        "difficulty": "Medium",
                        "time_limit": 5,
                        "memory_limit": 256,
                        "template": "#include <stdio.h>\n\nint main() {\n    int n;\n    if (scanf(\"%d\", &n) == 1) {\n        long long fact = 1;\n        for (int i = 1; i <= n; i++) {\n            fact *= i;\n        }\n        printf(\"%lld\", fact);\n    }\n    return 0;\n}",
                        "testcases": [
                            {"input": "5", "output": "120", "hidden": False},
                            {"input": "3", "output": "6", "hidden": False},
                            {"input": "0", "output": "1", "hidden": True}
                        ]
                    }
                ],
                "daily": {
                    "quiz": {
                        "title": "C Daily Quiz",
                        "description": "Pointer arithmetic and operations.",
                        "time_limit": 10,
                        "questions": [
                            {
                                "question": "Which operator is used to retrieve the address of a variable in C?",
                                "a": "*", "b": "&", "c": "->", "d": ".",
                                "correct": "B", "points": 2, "hint": "The ampersand character.",
                                "explanation": "The ampersand (&) operator yields the address of its operand."
                            }
                        ]
                    },
                    "challenge": {
                        "title": "Even or Odd",
                        "description": "Read an integer from stdin. Print 'even' if it is even, and 'odd' if it is odd.",
                        "difficulty": "Easy",
                        "time_limit": 5,
                        "memory_limit": 256,
                        "template": "#include <stdio.h>\n\nint main() {\n    int val;\n    if (scanf(\"%d\", &val) == 1) {\n        if (val % 2 == 0) printf(\"even\");\n        else printf(\"odd\");\n    }\n    return 0;\n}",
                        "testcases": [
                            {"input": "4", "output": "even", "hidden": False},
                            {"input": "7", "output": "odd", "hidden": False},
                            {"input": "0", "output": "even", "hidden": True}
                        ]
                    }
                }
            },
            "C++": {
                "theory": """# C++ Programming Language

C++ is a cross-platform language that can be used to create high-performance applications. It was created by Bjarne Stroustrup as an extension of the C language.

## Key Features
* **Classes and Objects**: Rich OOP support built on top of standard C.
* **Standard Template Library (STL)**: Ready-made template classes for vectors, stacks, queues, and maps.
* **References**: Alias pointers with cleaner syntax.

### C++ STL Containers Comparison

| Container | Internal Structure | Search Complexity | Insertion Complexity |
| --- | --- | --- | --- |
| `std::vector` | Dynamic Array | O(1) random access | O(1) amortized end insertions |
| `std::list` | Doubly Linked List | O(N) | O(1) at known iterator position |
| `std::set` | Red-black tree | O(log N) | O(log N) |
| `std::unordered_map` | Hash Table | O(1) average | O(1) average |

### Example Code
Defining an inheritance tree in C++:
```cpp
#include <iostream>
using namespace std;

class Animal {
public:
    virtual void speak() {
        cout << "Animal sound" << endl;
    }
};

class Dog : public Animal {
public:
    void speak() override {
        cout << "Woof!" << endl;
    }
};

int main() {
    Animal* a = new Dog();
    a->speak(); // Outputs: Woof!
    delete a;
    return 0;
}
```
""",
                "quizzes": [
                    {
                        "title": "C++ STL & References Quiz",
                        "description": "Check your STL vectors, lists, and OOP polymorphism understanding.",
                        "time_limit": 20,
                        "questions": [
                            {
                                "question": "What is the average search complexity of std::unordered_map in C++?",
                                "a": "O(N)", "b": "O(log N)", "c": "O(1)", "d": "O(N log N)",
                                "correct": "C", "points": 2, "hint": "Hash tables have constant average search time.",
                                "explanation": "An unordered_map uses hash tables internally, giving constant O(1) search time on average."
                            },
                            {
                                "question": "Which keyword in C++ is used to declare that a function can be overridden in derived classes?",
                                "a": "override", "b": "virtual", "c": "abstract", "d": "static",
                                "correct": "B", "points": 1, "hint": "Begins with 'v'.",
                                "explanation": "The virtual keyword in a base class declaration specifies that a function behaves polymorphically when overridden."
                            }
                        ]
                    }
                ],
                "challenges": [
                    {
                        "title": "Vector Sum",
                        "description": "Write a C++ program to read N integers from stdin and print their sum to stdout.",
                        "difficulty": "Easy",
                        "time_limit": 5,
                        "memory_limit": 256,
                        "template": "#include <iostream>\n#include <vector>\n#include <numeric>\n\nusing namespace std;\n\nint main() {\n    int n;\n    if (cin >> n) {\n        vector<int> v(n);\n        for (int i = 0; i < n; i++) {\n            cin >> v[i];\n        }\n        int sum = accumulate(v.begin(), v.end(), 0);\n        cout << sum;\n    }\n    return 0;\n}",
                        "testcases": [
                            {"input": "3 10 20 30", "output": "60", "hidden": False},
                            {"input": "2 -5 5", "output": "0", "hidden": False},
                            {"input": "5 1 2 3 4 5", "output": "15", "hidden": True}
                        ]
                    }
                ],
                "daily": {
                    "quiz": {
                        "title": "C++ Daily Quiz",
                        "description": "Daily C++ keywords review.",
                        "time_limit": 10,
                        "questions": [
                            {
                                "question": "Which C++ operator is used to dynamically allocate memory on the heap?",
                                "a": "malloc", "b": "new", "c": "alloc", "d": "heap",
                                "correct": "B", "points": 2, "hint": "Often paired with the 'delete' keyword.",
                                "explanation": "The 'new' operator allocates heap memory in C++ and calls constructors."
                            }
                        ]
                    },
                    "challenge": {
                        "title": "Maximum of two",
                        "description": "Read two integers from stdin. Print the larger value to stdout.",
                        "difficulty": "Easy",
                        "time_limit": 5,
                        "memory_limit": 256,
                        "template": "#include <iostream>\n#include <algorithm>\n\nusing namespace std;\n\nint main() {\n    int a, b;\n    if (cin >> a >> b) {\n        cout << max(a, b);\n    }\n    return 0;\n}",
                        "testcases": [
                            {"input": "10 20", "output": "20", "hidden": False},
                            {"input": "-5 -2", "output": "-2", "hidden": False},
                            {"input": "100 100", "output": "100", "hidden": True}
                        ]
                    }
                }
            }
        }

        # Clear existing contents first to prevent duplications
        for sub_name, data in subjects_data.items():
            subject = Subject.query.filter_by(name=sub_name).first()
            if not subject:
                print(f"Subject '{sub_name}' not found. Creating subject first...")
                subject = Subject(name=sub_name, description=f"{sub_name} Programming Curriculum", created_by=admin_id)
                db.session.add(subject)
                db.session.flush()

                # Create 4 chapters
                sections = ['Theory', 'MCQ Part', 'Code Challenges', 'Daily Challenge']
                for sec in sections:
                    chap = Chapter(
                        subject_id=subject.id,
                        name=sec,
                        description=f"{sec} for {sub_name}",
                        theory='',
                        created_by=admin_id
                    )
                    db.session.add(chap)
                db.session.flush()

            # Load the chapters
            chapters = Chapter.query.filter_by(subject_id=subject.id).all()
            chap_by_name = {ch.name: ch for ch in chapters}

            # Double-check chapters are correct
            for key in ['Theory', 'MCQ Part', 'Code Challenges', 'Daily Challenge']:
                if key not in chap_by_name:
                    ch = Chapter(subject_id=subject.id, name=key, description=f"{key} for {sub_name}", theory='', created_by=admin_id)
                    db.session.add(ch)
                    db.session.flush()
                    chap_by_name[key] = ch

            # 1. Update Theory chapter
            theory_chap = chap_by_name['Theory']
            theory_chap.theory = data['theory']

            # Clear existing quizzes, challenges from MCQ Part, Code Challenges, Daily Challenge chapters
            all_chap_ids = [chap_by_name[k].id for k in ['MCQ Part', 'Code Challenges', 'Daily Challenge']]
            
            # Delete questions & quizzes
            quizzes = Quiz.query.filter(Quiz.chapter_id.in_(all_chap_ids)).all()
            for q in quizzes:
                Question.query.filter_by(quiz_id=q.id).delete()
                db.session.delete(q)
            
            # Delete challenges & testcases
            challenges = CodeChallenge.query.filter(CodeChallenge.chapter_id.in_(all_chap_ids)).all()
            for c in challenges:
                TestCase.query.filter_by(challenge_id=c.id).delete()
                ChallengeTemplate.query.filter_by(challenge_id=c.id).delete()
                db.session.delete(c)

            db.session.flush()

            # 2. Add Quizzes to MCQ Part chapter
            mcq_chap = chap_by_name['MCQ Part']
            for q_data in data['quizzes']:
                quiz = Quiz(
                    title=q_data['title'],
                    description=q_data['description'],
                    chapter_id=mcq_chap.id,
                    time_limit=q_data['time_limit'],
                    created_by=admin_id
                )
                db.session.add(quiz)
                db.session.flush()

                for qst in q_data['questions']:
                    question = Question(
                        quiz_id=quiz.id,
                        question=qst['question'],
                        option_a=qst['a'],
                        option_b=qst['b'],
                        option_c=qst['c'],
                        option_d=qst['d'],
                        correct_answer=qst['correct'],
                        points=qst['points'],
                        hint=qst['hint'],
                        explanation=qst['explanation']
                    )
                    db.session.add(question)

            # 3. Add Code Challenges to Code Challenges chapter
            challenges_chap = chap_by_name['Code Challenges']
            for ch_data in data['challenges']:
                cc = CodeChallenge(
                    title=ch_data['title'],
                    description=ch_data['description'],
                    chapter_id=challenges_chap.id,
                    difficulty=ch_data['difficulty'],
                    time_limit=ch_data['time_limit'],
                    memory_limit=ch_data['memory_limit'],
                    created_by=admin_id
                )
                db.session.add(cc)
                db.session.flush()

                # Add template
                lang = sub_name.lower()
                if lang == 'c++':
                    lang = 'cpp'
                tpl = ChallengeTemplate(
                    challenge_id=cc.id,
                    language=lang,
                    template_code=ch_data['template']
                )
                db.session.add(tpl)

                # Add test cases
                for tc in ch_data['testcases']:
                    testcase = TestCase(
                        challenge_id=cc.id,
                        input_data=tc['input'],
                        expected_output=tc['output'],
                        is_hidden=tc['hidden']
                    )
                    db.session.add(testcase)

            # 4. Add Daily Challenges to Daily Challenge chapter
            daily_chap = chap_by_name['Daily Challenge']
            
            # Daily MCQ Quiz
            d_quiz_data = data['daily']['quiz']
            d_quiz = Quiz(
                title=d_quiz_data['title'],
                description=d_quiz_data['description'],
                chapter_id=daily_chap.id,
                time_limit=d_quiz_data['time_limit'],
                created_by=admin_id
            )
            db.session.add(d_quiz)
            db.session.flush()

            for qst in d_quiz_data['questions']:
                question = Question(
                    quiz_id=d_quiz.id,
                    question=qst['question'],
                    option_a=qst['a'],
                    option_b=qst['b'],
                    option_c=qst['c'],
                    option_d=qst['d'],
                    correct_answer=qst['correct'],
                    points=qst['points'],
                    hint=qst['hint'],
                    explanation=qst['explanation']
                )
                db.session.add(question)

            # Daily Code Challenge
            d_ch_data = data['daily']['challenge']
            d_cc = CodeChallenge(
                title=d_ch_data['title'],
                description=d_ch_data['description'],
                chapter_id=daily_chap.id,
                difficulty=d_ch_data['difficulty'],
                time_limit=d_ch_data['time_limit'],
                memory_limit=d_ch_data['memory_limit'],
                created_by=admin_id
            )
            db.session.add(d_cc)
            db.session.flush()

            # Add template
            lang = sub_name.lower()
            if lang == 'c++':
                lang = 'cpp'
            d_tpl = ChallengeTemplate(
                challenge_id=d_cc.id,
                language=lang,
                template_code=d_ch_data['template']
            )
            db.session.add(d_tpl)

            # Add test cases
            for tc in d_ch_data['testcases']:
                d_testcase = TestCase(
                    challenge_id=d_cc.id,
                    input_data=tc['input'],
                    expected_output=tc['output'],
                    is_hidden=tc['hidden']
                )
                db.session.add(d_testcase)

            print(f"Successfully seeded high-quality contents for '{sub_name}' subject.")

        db.session.commit()
        print("All subjects successfully updated and seeded.")

if __name__ == '__main__':
    seed_data()
