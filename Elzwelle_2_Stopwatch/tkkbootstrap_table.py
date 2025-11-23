import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import SUCCESS

# Create main window
my_w = ttk.Window()
my_w.geometry("400x300")  # Set window size

# Fetch default color theme
colors = my_w.style.colors

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

# Create Tableview Widget
dv = ttk.tableview.Tableview(
    master=my_w,
    paginated=True, # Enable pagination
    coldata=l1, # Column headers
    rowdata=r_set, # Table data
    searchable=True, # Enable search feature
    bootstyle=SUCCESS, # Bootstrap style
    pagesize=10, # Number of rows per page
    height=10, # Number of visible rows
    stripecolor=(colors.light, None) # Row stripe colors
)

dv.grid(row=0, column=0, padx=10, pady=5)

# Autofit columns to match content
dv.autofit_columns()

# Run the Tkinter application
my_w.mainloop()