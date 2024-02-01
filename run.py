import os
import subprocess
import platform
import sys
from enum import Enum
from secret import secrets_dict


class Platform(Enum):
    NULL = 0,
    WINDOWS = 1,
    UNIX = 2


def run():
    venv_path = ""
    match platform.system():
        case 'Windows':
            os_type = Platform.WINDOWS
        case 'Darwin':  # Mac
            os_type = Platform.UNIX
        case 'Linux':
            os_type = Platform.UNIX
        case _:
            os_type = Platform.NULL
    os.chdir(os.path.dirname(os.path.realpath(__file__)))  # changes cwd to script directory
    for path in ['env', 'venv', '.env', '.venv']:
        if os.path.exists(os.path.join(".", path)):
            venv_path = os.path.join(".", path)
            break
    if os_type == Platform.NULL:
        print("Invalid platform. Platform detected: " + platform.system())
        exit(1)
    if venv_path != "":
        if os_type == Platform.UNIX:
            subprocess.run(["source", os.path.join(venv_path, "bin", "activate")])
        elif os_type == Platform.WINDOWS:
            this_file = os.path.join(venv_path, 'Scripts', 'activate_this.py')
            exec(open(this_file).read(), {'__file__': this_file})
    for secret in secrets_dict:
        os.environ[secret['name']] = secret['val']
    commands = ["account_unsetmultipleprimaryemails", "changepassword", "createsuperuser", "remove_stale_contenttypes",
                "check", "compilemessages", "createcachetable", "dbshell", "diffsettings", "dumpdata", "flush",
                "inspectdb", "loaddata", "makemessages", "makemigrations", "migrate", "optimizemigration",
                "sendtestemail", "shell", "showmigrations", "sqlflush", "sqlmigrate", "sqlsequencereset",
                "squashmigrations", "startapp", "startproject", "test", "testserver", "runserver", "clearsessions",
                "collectstatic", "findstatic"]
    args = sys.argv
    if len(args) < 2:
        args.append("help")
    for i in range(len(args)):
        command_collection = ["python", "manage.py", args[i]]
        if args[i] == "help":
            if len(args) > i + 1:
                if args[i + 1] in commands + ["--django", "-dj", "-d"]:
                    if args[i + 1] in commands:
                        command_collection.append(args[i + 1])
                    i += 1
                    subprocess.run(command_collection, shell=True)
                    continue
            print("\nrun.py is a flexible program designed to make it easy to run your django server.\n\n" +
                  "Usage:\n"
                  "\trun.py [manage.py subcommand [arguments]] [manage.py subcommand [arguments]] ...\n\n"
                  "Example:\n\t run.py makemigrations migrate test runserver localhost:8000\n"
                  "\t This command will make migrations, migrate, test, and run the server on port 8000, in that order"
                  "\n\nOptional arguments:\n\t--django, -dj, -d        Displays 'manage.py help'\n"
                  "\t[manage.py subcommand]   Displays 'manage.py help [subcommand]'. Example: 'run.py help test'\n")
        elif args[i] in commands:
            j = i + 1
            while j < len(args) and args[j] not in commands:
                command_collection.append(args[j])
                j += 1
            print(f"--- Running {args[i]}" +
                  (" with arguments: " + str(command_collection[3:]) if len(command_collection) > 3 else "")
                  + "---------------------")
            try:
                subprocess.run(command_collection, shell=True)
            except KeyboardInterrupt as e:
                print('Closed process.')
                sys.exit(e)


if __name__ == '__main__':
    run()
