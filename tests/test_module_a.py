from tests.conftest import dependency


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
