from dependencies.user import get_user_id
from uuid import uuid4


def test_get_user_id_valid():
    user_id = str(uuid4())
    result = get_user_id(x_user_id=user_id)
    assert str(result) == user_id
