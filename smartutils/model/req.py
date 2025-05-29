from pydantic import BaseModel


def explicit_nonnull_fields(model: BaseModel) -> dict:
    try:
        # Pydantic 2
        data = model.model_dump(exclude_unset=True)
    except AttributeError:
        # Pydantic 1
        data = model.dict(exclude_unset=True)
    return {k: v for k, v in data.items() if v is not None}
