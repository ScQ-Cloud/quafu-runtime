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

    def __str__(self):
        return f"<Program id:{self.program_id}, name:{self.name}\n" \
               f"is_public:{self.is_public}, backend:{self.backend}\n" \
               f"description:{self.description}, max_cost_time:{self.max_cost_time}\n" \
               f"data:{self.data}>"


