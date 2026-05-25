with open('/app/app/services/mes/exporter.py', 'r') as f:
    content = f.read()

# Fix line 192
old_line = "        if not project_set_result['success'] or not project_set_result['finalValue'] not in project:"
new_line = "        if not project_set_result['success'] or project not in project_set_result['finalValue']:"

content = content.replace(old_line, new_line)

with open('/app/app/services/mes/exporter.py', 'w') as f:
    f.write(content)

print("Fixed line 192")
