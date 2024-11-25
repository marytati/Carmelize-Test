from pydantic import BaseModel

def camelize(s: str) -> str:
    """
    Converts a snake_case string to camelCase.
    """
    parts = s.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

class Schema(BaseModel):
    class Config:
        alias_generator = camelize
        populate_by_name = True  # Pydantic will use the camelize function to automatically change field names to camelCase when it outputs data.
