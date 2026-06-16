import os

file_path = "/home/ubuntu/AM4user/analysis/lifecycle.py"
with open(file_path, 'r') as f:
    lines = f.readlines()

# Line numbers are 1-indexed, so line 91 is index 90 (0-indexed)
line_index = 90  # because line 1 is index 0
if line_index < len(lines):
    old_line = lines[line_index]
    print("Old line:", repr(old_line))
    # Replace the line
    new_line = '        raise ValueError(f"Route not found.\\nAircraft: {ac[\\'name\\']}\\nOrigin: {ori[\\'iata\\']}\\nDestination: {dest[\\'iata\\']}\\n\\nPossible reasons:\\n• Route does not exist in dataset\\n• Aircraft shortname mismatch\\n• Airport code mismatch")\n'
    lines[line_index] = new_line
    with open(file_path, 'w') as f:
        f.writelines(lines)
    print("Successfully updated the error message.")
else:
    print(f"Line index {line_index} is out of range. The file has {len(lines)} lines.")