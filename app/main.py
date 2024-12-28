import sys
import os
import subprocess
import shlex
import math
import shutil
from collections import defaultdict



# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def find_executable(command, path):
    directories = path.split(':')
    for directory in directories:
        file_path = os.path.join(directory, command)
        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
            return file_path
    return None

def execute_command(command, args, output_file=None, error_file=None, append_stdout=False, append_stderr=False):
    try:
        stdout = open(output_file, 'a' if append_stdout else 'w') if output_file else subprocess.PIPE
        stderr = open(error_file, 'a' if append_stderr else 'w') if error_file else subprocess.PIPE
        
        result = subprocess.run([command] + args, stdout=stdout, stderr=stderr, text=True)
        
        if output_file:
            stdout.close()
        else:
            print(result.stdout, end='')
        
        if error_file:
            stderr.close()
        else:
            print(result.stderr, end='', file=sys.stderr)
    except Exception as e:
        print(f"Error executing {command}: {str(e)}", file=sys.stderr)

def format_in_columns(items, term_width=80, color=RESET):
    if not items:
        return ""

    # Get the maximum length of any item
    max_len = max(len(item) for item in items)
    
    # Calculate the number of columns
    num_columns = max(1, term_width // (max_len + 2))
    
    # Calculate the number of rows
    num_rows = math.ceil(len(items) / num_columns)
    
    # Pad the list to fill the grid
    items = items + [''] * (num_rows * num_columns - len(items))
    
    # Create columns with color and bold
    columns = defaultdict(list)
    for i, item in enumerate(items):
        columns[i % num_columns].append(f"{BOLD}{color}{item.ljust(max_len)}{RESET}")
    
    # Join columns and rows
    return '\n'.join(' '.join(row) for row in zip(*columns.values()))

def display_welcome_message():
    terminal_width = shutil.get_terminal_size().columns

    welcome_msg = "WELCOME TO"
    boss_shell = """
    ██████╗  ██████╗ ███████╗███████╗    ███████╗██╗  ██╗███████╗██╗     ██╗     
    ██╔══██╗██╔═══██╗██╔════╝██╔════╝    ██╔════╝██║  ██║██╔════╝██║     ██║     
    ██████╔╝██║   ██║███████╗███████╗    ███████╗███████║█████╗  ██║     ██║     
    ██╔══██╗██║   ██║╚════██║╚════██║    ╚════██║██╔══██║██╔══╝  ██║     ██║     
    ██████╔╝╚██████╔╝███████║███████║    ███████║██║  ██║███████╗███████╗███████╗
    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝    ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
    """

    print(f"\n{BOLD}{CYAN}")
    print(welcome_msg.center(terminal_width))

    boss_shell_art = f"""
  {boss_shell}
"""

    for line in boss_shell_art.split('\n'):
        print(line.center(terminal_width))

    print(f"{RESET}\n" + "=" * terminal_width + "\n")


def main():
    valid_commands = ["exit", "echo", "type", "pwd", "cd"]
    path = os.environ.get('PATH', '')
    
    display_welcome_message()  # Add this line

    
    while True:
        # sys.stdout.write("$ ")
        sys.stdout.write(f"{GREEN}$ {RESET}")
        sys.stdout.flush()

        command = input().strip()
        args = shlex.split(command)
        
        if not args:
            continue
        
        # Check for output and error redirection
        output_file = None
        error_file = None
        append_stdout = False
        append_stderr = False
        
        if '>>' in args or '1>>' in args:
            redirect_index = args.index('>>') if '>>' in args else args.index('1>>')
            output_file = args[redirect_index + 1]
            args = args[:redirect_index] + args[redirect_index + 2:]
            append_stdout = True
        elif '>' in args or '1>' in args:
            redirect_index = args.index('>') if '>' in args else args.index('1>')
            output_file = args[redirect_index + 1]
            args = args[:redirect_index] + args[redirect_index + 2:]
        
        if '2>>' in args:
            redirect_index = args.index('2>>')
            error_file = args[redirect_index + 1]
            args = args[:redirect_index] + args[redirect_index + 2:]
            append_stderr = True
        elif '2>' in args:
            redirect_index = args.index('2>')
            error_file = args[redirect_index + 1]
            args = args[:redirect_index] + args[redirect_index + 2:]
        
        # Redirect stdout and stderr if necessary
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        if output_file:
            sys.stdout = open(output_file, 'a' if append_stdout else 'w')
        if error_file:
            sys.stderr = open(error_file, 'a' if append_stderr else 'w')
        
        try:
            # Handle exit command
            if args[0] == "exit":
                if len(args) > 1 and args[1] == "0":
                    # print("------------------------")
                    sys.exit(0)
                else:
                    print("exit: expected numeric argument", file=sys.stderr)
                    # print("------------------------")
                    
            # Handle echo command
            elif args[0] == "echo":
                print(" ".join(args[1:]))
                # print("------------------------")
            
            # Handle type command
            elif args[0] == "type":
                if len(args) == 2:
                    if args[1] in valid_commands:
                        print(f"{args[1]} is a shell builtin")
                        # print("------------------------")
                    else:
                        executable_path = find_executable(args[1], path)
                        if executable_path:
                            print(f"{args[1]} is {executable_path}")
                            # print("------------------------")
                        else:
                            print(f"{args[1]}: not found", file=sys.stderr)
                            # print("------------------------")
                else:
                    print("type: expected a command", file=sys.stderr)
                    # print("------------------------")
                    
            # Handle pwd command       
            elif args[0] == "pwd":
                sys.stdout.write(f"{BLUE}{os.getcwd()}{RESET}\n")
                sys.stdout.flush()
                # print("------------------------")
                
            # Handle cd command
            elif args[0] == "cd":
                if len(args) != 2:
                    print("cd: expected 1 argument", file=sys.stderr)
                    # print("------------------------")
                else:
                    target_dir = args[1]
                    if target_dir == "~":
                        target_dir = os.environ.get('HOME', '')
                    try:
                        os.chdir(target_dir)
                        # print("------------------------")
                    except FileNotFoundError:
                        print(f"cd: {args[1]}: No such file or directory", file=sys.stderr)
                        # print("------------------------")
                        
            # Handle ls command
            elif args[0] == "ls":
                try:
                    directory = args[1] if len(args) > 1 else '.'
                    items = sorted(os.listdir(directory))
                    print(format_in_columns(items, color=CYAN))
                    # print("------------------------")
                except FileNotFoundError:
                    print(f"ls: {directory}: No such file or directory", file=sys.stderr)
                    # print("------------------------")
                except PermissionError:
                    print(f"ls: {directory}: Permission denied", file=sys.stderr)
                    # print("------------------------")

            # Handle program exe command or command not found
            else:
                executable_path = find_executable(args[0], path)
                if executable_path:
                    execute_command(executable_path, args[1:], output_file, error_file, append_stdout, append_stderr)
                    # print("------------------------")
                    
                else:
                    print(f"{args[0]}: command not found", file=sys.stderr)
                    # print("------------------------")
        
        finally:
            # Restore original stdout and stderr
            if output_file:
                sys.stdout.close()
                sys.stdout = original_stdout
            if error_file:
                sys.stderr.close()
                sys.stderr = original_stderr

if __name__ == "__main__":
    main()
