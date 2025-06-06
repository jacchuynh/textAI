#!/usr/bin/env python3
import re

# Read the parser engine file
with open('/Users/jacc/Downloads/TextRealmsAI/backend/src/text_parser/parser_engine.py', 'r') as f:
    content = f.read()

# Pattern to match tool class definitions with name and description
pattern = r'(class \w+Tool\(BaseTool\):\s*"""[^"]*"""\s*)(name = "[^"]+"\s*description = "[^"]+")' 

def fix_tool_definition(match):
    class_start = match.group(1)
    old_fields = match.group(2)
    
    # Extract name and description values
    name_match = re.search(r'name = "([^"]+)"', old_fields)
    desc_match = re.search(r'description = "([^"]+)"', old_fields)
    
    if name_match and desc_match:
        name_value = name_match.group(1)
        desc_value = desc_match.group(1)
        
        new_fields = f'name: str = "{name_value}"\n    description: str = "{desc_value}"'
        return class_start + new_fields
    
    return match.group(0)

# Apply the fix
fixed_content = re.sub(pattern, fix_tool_definition, content, flags=re.DOTALL)

# Write back the fixed content
with open('/Users/jacc/Downloads/TextRealmsAI/backend/src/text_parser/parser_engine.py', 'w') as f:
    f.write(fixed_content)

print("Fixed tool class definitions with type annotations")
