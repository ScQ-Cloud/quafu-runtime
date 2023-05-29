class RuntimeProgram:
    """Class for represent a program."""
    def __init__(self, program_id: str):
        self.program_id = program_id
        self.name = None
        self.is_public = None
        self.backend = None
        self.description = None
        self.data = None
        self.max_cost_time = None

    def update(self, program: dict):
        if 'program_id' in program:
            self.program_id = program['program_id']
        if 'data' in program:
            # response['data'] = from_base64_string(response['data']).decode("utf-8")
            self.data = program['data']
        if 'description' in program:
            self.description = program['description']
        if 'name' in program:
            self.name = program['name']
        if 'is_public' in program:
            self.is_public = program['is_public']
        if 'backend' in program:
            self.backend = program['backend']
        if 'cost' in program:
            self.max_cost_time = program['cost']

    def __str__(self):
        return f"<Program id:{self.program_id}, name:{self.name}\n" \
               f"is_public:{self.is_public}, backend:{self.backend}\n" \
               f"description:{self.description}, max_cost_time:{self.max_cost_time}\n" \
               f"data:\n{self.data}>"


