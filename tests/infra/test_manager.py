import pytest
from smartutils.infra.manager import ContextResourceManager


def test_context_var_name_unique():
    mgr1 = ContextResourceManager({}, "my_var")
    with pytest.raises(ValueError):
        ContextResourceManager({}, "my_var")
