

import mysql.connector
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd


def authenticate_user(username, password):

    return username == 'admin' and password == 'aupp'


def open_login_window():
    login_window = Tk()
    login_window.title('Login')
    login_window.geometry('300x150')
    login_window.resizable(False, False)

    Label(login_window, text='Username:').pack(pady=5)
    username_entry = Entry(login_window, width=20)
    username_entry.pack(pady=5)

    Label(login_window, text='Password:').pack(pady=5)
    password_entry = Entry(login_window, width=20, show='*')
    password_entry.pack(pady=5)

    def authenticate():
        username = username_entry.get()
        password = password_entry.get()

        if authenticate_user(username, password):
            mb.showinfo('Login Successful', 'Welcome, ' + username + '!')
            login_window.destroy()
            root.deiconify()
        else:
            mb.showerror('Login Failed', 'Invalid username or password')

    Button(login_window, text='Login', command=authenticate).pack(pady=5, padx=5, ipadx=20, ipady=5)

    login_window.mainloop()
def login():
    login_window = Tk()
    login_window.title('Login')
    login_window.geometry('300x150')
    login_window.resizable(False, False)

    Label(login_window, text='Username:').pack(pady=5)
    username_entry = Entry(login_window, width=20)
    username_entry.pack(pady=5)

    Label(login_window, text='Password:').pack(pady=5)
    password_entry = Entry(login_window, width=20, show='*')
    password_entry.pack(pady=5)

    def authenticate():
        username = username_entry.get()
        password = password_entry.get()

        if authenticate_user(username, password):
            mb.showinfo('Login Successful', 'Welcome, ' + username + '!')
            login_window.destroy()
            root.deiconify()
        else:
            mb.showerror('Login Failed', 'Invalid username or password')

    Button(login_window, text='Login', command=authenticate).pack(pady=10)
    login_window.mainloop()

def issuer_card():
    Cid = sd.askstring('Issuer Card ID', 'What is the Issuer\'s Card ID?\t\t\t')
    if not Cid:
        mb.showerror('Issuer ID cannot be zero!', 'Issuer ID cannot be empty.')
    else:
        return Cid
def display_records():
    global cursor
    global tree

    tree.delete(*tree.get_children())

    try:
        cursor.execute('SELECT * FROM Library')
        data = cursor.fetchall()

        for records in data:
            tree.insert('', END, values=records)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        mb.showerror("Database Error", f"Error fetching records: {err}")

def add_record():
    global connector, bk_name, bk_id, author_name, bk_status, card_id, genre_entry

    if bk_status.get() == 'Issued':
        card_id_value = issuer_card()
        if card_id_value is not None:
            card_id.set(card_id_value)
        else:
            # If card ID is not provided, return without adding the record
            return

    try:
        with connector.cursor() as cursor:
            genre = genre_entry.get()  # Add this line to retrieve the genre from the entry
            surety = mb.askyesno('Verify', 'Please check it once again')
            if surety:
                cursor.execute(
                    'INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID, GENRE) VALUES (%s, %s, %s, %s, %s, %s)',
                    (bk_name.get(), bk_id.get(), author_name.get(), bk_status.get(), card_id.get(), genre))
                connector.commit()
                mb.showinfo('Book added', 'The new book was successfully added')
                clear_and_display()
    except mysql.connector.IntegrityError:
        mb.showerror('Book ID already in use!', 'The Book ID you are trying to enter is already used')



def change_availability():
    global card_id, tree, connector

    if not tree.selection():
        mb.showerror('Error!', 'Please select a book from the database')
        return

    current_item = tree.focus()
    values = tree.item(current_item)
    BK_id = values['values'][1]
    BK_status = values["values"][3]

    if BK_status == 'Issued':
        surety = mb.askyesno('Is return confirmed?', 'Has the book been returned to you?')
        if surety:
            cursor.execute('UPDATE Library SET bk_status=%s, card_id=%s WHERE bk_id=%s', ('Available', 'N/A', BK_id))
            connector.commit()
        else:
            mb.showinfo(
                'Cannot be returned', 'The book status cannot be set to Available unless it has been returned')
    else:
        cursor.execute('UPDATE Library SET bk_status=%s, card_id=%s WHERE bk_id=%s', ('Issued', issuer_card(), BK_id))
        connector.commit()

    clear_and_display()


def clear_fields():
    global bk_status, bk_id, bk_name, author_name, card_id, genre_entry

    bk_status.set('Available')
    for i in ['bk_id', 'bk_name', 'author_name', 'card_id', 'genre_entry']:
        eval(f"{i}.set('')")
    try:
        tree.selection_remove(tree.selection()[0])
    except:
        pass


def clear_and_display():
    clear_fields()
    display_records()


def view_record():
    global bk_name, bk_id, bk_status, author_name, card_id
    global tree

    if not tree.focus():
        mb.showerror('Select a row!',
                     'To view a record, you must select it in the table. Please do so before continuing.')
        return

    current_item_selected = tree.focus()
    values_in_selected_item = tree.item(current_item_selected)
    selection = values_in_selected_item['values']

    bk_name.set(selection[0])
    bk_id.set(selection[1])
    bk_status.set(selection[3])
    author_name.set(selection[2])
    try:
        card_id.set(selection[4])
    except:
        card_id.set('')


def update_record():
    def update(genre_entry_value):
        global bk_status, bk_name, bk_id, author_name, card_id, connector, tree

        if bk_status.get() == 'Issued':
            card_id_value = issuer_card()
            if card_id_value is not None:
                card_id.set(card_id_value)

        cursor.execute(
            'UPDATE Library SET BK_NAME=%s, BK_STATUS=%s, AUTHOR_NAME=%s, CARD_ID=%s, GENRE=%s WHERE BK_ID=%s',
            (bk_name.get(), bk_status.get(), author_name.get(), card_id.get(), genre_entry_value, bk_id.get()))
        connector.commit()
        clear_and_display()
        edit.destroy()

    view_record()

    edit = Toplevel(root)
    edit.title('Update Record')
    edit.geometry('300x250')

    Label(edit, text='Genre:').pack(pady=5)
    genre_entry = Entry(edit, width=20)
    genre_entry.pack(pady=5)

    Button(edit, text='Update Record', font=btn_font, bg='SteelBlue', width=20, command=lambda: update(genre_entry.get())).pack(pady=10)


def remove_record():
    if not tree.selection():
        mb.showerror('Error!', 'Please select an item from the database')
        return

    current_item = tree.focus()
    values = tree.item(current_item)
    selection = values["values"]

    cursor.execute('DELETE FROM Library WHERE BK_ID=%s', (selection[1],))
    connector.commit()

    tree.delete(current_item)
    mb.showinfo('Done', 'The record you wanted deleted was successfully deleted.')


def delete_inventory():
    if mb.askyesno('Are you sure?',
                   'Are you sure you want to delete the entire inventory?\n\nThis command cannot be reversed'):
        tree.delete(*tree.get_children())
        cursor.execute('DELETE FROM Library')
        connector.commit()

def search_record_by_id():
    global cursor, tree

    book_id_to_search = sd.askstring('Search by Book ID', 'Enter the Book ID to search for:')
    if not book_id_to_search:
        mb.showerror('Invalid Input', 'Book ID cannot be empty.')
        return

    try:
        cursor.execute('SELECT * FROM Library WHERE BK_ID = %s', (book_id_to_search,))
        record = cursor.fetchone()

        if record:
            tree.delete(*tree.get_children())
            tree.insert('', END, values=record)
        else:
            mb.showinfo('Not Found', f'No record found for Book ID: {book_id_to_search}')
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        mb.showerror("Database Error", f"Error searching for record: {err}")

open_login_window()
root = Tk()
root.title('PythonGeeks Library Management System')
root.geometry('1010x530')
root.resizable(False, False)

connector = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='Roosmile@2004',
    database='library_py'
)

cursor = connector.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Library (
        BK_NAME TEXT,
        BK_ID VARCHAR(255) PRIMARY KEY NOT NULL UNIQUE,
        AUTHOR_NAME TEXT,
        BK_STATUS TEXT,
        CARD_ID TEXT,
        GENRE TEXT
    )
''')



bk_status = StringVar()
bk_name = StringVar()
bk_id = StringVar()
author_name = StringVar()
card_id = StringVar()
genre_entry = StringVar()
btn_font = ('Gill Sans MT', 13)
lbl_font = ('Georgia', 13)  # Font for all labels
entry_font = ('Times New Roman', 12)  # Font for all Entry widgets
left_frame = Frame(root, bg='black')  # Change background color to black
left_frame.place(x=0, y=0, relwidth=0.3, relheight=1)  # Move up the left_frame and adjust the height

RT_frame = Frame(root, bg='black')  # Change background color to black
RT_frame.place(relx=0.3, y=0, relheight=0.2, relwidth=0.7)

RB_frame = Frame(root, bg='black')  # Change background color to black
RB_frame.place(relx=0.3, rely=0.2, relheight=0.8, relwidth=0.7)
Label(left_frame, text='Book Name', bg='black', font=lbl_font, fg='white').place(x=98, y=25)  # Change background color to black and text color to white
Entry(left_frame, width=25, font=entry_font, textvariable=bk_name).place(x=45, y=55)

Label(left_frame, text='Book ID', bg='black', font=lbl_font, fg='white').place(x=110, y=105)  # Change background color to black and text color to white
bk_id_entry = Entry(left_frame, width=25, font=entry_font, textvariable=bk_id)
bk_id_entry.place(x=45, y=135)

Label(left_frame, text='Author Name', bg='black', font=lbl_font, fg='white').place(x=90, y=185)  # Change background color to black and text color to white
Entry(left_frame, width=25, font=entry_font, textvariable=author_name).place(x=45, y=215)

Label(left_frame, text='Status of the Book', bg='black', font=lbl_font, fg='white').place(x=75, y=265)  # Change background color to black and text color to white
dd = OptionMenu(left_frame, bk_status, *['Available', 'Issued'])
dd.configure(font=entry_font, width=12)
dd.place(x=75, y=300)
Label(left_frame, text='Genre', bg='black', font=lbl_font, fg='white').place(x=45, y=350)  # Adjust y-coordinate
Entry(left_frame, width=25, font=entry_font, textvariable=genre_entry).place(x=45, y=380)  # Adjust y-coordinate

submit = Button(left_frame, text='Add new record', font=btn_font, bg='SteelBlue', width=20, command=add_record)
submit.place(x=50, y=450)  # Adjust y-coordinate

clear = Button(left_frame, text='Clear fields', font=btn_font, bg='SteelBlue', width=20, command=clear_fields)
clear.place(x=50, y=500)



RT_frame.columnconfigure(0, weight=1)  # Make the first column (label) take more space

Button(RT_frame, text='Delete book record', font=btn_font, bg='SteelBlue', width=15, command=remove_record).pack(side=LEFT, padx=5, pady=5)
Button(RT_frame, text='Delete full inventory', font=btn_font, bg='SteelBlue', width=15, command=delete_inventory).pack(side=LEFT, padx=5, pady=5)
Button(RT_frame, text='Update book details', font=btn_font, bg='SteelBlue', width=15, command=update_record).pack(side=LEFT, padx=5, pady=5)
Button(RT_frame, text='Change Availability', font=btn_font, bg='SteelBlue', width=17, command=change_availability).pack(side=LEFT, padx=5, pady=5)

Label(RB_frame, text='BOOK INVENTORY', bg='DodgerBlue', font=("Noto Sans CJK TC", 15, 'bold')).pack(side=TOP, fill=X)

Button(RT_frame, text='Search', font=btn_font, bg='SteelBlue', width=12, command=search_record_by_id).pack(side=LEFT, padx=5, pady=5)
Label(left_frame, text='Genre', bg='black', font=lbl_font, fg='white').place(x=110, y=415)
Entry(left_frame, width=25, font=entry_font, textvariable=genre_entry).place(x=45, y=445)

submit = Button(left_frame, text='Add new record', font=btn_font, bg='SteelBlue', width=20, command=add_record)
submit.place(x=50, y=495)

tree = ttk.Treeview(RB_frame, selectmode=BROWSE, columns=('Book Name', 'Book ID', 'Author', 'Status', 'Issuer Card ID','Genre'))

XScrollbar = Scrollbar(tree, orient=HORIZONTAL, command=tree.xview)
YScrollbar = Scrollbar(tree, orient=VERTICAL, command=tree.yview)
XScrollbar.pack(side=BOTTOM, fill=X)
YScrollbar.pack(side=RIGHT, fill=Y)

tree.config(xscrollcommand=XScrollbar.set, yscrollcommand=YScrollbar.set)

tree.heading('Book Name', text='Book Name', anchor=CENTER)
tree.heading('Book ID', text='Book ID', anchor=CENTER)
tree.heading('Author', text='Author', anchor=CENTER)
tree.heading('Status', text='Status of the Book', anchor=CENTER)
tree.heading('Issuer Card ID', text='Student ID', anchor=CENTER)
tree.heading('Genre', text='Book Genre', anchor=CENTER)


tree.column('#0', width=0, stretch=NO)
tree.column('#1', width=225, stretch=NO)
tree.column('#2', width=70, stretch=NO)
tree.column('#3', width=150, stretch=NO)
tree.column('#4', width=105, stretch=NO)
tree.column('#5', width=132, stretch=NO)

tree.place(y=30, x=0, relheight=0.9, relwidth=1)

display_records()

root.mainloop()

# Make sure to close the cursor and connection when you're done
cursor.close()
connector.close()
