from pathlib import Path
import os


def pyinstaller() -> None:
    icon: str = f"--icon {Path(__file__).parent.joinpath('icon', 'engeneering.ico')}"
    flags: list[str] = ["--name СМЭП_Клиент", "--console", "--onefile",
                        "--clean", "--noconfirm"]
    main_path: str = str(Path(__file__).parent.joinpath('__main__.py'))
    smef: str = f"--add-data \"{Path(__file__).parent};smef\""
    destination: str = f"--distpath {Path.cwd()}"
    to_exe_cmd: str = ' '.join(["pyinstaller", main_path,
                                *flags,
                                destination,
                                icon,
                                smef
                                ])
    os.system(to_exe_cmd)
    for flag in to_exe_cmd.split('--'):
        print(f'--{flag}')


if __name__ == '__main__':
    pyinstaller()

    # print(cwd())