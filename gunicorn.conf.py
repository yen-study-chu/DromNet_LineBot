import os

workers = 4
bind = f"{os.environ.get('IP')}:{os.environ.get('PORT')}"
