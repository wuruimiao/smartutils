import pytest
from pydantic import ValidationError

from smartutils.config.schema.project import ProjectConf


@pytest.mark.parametrize(
    "name, description, version",
    [
        ("unmanned", "无人柜审核", "0.0.1"),
        ("auth", "权限", "0.0.2"),
    ]
)
def test_project_conf_valid(name, description, version):
    conf = ProjectConf(name=name, description=description, version=version)
    assert conf.name == name
    assert conf.description == description
    assert conf.version == version


@pytest.mark.parametrize(
    "name, description, version",
    [
        ("unmanned", "", " "),
        ("", "无人柜", None),
        ("   ", " ", "   "),
        (1, 2, 3),
        (None, None, None),
    ]
)
def test_project_conf_invalid(name, description, version):
    with pytest.raises(ValidationError) as exc:
        ProjectConf(name=name, description=description, version=version)
    assert ('Input should be a valid string' in str(exc.value)
            or 'String should have at least 1 character' in str(exc.value))
