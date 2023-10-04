from pathlib import Path
import functools
from filehash.filehash import FileHash
from loguru import logger

def calculate_folder_code_hash(path: Path, target_hash_string: str):
    hasher = FileHash('sha1')
    files: list[Path] = [file for file in path.rglob('*.py')]
    hash_list: list[int] = [int(result.hash, 16) for result in hasher.hash_files(files)]
    hash_string: str = hex(functools.reduce(lambda x, y: x ^ y, hash_list))
    logger.info(f'{hash_string=}')
    if hash_string != target_hash_string:
        logger.error('Hash sum incorrect')
        return False
    else:
        logger.success('Hash sum OK')
        return True


if __name__ == '__main__':
    calculate_folder_code_hash(Path('./smef'), '0xab34fdd76ee0f4f0ac7bc06624d5456623ba4af6')

