class Command:
    def __init__(self, cmd_id, command, arguments):
        self.id = cmd_id
        self.command = command
        self.arguments = arguments

    def __str__(self):
        return f'{str(self.id) + " " if self.id is not None else ""}{self.command} {" ".join(self.arguments)}'

    @staticmethod
    def parse(string):
        components = string.split()

        if components[0].isdigit():
            cmd_id = int(components[0])
            components = components[1:]
        else:
            cmd_id = None

        return Command(cmd_id, components[0], components[1:])


class Response:
    def __init__(self, success, response_id, result):
        self.success = success
        self.id = response_id
        self.result = result

    def __str__(self):
        return f'{"=" if self.success else "?"}{self.id if self.id is not None else ""} {self.result}'

    @staticmethod
    def parse(string):
        components = string.split(maxsplit=1)

        status_chr = components[0][0]
        id_str = components[0][1:]

        if status_chr == '=':
            success = True
        elif status_chr == '?':
            success = False
        else:
            assert False

        if id_str.isdigit():
            response_id = int(id_str)
        else:
            response_id = None

        return Response(success, response_id, components[1])
