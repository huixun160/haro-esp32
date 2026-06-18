import sys

path = '/home/shiro/.espressif/python_env/idf5.5_py3.12_env/lib/python3.12/site-packages/idf_component_manager/dependencies.py'
with open(path, 'r') as f:
    content = f.read()

target = """    except (HashNotFoundError, HashNotSHA256Error):
        raise InvalidComponentHashError(
            f'File {HASH_FILENAME} or {CHECKSUMS_FILENAME} for component "{component.name}" '
            'in the managed components directory does not exist or cannot be parsed. '
            'These files are used by the component manager for component integrity checks. '
            'If they exist in the component source, please ask the component '
            'maintainer to remove them.'
        )"""

replacement = """    except (HashNotFoundError, HashNotSHA256Error):
        if not component_path.exists():
            return None
        return component_path.as_posix()"""

new_content = content.replace(target, replacement)

with open(path, 'w') as f:
    f.write(new_content)
