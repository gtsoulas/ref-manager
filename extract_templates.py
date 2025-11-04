import re

# Read the combined file
with open('all_templates.html', 'r') as f:
    content = f.read()

# Split by FILE: markers
sections = re.split(r'<!-- =+\s*FILE: (.+?)\s*=+ -->', content)

# Process each section (skip first empty section)
for i in range(1, len(sections), 2):
    filename = sections[i].strip()
    template_content = sections[i+1].strip()
    
    # Create the file
    with open(filename, 'w') as f:
        f.write(template_content)
    
    print(f"✓ Created {filename}")

print(f"\nTotal templates created: {(len(sections)-1)//2}")
