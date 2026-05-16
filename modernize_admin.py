import os

path = 'admin_page.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Replace width='stretch' with use_container_width=True
text = text.replace("width='stretch'", "use_container_width=True")

# 2. Optimize Analytics Layout (metrics columns)
# Let's find where metrics are displayed and maybe make them more columns.
# In admin_page.py, typically: col1, col2, col3, col4 = st.columns(4)
# If it's already 4, it's fine. 
# But maybe we can put the charts side-by-side.

# Optimize Analytics charts to be side-by-side if they weren't
# I'll check the current analytics code in admin_page.py
with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated admin_page.py with use_container_width.")
