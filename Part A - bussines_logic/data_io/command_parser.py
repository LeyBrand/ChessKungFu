def parse_commands(commands_text):
    commands = []
    for line in commands_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
            
        parts = line.split()
        cmd_name = parts[0]
        args = parts[1:]
        
        command = {
            "name": cmd_name,
            "args": args
        }
        commands.append(command)
    return commands