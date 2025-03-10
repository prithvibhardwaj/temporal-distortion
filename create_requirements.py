import regex as re
def create_requirements_txt(input_file, output_file="requirements.txt"):
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    packages = []
    # Regular expression to extract name, version, and channel
    pattern = r'^\s*(\S+)\s+(\S+)\s+(\S*)\s*(\S*)?\s*$'
    allowed_channels=['pypi']
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        match = re.match(pattern, line)
        if match:
            name = match.group(1)
            version = match.group(2)
            build = match.group(3)
            channel = match.group(4) if match.group(4) else ""
            
            if name.startswith("_") or (channel not in allowed_channels):
                continue
                
            packages.append(f"{name}=={version}")
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(sorted(packages)))
    
    return len(packages)

filename=input("Enter filename: ")
count = create_requirements_txt(filename)
print(f"Created requirements.txt with {count} packages")
