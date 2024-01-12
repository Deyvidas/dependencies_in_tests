from tests.conftest import dependency


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
