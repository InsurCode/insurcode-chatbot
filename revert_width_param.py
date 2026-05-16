import os

files = ['app.py', 'admin_page.py']
for path in files:
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Replace use_container_width=True with width='stretch'
    text = text.replace("use_container_width=True", "width='stretch'")
    # Replace use_container_width=False with width='content'
    text = text.replace("use_container_width=False", "width='content'")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Updated {path} to use width instead of use_container_width.")
