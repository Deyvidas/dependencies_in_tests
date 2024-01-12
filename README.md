- [How does the dependency decorator work](#0)
- [Without arguments](#1)
- [With module scope](#2)
- [When tests depend on tests from other modules.](#3)
- [Dependencies between test classes](#4)

---

<h3 align="center">Decorator dependency()</h3>

It's a custom decorator that union decorators:
- `@pytest.mark.dependency()` - to skip tests if tests in the dependency are SKIPPED or FAILED.
- `@pytest.mark.order()` - to change the order of tests.
- [pytest-dependency documentation](https://pytest-dependency.readthedocs.io/en/stable/index.html#content-of-the-documentation)
- [pytest-order documentation](https://pytest-order.readthedocs.io/en/stable/index.html)

```python
from functools import wraps
from typing import Callable
from typing import Literal
from typing import TypeAlias

import pytest


Scope: TypeAlias = Literal[
    'function',
    'class',
    'module',
    'package',
    'session',
]


def dependency(depends: list[str] = list(), scope: Scope = 'session'):
    def get_func(func: Callable):
        @wraps(func)
        @pytest.mark.dependency(depends=depends, scope=scope)
        @pytest.mark.order(after=depends)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        return wrapper

    return get_func

```

---

<h3 id="0" align="center">How does the dependency decorator work</h3>

```python
# tests/test_module_a.py
@dependency(depends=['test_b'], scope='module')
def test_a():  # ------ 10 ------
    assert True

@dependency(depends=['TestA::test_b'], scope='module')
def test_b():  # ------ 9 ------
    assert True


class TestA:
    @dependency(depends=['test_b'], scope='class')
    def test_a(self):  # ------ 8 ------
        assert True

    @dependency(depends=['TestB::test_c'], scope='module')
    def test_b(self):  # ------ 7 ------
        assert True

    @dependency()
    def test_c(self):  # ------ 1 ------
        assert True


class TestB:
    @dependency()
    def test_a(self):  # ------ 2 ------
        assert True

    @dependency()
    def test_b(self):  # ------ 3 ------
        assert True

    @dependency(
        depends=['tests/test_module_b.py::TestA::test_b'],
        scope='session',
    )
    def test_c(self):  # ------ 6 ------
        assert True
```
```python
class TestA:
    @dependency()
    def test_a(self):  # ------ 4 ------
        assert True

    @dependency()
    def test_b(self):  # ------ 5 ------
        assert True

    @dependency()
    def test_c(self):  # ------ 11 ------
        assert True
```
```sh
collected 11 items

tests/test_module_a.py::TestA::test_c PASSED
tests/test_module_a.py::TestB::test_a PASSED
tests/test_module_a.py::TestB::test_b PASSED
tests/test_module_b.py::TestA::test_a PASSED
tests/test_module_b.py::TestA::test_b PASSED
tests/test_module_a.py::TestB::test_c PASSED
tests/test_module_a.py::TestA::test_b PASSED
tests/test_module_a.py::test_b PASSED
tests/test_module_a.py::test_a PASSED
tests/test_module_a.py::TestA::test_a PASSED
tests/test_module_b.py::TestA::test_c PASSED
```

---

<h3 id="1" align="center">Without arguments</h3>

```python
@dependency()
def test_a():
    assert True

@dependency()
def test_b():
    assert True

@dependency()
def test_c():
    assert True
```
```sh
collected 3 items

tests/test_module_a.py::test_a PASSED
tests/test_module_a.py::test_b PASSED
tests/test_module_a.py::test_c PASSED
```

---

<h3 id="2" align="center">With module scope</h3>

```python
@dependency(depends=['test_b'], scope='module')
def test_a():
    assert True

@dependency(depends=['test_c'], scope='module')
def test_b():
    assert True

@dependency()
def test_c():
    assert True
```
```sh
collected 3 items

tests/test_module_a.py::test_c PASSED
tests/test_module_a.py::test_b PASSED
tests/test_module_a.py::test_a PASSED
```

---

```python
@dependency(depends=['test_b'], scope='module')
def test_a():
    assert True

@dependency(depends=['test_c'], scope='module')
def test_b():
    assert True

@dependency()
def test_c():
    pytest.fail()  # this test FAIL
```
```sh
collected 3 items

tests/test_module_a.py::test_c FAILED
tests/test_module_a.py::test_b SKIPPED (test_b depends on test_c)  # because test_c is FAIL
tests/test_module_a.py::test_a SKIPPED (test_a depends on test_b)  # because test_b is SKIPPED
```

---

```python
@dependency(depends=['test_b'], scope='module')
def test_a():
    assert True

@dependency(depends=['test_c'], scope='module')
def test_b():
    pytest.fail()  # this test FAIL

@dependency()
def test_c():
    assert True
```
```sh
collected 3 items

tests/test_module_a.py::test_c PASSED
tests/test_module_a.py::test_b FAILED
tests/test_module_a.py::test_a SKIPPED (test_a depends on test_b)  # because test_b is FAIL
```

---

<h3 id="3" align="center">When tests depend on tests from other modules.</h3>

```python
# tests/test_module_a.py
@dependency(depends=['test_b'], scope='module')
def test_a():
    assert True

@dependency(depends=['tests/test_module_b.py::test_c'], scope='module')
def test_b():
    assert True

@dependency()
def test_c():
    assert True
```
```python
# tests/test_module_b.py
@dependency()
def test_a():
    assert True

@dependency()
def test_b():
    assert True

@dependency()
def test_c():
    assert True
```
```sh
collected 6 items

tests/test_module_a.py::test_c PASSED
tests/test_module_b.py::test_a PASSED
tests/test_module_b.py::test_b PASSED
tests/test_module_b.py::test_c PASSED
tests/test_module_a.py::test_b SKIPPED (test_b depends on tests/test_module_b.py::test_c)
tests/test_module_a.py::test_a SKIPPED (test_a depends on test_b)
```

---

Если тест зависит от теста в другом модуле мы должны использовать scope='session'
иначе попросту результат теста не будет виден зависящему от него тесту и он
скипнется.

```python
# tests/test_module_a.py
@dependency(depends=['test_b'], scope='module')
def test_a():
    assert True

@dependency(depends=['tests/test_module_b.py::test_c'], scope='session')
def test_b():
    assert True

@dependency()
def test_c():
    assert True
```
```sh
collected 6 items

tests/test_module_a.py::test_c PASSED
tests/test_module_b.py::test_a PASSED
tests/test_module_b.py::test_b PASSED
tests/test_module_b.py::test_c PASSED
tests/test_module_a.py::test_b PASSED
tests/test_module_a.py::test_a PASSED
```

---

<h3 id="4" align="center">Dependencies between test classes</h3>

<h4 align="left">class scope</h3>

```python
class TestA:
    @dependency(depends=['test_b'], scope='class')
    def test_a(self):
        assert True

    @dependency(depends=['test_c'], scope='class')
    def test_b(self):
        assert True

    @dependency()
    def test_c(self):
        assert True


class TestB:
    @dependency()
    def test_a(self):
        assert True

    @dependency()
    def test_b(self):
        assert True

    @dependency()
    def test_c(self):
        assert True
```
```sh
collected 6 items

tests/test_module_a.py::TestA::test_c PASSED
tests/test_module_a.py::TestA::test_b PASSED
tests/test_module_a.py::TestA::test_a PASSED
tests/test_module_a.py::TestB::test_a PASSED
tests/test_module_a.py::TestB::test_b PASSED
tests/test_module_a.py::TestB::test_c PASSED
```

---

<h4 align="left">module scope</h3>

```python
class TestA:
    @dependency(depends=['test_b'], scope='class')
    def test_a(self):
        assert True

    @dependency(depends=['TestB::test_c'], scope='module')
    def test_b(self):
        assert True

    @dependency()
    def test_c(self):
        assert True


class TestB:
    @dependency()
    def test_a(self):
        assert True

    @dependency()
    def test_b(self):
        assert True

    @dependency()
    def test_c(self):
        assert True
```
```sh
collected 6 items

tests/test_module_a.py::TestA::test_c PASSED
tests/test_module_a.py::TestB::test_a PASSED
tests/test_module_a.py::TestB::test_b PASSED
tests/test_module_a.py::TestB::test_c PASSED
tests/test_module_a.py::TestA::test_b PASSED
tests/test_module_a.py::TestA::test_a PASSED
```

---

<h4 align="left">session scope</h3>

```python
# tests/test_module_a.py
class TestA:
    @dependency(depends=['test_b'], scope='class')
    def test_a(self):
        assert True

    @dependency(depends=['TestB::test_c'], scope='module')
    def test_b(self):
        assert True

    @dependency()
    def test_c(self):
        assert True


class TestB:
    @dependency()
    def test_a(self):
        assert True

    @dependency()
    def test_b(self):
        assert True

    @dependency(
        depends=['tests/test_module_b.py::TestA::test_b'],
        scope='session',
    )
    def test_c(self):
        assert True
```
```python
# tests/test_module_b.py
class TestA:
    @dependency()
    def test_a(self):
        assert True

    @dependency()
    def test_b(self):
        assert True

    @dependency()
    def test_c(self):
        assert True
```
```sh
collected 9 items

tests/test_module_a.py::TestA::test_c PASSED
tests/test_module_a.py::TestB::test_a PASSED
tests/test_module_a.py::TestB::test_b PASSED
tests/test_module_b.py::TestA::test_a PASSED
tests/test_module_b.py::TestA::test_b PASSED
tests/test_module_a.py::TestB::test_c PASSED
tests/test_module_a.py::TestA::test_b PASSED
tests/test_module_a.py::TestA::test_a PASSED
tests/test_module_b.py::TestA::test_c PASSED
```
