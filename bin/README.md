


# Python style guide

https://google.github.io/styleguide/pyguide.html#3164-guidelines-derived-from-guidos-recommendations

3.16 Naming

module_name, package_name, ClassName, method_name, ExceptionName, function_name, GLOBAL_CONSTANT_NAME, global_var_name, instance_var_name, function_parameter_name, local_var_name, query_proper_noun_for_thing, send_acronym_via_https.

Function names, variable names, and filenames should be descriptive; avoid abbreviation. In particular, do not use abbreviations that are ambiguous or unfamiliar to readers outside your project, and do not abbreviate by deleting letters within a word.

Always use a .py filename extension. Never use dashes.

3.16.1 Names to Avoid

    single character names, except for specifically allowed cases:
        counters or iterators (e.g. i, j, k, v, et al.)
        e as an exception identifier in try/except statements.
        f as a file handle in with statements
        private type variables with no constraints (e.g. _T = TypeVar("_T"), _P = ParamSpec("_P"))

    Please be mindful not to abuse single-character naming. Generally speaking, descriptiveness should be proportional to the name’s scope of visibility. For example, i might be a fine name for 5-line code block but within multiple nested scopes, it is likely too vague.

    dashes (-) in any package/module name

    __double_leading_and_trailing_underscore__ names (reserved by Python)

    offensive terms

    names that needlessly include the type of the variable (for example: id_to_name_dict)

3.16.2 Naming Conventions

    “Internal” means internal to a module, or protected or private within a class.

    Prepending a single underscore (_) has some support for protecting module variables and functions (linters will flag protected member access). Note that it is okay for unit tests to access protected constants from the modules under test.

    Prepending a double underscore (__ aka “dunder”) to an instance variable or method effectively makes the variable or method private to its class (using name mangling); we discourage its use as it impacts readability and testability, and isn’t really private. Prefer a single underscore.

    Place related classes and top-level functions together in a module. Unlike Java, there is no need to limit yourself to one class per module.

    Use CapWords for class names, but lower_with_under.py for module names. Although there are some old modules named CapWords.py, this is now discouraged because it’s confusing when the module happens to be named after a class. (“wait – did I write import StringIO or from StringIO import StringIO?”)

    New unit test files follow PEP 8 compliant lower_with_under method names, for example, test_<method_under_test>_<state>. For consistency(*) with legacy modules that follow CapWords function names, underscores may appear in method names starting with test to separate logical components of the name. One possible pattern is test<MethodUnderTest>_<state>.

3.16.3 File Naming

Python filenames must have a .py extension and must not contain dashes (-). This allows them to be imported and unittested. If you want an executable to be accessible without the extension, use a symbolic link or a simple bash wrapper containing exec "$0.py" "$@".

3.16.4 Guidelines derived from Guido’s Recommendations
Type 	Public 	Internal
Packages 	lower_with_under
Modules 	lower_with_under 	_lower_with_under
Classes 	CapWords 	_CapWords
Exceptions 	CapWords
Functions 	lower_with_under() 	_lower_with_under()
Global/Class Constants 	CAPS_WITH_UNDER 	_CAPS_WITH_UNDER
Global/Class Variables 	lower_with_under 	_lower_with_under
Instance Variables 	lower_with_under 	_lower_with_under (protected)
Method Names 	lower_with_under() 	_lower_with_under() (protected)
Function/Method Parameters 	lower_with_under
Local Variables 	lower_with_under

