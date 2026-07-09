def  parse(commands_text):
    commands = []
    for line in commands_text.strip().splitlines():
        parts = line.split()
        if line:
            commands.append(line)
    return commands