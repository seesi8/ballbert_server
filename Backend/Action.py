from typing import Self


class Parameter:
    def __init__(self, id: str, type: str, description: str, required: bool) -> None:
        self.id = id
        self.type = type
        self.description = description
        self.required = required

    def __repr__(self) -> str:
        return f"id: {self.id}, type: {self.type}, description: {self.description}, required: {self.required}"

    def to_dict(self) -> dict:
        data = {
            "type": self.type,
            "description": self.description,
            "required": self.required,
        }

        return self.id, data

    @classmethod
    def from_dict(cls, id, data) -> Self:
        required_fields = ["type", "description", "required"]

        for field in required_fields:
            if field not in data:
                raise Exception("Incorrect Fields")

        parameter = cls(id, data["type"], data["description"], data["required"])

        return parameter

    def __eq__(self, __value: object) -> bool:
        if type(__value) != type(self):
            return False

        id_same = self.id == __value.id
        type_same = self.type == __value.type
        description_same = self.description == __value.description
        required_same = self.required == __value.required

        return id_same and type_same and description_same and required_same


class Action:
    def __init__(
        self, id: str, name: str, skill: str, parameters: list[Parameter], description
    ) -> None:
        self.id = id
        self.name = name
        self.skill = skill
        self.parameters = parameters
        self.description = description

    def __repr__(self) -> str:
        return f"id: {self.id}, name: {self.name}, skill: {self.skill}, parameters: {str(self.parameters)}"

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "skill": self.skill,
            "parameters": {
                param.to_dict()[0]: param.to_dict()[1] for param in self.parameters
            },
            "description": self.description,
        }

        return data

    @classmethod
    def from_dict(cls, data) -> Self:
        required_fields = ["id", "name", "skill", "parameters", "description"]

        for field in required_fields:
            if field not in data:
                raise Exception("Incorrect Fields")

        action = cls(
            data["id"],
            data["name"],
            data["skill"],
            [
                Parameter.from_dict(id, param)
                for id, param in data["parameters"].items()
            ],
            data["description"],
        )

        return action

    def __eq__(self, __value: object) -> bool:
        if type(__value) != type(self):
            return False

        id_same = self.id == __value.id
        name_same = self.name == __value.name
        skill_same = self.skill == __value.skill
        parameters_same = self.parameters == __value.parameters
        description_same = self.description == __value.description

        return (
            id_same
            and name_same
            and skill_same
            and parameters_same
            and description_same
        )
