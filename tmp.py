import difflib


def text_diff(old: str, new: str) -> str:
    """Generate a diff between old and new."""
    old_list = old.splitlines(keepends=True)
    new_list = new.splitlines(keepends=True)

    return "".join(difflib.ndiff(old_list, new_list))


def conversion_instructions(old: str, new: str) -> str:
    """Generate a list of instructions for converting from old to new."""
    out = ""

    old_list = old.splitlines(keepends=True)
    new_list = new.splitlines(keepends=True)

    diff = difflib.ndiff(old_list, new_list)

    for i, s in enumerate(diff):
        if s[0] == " ":
            continue

        if s[0] == "-":
            out += f'Delete "{s[2:]}" from position {i}.'
        elif s[0] == "+":
            out += f'Add "{s[2:]}" to position {i}.'

    return out


a = "ac\nd"
c = "bc\nd"

print(text_diff(a, c))
