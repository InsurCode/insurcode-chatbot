import os

path = 'app.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace width='stretch' with use_container_width=True
text = text.replace("width='stretch'", "use_container_width=True")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated app.py with use_container_width.")
