# main.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
from datetime import datetime

class LibraryManagementSystem:
    def __init__(self):
        self.db = Database()
        self.root = ctk.CTk()
        self.root.title("Library Management System")
        self.root.geometry("1200x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.setup_ui()
    
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.create_sidebar()
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(side="right", fill="both", expand=True)
        self.show_dashboard()
    
    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self.main_frame, width=200)
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        sidebar.pack_propagate(False)
        
        ctk.CTkLabel(sidebar, text="Library System", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        nav_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("📚 Books", self.show_books),
            ("👥 Members", self.show_members),
            ("📖 Issue", self.show_issue),
            ("↩️ Return", self.show_return),
            ("📋 Issues", self.show_issues),
        ]
        
        for text, cmd in nav_items:
            btn = ctk.CTkButton(sidebar, text=text, command=cmd, anchor="w", fg_color="transparent")
            btn.pack(fill="x", padx=10, pady=5)
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Library Dashboard", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        stats_frame = ctk.CTkFrame(self.content_frame)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        stats = [
            ("Total Books", len(self.db.get_all_books()), "#4CC9F0"),
            ("Total Members", len(self.db.get_all_members()), "#F72585"),
            ("Active Issues", len(self.db.get_active_issues()), "#7209B7"),
        ]
        
        for i, (label, value, color) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame, fg_color=color)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            stats_frame.columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=label).pack(pady=(10, 5))
            ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(weight="bold")).pack(pady=5)
    
    def show_books(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Books Management", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        # Add book form
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(form_frame, text="Add New Book", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        entries_frame = ctk.CTkFrame(form_frame)
        entries_frame.pack(fill="x", padx=10, pady=10)
        self.book_entries = {}
        
        for i, field in enumerate(["Title", "Author", "Publisher", "ISBN", "Copies"]):
            ctk.CTkLabel(entries_frame, text=field).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ctk.CTkEntry(entries_frame, width=200)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.book_entries[field.lower()] = entry
        
        ctk.CTkButton(entries_frame, text="Add Book", command=self.add_book).grid(row=5, column=1, pady=10, sticky="e")
        
        # Books list
        list_frame = ctk.CTkFrame(self.content_frame)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkLabel(list_frame, text="All Books", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        columns = ("ID", "Title", "Author", "Publisher", "ISBN", "Total", "Available")
        self.books_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=100)
        self.books_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_books()
    
    def add_book(self):
        try:
            data = {key: entry.get() for key, entry in self.book_entries.items()}
            if not all(data.values()):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            if self.db.add_book(data['title'], data['author'], data['publisher'], data['isbn'], int(data['copies'])):
                messagebox.showinfo("Success", "Book added successfully!")
                for entry in self.book_entries.values():
                    entry.delete(0, 'end')
                self.load_books()
            else:
                messagebox.showerror("Error", "ISBN already exists!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid number for copies")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def load_books(self):
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        for book in self.db.get_all_books():
            self.books_tree.insert("", "end", values=book)
    
    def show_members(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Members Management", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        # Add member form
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(form_frame, text="Add New Member", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        entries_frame = ctk.CTkFrame(form_frame)
        entries_frame.pack(fill="x", padx=10, pady=10)
        self.member_entries = {}
        
        fields = ["Name", "Email", "Phone", "Address"]
        for i, field in enumerate(fields):
            row, col = i // 2, (i % 2) * 2
            ctk.CTkLabel(entries_frame, text=field + ":").grid(row=row, column=col, padx=5, pady=5, sticky="w")
            entry = ctk.CTkTextbox(entries_frame, height=60) if field == "Address" else ctk.CTkEntry(entries_frame, width=200)
            entry.grid(row=row, column=col+1, padx=5, pady=5, sticky="ew")
            self.member_entries[field.lower()] = entry
        
        ctk.CTkButton(entries_frame, text="Add Member", command=self.add_member).grid(row=2, column=3, pady=10, sticky="e")
        
        # Members list
        list_frame = ctk.CTkFrame(self.content_frame)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkLabel(list_frame, text="All Members", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=10)
        
        columns = ("ID", "Name", "Email", "Phone", "Address", "Join Date", "Status")
        self.members_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.members_tree.heading(col, text=col)
        self.members_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Action buttons
        action_frame = ctk.CTkFrame(list_frame)
        action_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(action_frame, text="Refresh", command=self.load_members).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Delete", command=self.delete_member, fg_color="#D32F2F").pack(side="right", padx=5)
        ctk.CTkButton(action_frame, text="Toggle Status", command=self.toggle_member_status, fg_color="#FF9800").pack(side="right", padx=5)
        
        self.load_members()
    
    def add_member(self):
        try:
            data = {}
            for key, entry in self.member_entries.items():
                data[key] = entry.get("1.0", "end-1c").strip() if key == "address" else entry.get().strip()
            
            if not data['name'] or not data['email']:
                messagebox.showerror("Error", "Name and Email are required")
                return
            
            if "@" not in data['email']:
                messagebox.showerror("Error", "Please enter valid email")
                return
            
            if self.db.add_member(data['name'], data['email'], data['phone'], data['address']):
                messagebox.showinfo("Success", "Member added successfully!")
                for key, entry in self.member_entries.items():
                    entry.delete("1.0", "end") if key == "address" else entry.delete(0, 'end')
                self.load_members()
            else:
                messagebox.showerror("Error", "Email already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def load_members(self):
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        for member in self.db.get_all_members():
            formatted = list(member)
            if formatted[5]: formatted[5] = formatted[5].split()[0]
            self.members_tree.insert("", "end", values=formatted, tags=(formatted[6],))
        self.members_tree.tag_configure('Active', background='#e8f5e8')
        self.members_tree.tag_configure('Inactive', background='#ffebee')
    
    def delete_member(self):
        selected = self.members_tree.selection()
        if not selected: return
        member_data = self.members_tree.item(selected[0], 'values')
        if messagebox.askyesno("Confirm", f"Delete {member_data[1]}?"):
            if self.db.delete_member(member_data[0]):
                messagebox.showinfo("Success", "Member deleted!")
                self.load_members()
            else:
                messagebox.showerror("Error", "Cannot delete - active issues!")
    
    def toggle_member_status(self):
        selected = self.members_tree.selection()
        if not selected: return
        member_data = self.members_tree.item(selected[0], 'values')
        new_status = "Inactive" if member_data[6] == "Active" else "Active"
        if self.db.update_member_status(member_data[0], new_status):
            messagebox.showinfo("Success", f"Status updated to {new_status}")
            self.load_members()
    
    def show_issue(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Issue Book", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        main_frame = ctk.CTkFrame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left frame
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Member selection
        member_frame = ctk.CTkFrame(left_frame)
        member_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(member_frame, text="Select Member", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        self.member_search = ctk.CTkEntry(member_frame, placeholder_text="Search member...")
        self.member_search.pack(fill="x", pady=5)
        self.member_search.bind('<KeyRelease>', self.search_members_issue)
        
        self.members_list = ctk.CTkTextbox(member_frame, height=100)
        self.members_list.pack(fill="x", pady=5)
        
        # Book selection
        book_frame = ctk.CTkFrame(left_frame)
        book_frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(book_frame, text="Select Book", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        self.book_search = ctk.CTkEntry(book_frame, placeholder_text="Search book...")
        self.book_search.pack(fill="x", pady=5)
        self.book_search.bind('<KeyRelease>', self.search_books_issue)
        
        self.books_list = ctk.CTkTextbox(book_frame, height=100)
        self.books_list.pack(fill="both", expand=True, pady=5)
        
        # Right frame
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both")
        
        details_frame = ctk.CTkFrame(right_frame)
        details_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(details_frame, text="Issue Details", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        ctk.CTkLabel(details_frame, text="Due Days:").pack(anchor="w", pady=5)
        self.due_days = ctk.CTkEntry(details_frame, placeholder_text="14")
        self.due_days.insert(0, "14")
        self.due_days.pack(fill="x", pady=5)
        
        self.summary_text = ctk.CTkTextbox(details_frame, height=150, state="disabled")
        self.summary_text.pack(fill="x", pady=10)
        
        self.issue_btn = ctk.CTkButton(details_frame, text="Issue Book", command=self.issue_book, state="disabled")
        self.issue_btn.pack(fill="x", pady=5)
        
        self.selected_member = None
        self.selected_book = None
        self.update_issue_lists()
    
    def search_members_issue(self, event=None):
        self.update_issue_lists()
    
    def search_books_issue(self, event=None):
        self.update_issue_lists()
    
    def update_issue_lists(self):
        # Members list
        members = self.db.get_all_members()
        search_term = self.member_search.get().lower()
        filtered_members = [m for m in members if m[6] == 'Active' and 
                           (not search_term or search_term in m[1].lower() or search_term in m[2].lower())]
        
        self.members_list.configure(state="normal")
        self.members_list.delete("1.0", "end")
        for member in filtered_members[:10]:  # Show first 10 results
            self.members_list.insert("end", f"{member[0]}: {member[1]} - {member[2]}\n")
        self.members_list.configure(state="disabled")
        
        # Books list
        books = self.db.get_all_books()
        search_term = self.book_search.get().lower()
        filtered_books = [b for b in books if b[6] > 0 and 
                         (not search_term or search_term in b[1].lower() or search_term in b[2].lower())]
        
        self.books_list.configure(state="normal")
        self.books_list.delete("1.0", "end")
        for book in filtered_books[:10]:
            self.books_list.insert("end", f"{book[0]}: {book[1]} by {book[2]} ({book[6]} available)\n")
        self.books_list.configure(state="disabled")
    
    def issue_book(self):
        if not self.selected_member or not self.selected_book:
            messagebox.showerror("Error", "Please select member and book")
            return
        
        try:
            days = int(self.due_days.get())
            if days <= 0:
                messagebox.showerror("Error", "Due days must be positive")
                return
            
            if self.db.issue_book(self.selected_book[0], self.selected_member[0], days):
                messagebox.showinfo("Success", "Book issued successfully!")
                self.selected_member = None
                self.selected_book = None
                self.update_issue_lists()
                self.update_issue_summary()
            else:
                messagebox.showerror("Error", "Failed to issue book")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid number")
    
    def update_issue_summary(self):
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        
        if self.selected_member and self.selected_book:
            try:
                days = int(self.due_days.get())
                due_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                summary = f"Member: {self.selected_member[1]}\nBook: {self.selected_book[1]}\nDue: {due_date}"
                self.summary_text.insert("1.0", summary)
                self.issue_btn.configure(state="normal")
            except:
                self.summary_text.insert("1.0", "Invalid due days")
                self.issue_btn.configure(state="disabled")
        else:
            self.summary_text.insert("1.0", "Select member and book")
            self.issue_btn.configure(state="disabled")
        
        self.summary_text.configure(state="disabled")
    
    def show_return(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Return Book", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        main_frame = ctk.CTkFrame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Issues list
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ctk.CTkLabel(left_frame, text="Active Issues", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=10)
        
        self.issues_tree = ttk.Treeview(left_frame, columns=("ID", "Book", "Member", "Due Date"), show="headings", height=15)
        for col in ("ID", "Book", "Member", "Due Date"):
            self.issues_tree.heading(col, text=col)
        self.issues_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.issues_tree.bind('<<TreeviewSelect>>', self.on_issue_select)
        
        # Return details
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both")
        ctk.CTkLabel(right_frame, text="Return Details", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=10)
        
        self.details_text = ctk.CTkTextbox(right_frame, height=200, state="disabled")
        self.details_text.pack(fill="x", padx=10, pady=10)
        
        self.return_btn = ctk.CTkButton(right_frame, text="Process Return", command=self.process_return, state="disabled")
        self.return_btn.pack(fill="x", padx=10, pady=10)
        
        self.selected_issue = None
        self.load_active_issues()
    
    def load_active_issues(self):
        for item in self.issues_tree.get_children():
            self.issues_tree.delete(item)
        for issue in self.db.get_active_issues():
            self.issues_tree.insert("", "end", values=(issue[0], issue[1], issue[2], issue[4].split()[0]))
    
    def on_issue_select(self, event):
        selection = self.issues_tree.selection()
        if selection:
            issue_data = self.issues_tree.item(selection[0], 'values')
            self.selected_issue = issue_data
            self.details_text.configure(state="normal")
            self.details_text.delete("1.0", "end")
            self.details_text.insert("1.0", f"Issue ID: {issue_data[0]}\nBook: {issue_data[1]}\nMember: {issue_data[2]}")
            self.details_text.configure(state="disabled")
            self.return_btn.configure(state="normal")
    
    def process_return(self):
        if not self.selected_issue: return
        if messagebox.askyesno("Confirm", f"Return {self.selected_issue[1]}?"):
            if self.db.return_book(self.selected_issue[0]):
                messagebox.showinfo("Success", "Book returned!")
                self.load_active_issues()
                self.selected_issue = None
                self.return_btn.configure(state="disabled")
    
    def show_issues(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Active Issues", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        # Stats
        stats_frame = ctk.CTkFrame(self.content_frame)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        issues = self.db.get_active_issues()
        total = len(issues)
        overdue = len([i for i in issues if (datetime.now() - datetime.strptime(i[4], "%Y-%m-%d %H:%M:%S")).days > 0])
        
        stats = [
            ("Total Issues", total, "#2196F3"),
            ("Overdue", overdue, "#F44336"),
            ("On Time", total - overdue, "#4CAF50"),
        ]
        
        for i, (label, value, color) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame, fg_color=color)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            stats_frame.columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=label).pack(pady=5)
            ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # Issues table
        table_frame = ctk.CTkFrame(self.content_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("ID", "Book", "Member", "Issue Date", "Due Date", "Status")
        self.issues_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.issues_table.heading(col, text=col)
        self.issues_table.pack(fill="both", expand=True, padx=10, pady=10)
        
        for issue in issues:
            due_date = datetime.strptime(issue[4], "%Y-%m-%d %H:%M:%S")
            status = "Overdue" if (datetime.now() - due_date).days > 0 else "On Time"
            self.issues_table.insert("", "end", values=(
                issue[0], issue[1], issue[2], issue[3].split()[0], issue[4].split()[0], status
            ))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    from datetime import timedelta
    app = LibraryManagementSystem()
    app.run()