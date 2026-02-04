import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.widgets.tableview import Tableview
from ttkbootstrap.constants import SUCCESS, PRIMARY

# Create main window
my_w = ttk.Window()
my_w.geometry("600x500")  # Set window size

# Fetch default color theme
colors = my_w.style.colors
my_w.style.configure('.', font=('Helvetica', 16))

# Define table column headers
l1 = [
    {"text": "id", "stretch": False},
    {"text":"Name","stretch":True},
    "Class",
    {"text":"Mark"},
    {"text":"Gender"}
]  

# Sample data rows as a list of tuples
r_set = [
    (1, "Alex", 'Four', 90, 'Female'),    (2, "Ron", "Five", 80, 'Male'),
    (3, "Geek", 'Four', 70, 'Male'),    (4, 'King', 'Five', 78, 'Female'),
    (5, 'Queen', 'Four', 60, 'Female'),    (6, 'Jack', 'Five', 70, 'Female')
]

col_header = [
    {"text":"Startzeit","stretch":True},
    {"text":"Zeitstempel","stretch":True},
    {"text":"Zielzeit","stretch":True},
    {"text":"Zeitstempel","stretch":True},
]

row_data = [
    ("00:00:00", 0, "00:00:00", 0),
    ("00:00:00", 0, "00:00:00", 0),
    ("00:00:00", 0, "00:00:00", 0),
    ("00:00:00", 0, "00:00:00", 0),
]

# Create Tableview Widget
dv = Tableview(
    master=my_w,
    paginated=True,                    # Enable pagination
    coldata=col_header,                         # Column headers
    rowdata=row_data,                      # Table data
    searchable=False,                   # Enable search feature
    bootstyle=PRIMARY,                  # Bootstrap style
    pagesize=10,                        # Number of rows per page
    height=10,                          # Number of visible rows
    stripecolor=(colors.light, None),   # Row stripe colors
)

dv.pack(fill = tk.BOTH, expand = tk.YES, padx = 15, pady = 15)

#dv.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')

# Autofit columns to match content
dv.autofit_columns()

# Run the Tkinter application
my_w.mainloop()


# dv.insert_row('end', ['Marzale LLC', 26])