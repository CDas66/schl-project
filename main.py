# main.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from database import Database
import sqlite3
from datetime import datetime

class LibraryManagementSystem:
    def __init__(self):
        # Initialize database
        self.db = Database()
        
        # Setup main window
        self.root = ctk.CTk()
        self.root.title("Library Management System")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        # Configure theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_content_area()
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_sidebar(self):
        """Create sidebar navigation"""
        sidebar_frame = ctk.CTkFrame(self.main_frame, width=200, corner_radius=0)
        sidebar_frame.pack(side="left", fill="y", padx=(0, 10))
        sidebar_frame.pack_propagate(False)
        
        # App title
        title_label = ctk.CTkLabel(
            sidebar_frame, 
            text="Library System", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Navigation buttons
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("📚 Books Management", self.show_books),
            ("👥 Members Management", self.show_members),
            ("📖 Issue Books", self.show_issue),
            ("↩️ Return Books", self.show_return),
            ("📋 View Issues", self.show_issues),
        ]
        
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                sidebar_frame,
                text=text,
                command=command,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color="transparent"
            )
            btn.pack(fill="x", padx=10, pady=5)
    
    def create_content_area(self):
        """Create main content area"""
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(side="right", fill="both", expand=True)
    
    def clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show dashboard"""
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame, 
            text="Library Dashboard", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Statistics frame
        stats_frame = ctk.CTkFrame(self.content_frame)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        # Get statistics
        total_books = len(self.db.get_all_books())
        total_members = len(self.db.get_all_members())
        active_issues = len(self.db.get_active_issues())
        
        stats_data = [
            ("Total Books", total_books, "#4CC9F0"),
            ("Total Members", total_members, "#F72585"),
            ("Active Issues", active_issues, "#7209B7"),
        ]
        
        for i, (label, value, color) in enumerate(stats_data):
            stat_card = ctk.CTkFrame(stats_frame, fg_color=color)
            stat_card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            stats_frame.columnconfigure(i, weight=1)
            
            ctk.CTkLabel(stat_card, text=label, font=ctk.CTkFont(size=16)).pack(pady=(10, 5))
            ctk.CTkLabel(stat_card, text=str(value), font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(5, 10))
    
    def show_books(self):
        """Show books management"""
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame, 
            text="Books Management", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Add book form
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(form_frame, text="Add New Book", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=10)
        
        # Form entries
        entries_frame = ctk.CTkFrame(form_frame)
        entries_frame.pack(fill="x", padx=10, pady=10)
        
        titles = ["Title", "Author", "Publisher", "ISBN", "Copies"]
        self.book_entries = {}
        
        for i, field in enumerate(titles):
            ctk.CTkLabel(entries_frame, text=field).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ctk.CTkEntry(entries_frame, width=200)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.book_entries[field.lower()] = entry
        
        # Add book button
        ctk.CTkButton(
            entries_frame, 
            text="Add Book", 
            command=self.add_book
        ).grid(row=len(titles), column=1, padx=5, pady=10, sticky="e")
        
        # Books list
        list_frame = ctk.CTkFrame(self.content_frame)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(list_frame, text="All Books", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=10)
        
        # Treeview for books
        columns = ("ID", "Title", "Author", "Publisher", "ISBN", "Total", "Available")
        self.books_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=100)
        
        self.books_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load books
        self.load_books()
    
    def add_book(self):
        """Add new book to database"""
        try:
            data = {key: entry.get() for key, entry in self.book_entries.items()}
            
            if not all(data.values()):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            success = self.db.add_book(
                data['title'], data['author'], data['publisher'],
                data['isbn'], int(data['copies'])
            )
            
            if success:
                messagebox.showinfo("Success", "Book added successfully!")
                # Clear entries
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
        """Load books into treeview"""
        # Clear existing items
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        books = self.db.get_all_books()
        for book in books:
            self.books_tree.insert("", "end", values=book)
    
    def show_members(self):
        """Show members management"""
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame, 
            text="Members Management", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Add member form
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(form_frame, text="Add New Member", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=10)
        
        # Form entries
        entries_frame = ctk.CTkFrame(form_frame)
        entries_frame.pack(fill="x", padx=10, pady=10)
        
        # Create a grid for better alignment
        entries_frame.columnconfigure(1, weight=1)
        entries_frame.columnconfigure(3, weight=1)
        
        titles = ["Name", "Email", "Phone", "Address"]
        self.member_entries = {}
        
        for i, field in enumerate(titles):
            row = i // 2
            col = (i % 2) * 2
            ctk.CTkLabel(entries_frame, text=field + ":").grid(row=row, column=col, padx=5, pady=5, sticky="w")
            if field == "Address":
                entry = ctk.CTkTextbox(entries_frame, width=200, height=60)
            else:
                entry = ctk.CTkEntry(entries_frame, width=200)
            entry.grid(row=row, column=col+1, padx=5, pady=5, sticky="ew")
            self.member_entries[field.lower()] = entry
        
        # Add member button
        button_frame = ctk.CTkFrame(entries_frame)
        button_frame.grid(row=2, column=2, columnspan=2, padx=5, pady=10, sticky="e")
        
        ctk.CTkButton(
            button_frame, 
            text="Add Member", 
            command=self.add_member
        ).pack(side="right", padx=5)
        
        # Search frame
        search_frame = ctk.CTkFrame(self.content_frame)
        search_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(search_frame, text="Search Members", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=5)
        
        search_inner_frame = ctk.CTkFrame(search_frame)
        search_inner_frame.pack(fill="x", padx=10, pady=10)
        
        self.member_search_entry = ctk.CTkEntry(search_inner_frame, placeholder_text="Search by name, email, or phone...")
        self.member_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            search_inner_frame, 
            text="Search", 
            command=self.search_members
        ).pack(side="right")
        
        ctk.CTkButton(
            search_inner_frame, 
            text="Show All", 
            command=self.load_members,
            fg_color="gray40"
        ).pack(side="right", padx=(0, 10))
        
        # Members list
        list_frame = ctk.CTkFrame(self.content_frame)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(list_frame, text="All Members", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=10)
        
        # Treeview for members
        columns = ("ID", "Name", "Email", "Phone", "Address", "Join Date", "Status")
        self.members_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        column_widths = {
            "ID": 50, "Name": 150, "Email": 180, "Phone": 120, 
            "Address": 200, "Join Date": 120, "Status": 80
        }
        
        for col in columns:
            self.members_tree.heading(col, text=col)
            self.members_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.members_tree.yview)
        self.members_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.members_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        tree_scroll.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        # Action buttons frame
        action_frame = ctk.CTkFrame(list_frame)
        action_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            action_frame, 
            text="Refresh", 
            command=self.load_members
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            action_frame, 
            text="Delete Selected", 
            command=self.delete_member,
            fg_color="#D32F2F",
            hover_color="#B71C1C"
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            action_frame, 
            text="Toggle Status", 
            command=self.toggle_member_status,
            fg_color="#FF9800",
            hover_color="#F57C00"
        ).pack(side="right", padx=5)
        
        # Load members
        self.load_members()
    
    def add_member(self):
        """Add new member to database"""
        try:
            data = {}
            for key, entry in self.member_entries.items():
                if key == "address":
                    data[key] = entry.get("1.0", "end-1c").strip()
                else:
                    data[key] = entry.get().strip()
            
            # Validate required fields
            if not data['name'] or not data['email']:
                messagebox.showerror("Error", "Name and Email are required fields")
                return
            
            # Validate email format
            if "@" not in data['email'] or "." not in data['email']:
                messagebox.showerror("Error", "Please enter a valid email address")
                return
            
            success = self.db.add_member(
                data['name'], data['email'], data['phone'], data['address']
            )
            
            if success:
                messagebox.showinfo("Success", "Member added successfully!")
                # Clear entries
                for key, entry in self.member_entries.items():
                    if key == "address":
                        entry.delete("1.0", "end")
                    else:
                        entry.delete(0, 'end')
                self.load_members()
            else:
                messagebox.showerror("Error", "Email already exists!")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def load_members(self):
        """Load members into treeview"""
        # Clear existing items
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        
        members = self.db.get_all_members()
        for member in members:
            # Format the date and handle None values
            formatted_member = list(member)
            if formatted_member[5]:  # Join date
                formatted_member[5] = formatted_member[5].split()[0]  # Remove time part
            self.members_tree.insert("", "end", values=formatted_member, tags=(formatted_member[6],))
        
        # Color coding for status
        self.members_tree.tag_configure('Active', background='#e8f5e8')
        self.members_tree.tag_configure('Inactive', background='#ffebee')
    
    def search_members(self):
        """Search members based on search term"""
        search_term = self.member_search_entry.get().strip()
        if not search_term:
            self.load_members()
            return
        
        # Clear existing items
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        
        members = self.db.search_members(search_term)
        for member in members:
            formatted_member = list(member)
            if formatted_member[5]:  # Join date
                formatted_member[5] = formatted_member[5].split()[0]
            self.members_tree.insert("", "end", values=formatted_member, tags=(formatted_member[6],))
    
    def delete_member(self):
        """Delete selected member"""
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a member to delete")
            return
        
        member_data = self.members_tree.item(selected[0], 'values')
        member_name = member_data[1]
        
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete member: {member_name}?\n\nThis action cannot be undone."
        )
        
        if confirm:
            try:
                # Add delete_member method to Database class
                success = self.db.delete_member(member_data[0])  # member_id
                if success:
                    messagebox.showinfo("Success", "Member deleted successfully!")
                    self.load_members()
                else:
                    messagebox.showerror("Error", "Cannot delete member with active book issues!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete member: {str(e)}")
    
    def toggle_member_status(self):
        """Toggle member status between Active/Inactive"""
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a member")
            return
        
        member_data = self.members_tree.item(selected[0], 'values')
        member_id = member_data[0]
        current_status = member_data[6]
        new_status = "Inactive" if current_status == "Active" else "Active"
        
        try:
            success = self.db.update_member_status(member_id, new_status)
            if success:
                messagebox.showinfo("Success", f"Member status updated to {new_status}")
                self.load_members()
            else:
                messagebox.showerror("Error", "Failed to update member status")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status: {str(e)}")
    
    def show_issue(self):
        """Show book issue form"""
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame, 
            text="Issue Book to Member", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Main issue form frame
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Selection forms
        left_frame = ctk.CTkFrame(form_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        
        # Member selection section
        member_section = ctk.CTkFrame(left_frame)
        member_section.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(member_section, text="1. Select Member", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        # Member search and selection
        member_search_frame = ctk.CTkFrame(member_section)
        member_search_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(member_search_frame, text="Search Member:").pack(side="left", padx=(0, 10))
        self.member_search_issue = ctk.CTkEntry(member_search_frame, placeholder_text="Enter member name or ID...")
        self.member_search_issue.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.member_search_issue.bind('<KeyRelease>', self.search_members_for_issue)
        
        # Members listbox
        member_list_frame = ctk.CTkFrame(member_section)
        member_list_frame.pack(fill="both", expand=True, pady=5)
        
        self.members_listbox = ctk.Listbox(member_list_frame, height=8, font=("Arial", 11))
        member_scrollbar = ttk.Scrollbar(member_list_frame, orient="vertical", command=self.members_listbox.yview)
        self.members_listbox.configure(yscrollcommand=member_scrollbar.set)
        
        self.members_listbox.pack(side="left", fill="both", expand=True)
        member_scrollbar.pack(side="right", fill="y")
        self.members_listbox.bind('<<ListboxSelect>>', self.on_member_select)
        
        # Selected member info
        self.selected_member_frame = ctk.CTkFrame(member_section)
        self.selected_member_frame.pack(fill="x", pady=5)
        
        self.selected_member_label = ctk.CTkLabel(self.selected_member_frame, text="No member selected", text_color="gray")
        self.selected_member_label.pack(pady=10)
        
        # Book selection section
        book_section = ctk.CTkFrame(left_frame)
        book_section.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(book_section, text="2. Select Book", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        # Book search and selection
        book_search_frame = ctk.CTkFrame(book_section)
        book_search_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(book_search_frame, text="Search Book:").pack(side="left", padx=(0, 10))
        self.book_search_issue = ctk.CTkEntry(book_search_frame, placeholder_text="Enter book title, author, or ISBN...")
        self.book_search_issue.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.book_search_issue.bind('<KeyRelease>', self.search_books_for_issue)
        
        # Books listbox
        book_list_frame = ctk.CTkFrame(book_section)
        book_list_frame.pack(fill="both", expand=True, pady=5)
        
        self.books_listbox = ctk.Listbox(book_list_frame, height=8, font=("Arial", 11))
        book_scrollbar = ttk.Scrollbar(book_list_frame, orient="vertical", command=self.books_listbox.yview)
        self.books_listbox.configure(yscrollcommand=book_scrollbar.set)
        
        self.books_listbox.pack(side="left", fill="both", expand=True)
        book_scrollbar.pack(side="right", fill="y")
        self.books_listbox.bind('<<ListboxSelect>>', self.on_book_select)
        
        # Selected book info
        self.selected_book_frame = ctk.CTkFrame(book_section)
        self.selected_book_frame.pack(fill="x", pady=5)
        
        self.selected_book_label = ctk.CTkLabel(self.selected_book_frame, text="No book selected", text_color="gray")
        self.selected_book_label.pack(pady=10)
        
        # Right side - Issue details and action
        right_frame = ctk.CTkFrame(form_frame)
        right_frame.pack(side="right", fill="both", padx=(10, 0), pady=10)
        
        # Issue details section
        details_section = ctk.CTkFrame(right_frame)
        details_section.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(details_section, text="3. Issue Details", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        # Due date selection
        due_date_frame = ctk.CTkFrame(details_section)
        due_date_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(due_date_frame, text="Due Date:").pack(anchor="w")
        
        self.due_days_var = ctk.StringVar(value="14")
        days_options = ["7", "14", "21", "30"]
        
        days_radio_frame = ctk.CTkFrame(due_date_frame)
        days_radio_frame.pack(fill="x", pady=5)
        
        for i, days in enumerate(days_options):
            ctk.CTkRadioButton(
                days_radio_frame, 
                text=f"{days} days", 
                variable=self.due_days_var, 
                value=days
            ).pack(side="left", padx=(0, 10))
        
        # Custom date entry
        custom_frame = ctk.CTkFrame(due_date_frame)
        custom_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(custom_frame, text="Custom days:").pack(side="left", padx=(0, 10))
        self.custom_days_entry = ctk.CTkEntry(custom_frame, width=60, placeholder_text="Days")
        self.custom_days_entry.pack(side="left")
        
        # Issue summary
        summary_frame = ctk.CTkFrame(details_section)
        summary_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(summary_frame, text="Issue Summary:", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        self.summary_text = ctk.CTkTextbox(summary_frame, height=120, state="disabled")
        self.summary_text.pack(fill="x", pady=5)
        
        # Action buttons
        action_frame = ctk.CTkFrame(details_section)
        action_frame.pack(fill="x", pady=10)
        
        self.issue_btn = ctk.CTkButton(
            action_frame,
            text="Issue Book",
            command=self.issue_book_to_member,
            state="disabled",
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        )
        self.issue_btn.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            action_frame,
            text="Clear Selection",
            command=self.clear_issue_selection,
            fg_color="#757575",
            hover_color="#424242"
        ).pack(fill="x", pady=5)
        
        # Initialize data
        self.load_all_members_for_issue()
        self.load_all_books_for_issue()
        self.selected_member_id = None
        self.selected_book_id = None
        self.update_issue_summary()
    
    def load_all_members_for_issue(self):
        """Load all active members for issue"""
        members = self.db.get_all_members()
        self.all_members = [m for m in members if m[6] == 'Active']  # Filter active members
        self.filtered_members = self.all_members.copy()
        self.update_members_listbox()
    
    def load_all_books_for_issue(self):
        """Load all available books for issue"""
        books = self.db.get_all_books()
        self.all_books = [b for b in books if b[6] > 0]  # Filter books with available copies
        self.filtered_books = self.all_books.copy()
        self.update_books_listbox()
    
    def update_members_listbox(self):
        """Update members listbox with filtered results"""
        self.members_listbox.delete(0, ctk.END)
        for member in self.filtered_members:
            display_text = f"{member[0]}: {member[1]} - {member[2]}"
            self.members_listbox.insert(ctk.END, display_text)
    
    def update_books_listbox(self):
        """Update books listbox with filtered results"""
        self.books_listbox.delete(0, ctk.END)
        for book in self.filtered_books:
            display_text = f"{book[0]}: {book[1]} by {book[2]} ({book[6]} available)"
            self.books_listbox.insert(ctk.END, display_text)
    
    def search_members_for_issue(self, event=None):
        """Search members in real-time"""
        search_term = self.member_search_issue.get().lower()
        if not search_term:
            self.filtered_members = self.all_members.copy()
        else:
            self.filtered_members = [
                m for m in self.all_members 
                if (search_term in str(m[0]).lower() or  # member_id
                    search_term in m[1].lower() or       # name
                    search_term in m[2].lower())         # email
            ]
        self.update_members_listbox()
    
    def search_books_for_issue(self, event=None):
        """Search books in real-time"""
        search_term = self.book_search_issue.get().lower()
        if not search_term:
            self.filtered_books = self.all_books.copy()
        else:
            self.filtered_books = [
                b for b in self.all_books 
                if (search_term in str(b[0]).lower() or  # book_id
                    search_term in b[1].lower() or       # title
                    search_term in b[2].lower() or       # author
                    search_term in b[4].lower())         # isbn
            ]
        self.update_books_listbox()
    
    def on_member_select(self, event):
        """Handle member selection"""
        selection = self.members_listbox.curselection()
        if selection:
            index = selection[0]
            member = self.filtered_members[index]
            self.selected_member_id = member[0]
            
            # Update display
            member_info = f"✅ Selected: {member[1]}\nEmail: {member[2]}\nPhone: {member[3]}"
            self.selected_member_label.configure(text=member_info, text_color="white")
            
            self.update_issue_summary()
            self.check_issue_ready()
    
    def on_book_select(self, event):
        """Handle book selection"""
        selection = self.books_listbox.curselection()
        if selection:
            index = selection[0]
            book = self.filtered_books[index]
            self.selected_book_id = book[0]
            
            # Update display
            book_info = f"✅ Selected: {book[1]}\nAuthor: {book[2]}\nAvailable: {book[6]} copies"
            self.selected_book_label.configure(text=book_info, text_color="white")
            
            self.update_issue_summary()
            self.check_issue_ready()
    
    def update_issue_summary(self):
        """Update the issue summary text"""
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        
        if self.selected_member_id and self.selected_book_id:
            # Get fresh data
            member = next((m for m in self.all_members if m[0] == self.selected_member_id), None)
            book = next((b for b in self.all_books if b[0] == self.selected_book_id), None)
            
            if member and book:
                due_days = self.custom_days_entry.get() or self.due_days_var.get()
                try:
                    due_days = int(due_days)
                    from datetime import datetime, timedelta
                    due_date = (datetime.now() + timedelta(days=due_days)).strftime("%Y-%m-%d")
                    
                    summary = f"""ISSUE SUMMARY:

Member: {member[1]}
Email: {member[2]}
Member ID: {member[0]}

Book: {book[1]}
Author: {book[2]}
ISBN: {book[4]}
Book ID: {book[0]}

Due Date: {due_date}
Due In: {due_days} days

Status: ✅ Ready to Issue"""
                    self.summary_text.insert("1.0", summary)
                except ValueError:
                    self.summary_text.insert("1.0", "Please enter valid number of days")
        else:
            self.summary_text.insert("1.0", "Please select both a member and a book to see issue summary")
        
        self.summary_text.configure(state="disabled")
    
    def check_issue_ready(self):
        """Check if issue can be processed"""
        if self.selected_member_id and self.selected_book_id:
            self.issue_btn.configure(state="normal")
        else:
            self.issue_btn.configure(state="disabled")
    
    def issue_book_to_member(self):
        """Process book issue"""
        if not self.selected_member_id or not self.selected_book_id:
            messagebox.showerror("Error", "Please select both member and book")
            return
        
        try:
            # Get due days
            due_days = self.custom_days_entry.get() or self.due_days_var.get()
            due_days = int(due_days)
            
            if due_days <= 0:
                messagebox.showerror("Error", "Due days must be positive")
                return
            
            # Issue the book
            success = self.db.issue_book(self.selected_book_id, self.selected_member_id, due_days)
            
            if success:
                messagebox.showinfo("Success", "Book issued successfully!")
                
                # Get details for confirmation
                member = next((m for m in self.all_members if m[0] == self.selected_member_id), None)
                book = next((b for b in self.all_books if b[0] == self.selected_book_id), None)
                
                if member and book:
                    from datetime import datetime, timedelta
                    due_date = (datetime.now() + timedelta(days=due_days)).strftime("%Y-%m-%d")
                    
                    confirmation = f"""
Book Issued Successfully!

📚 Book: {book[1]}
👤 Member: {member[1]}
📅 Due Date: {due_date}

Please remind the member to return the book on time.
"""
                    messagebox.showinfo("Issue Confirmation", confirmation)
                
                # Reset form
                self.clear_issue_selection()
            else:
                messagebox.showerror("Error", "Failed to issue book. Book might not be available.")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid number of days")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def clear_issue_selection(self):
        """Clear all selections in issue form"""
        self.selected_member_id = None
        self.selected_book_id = None
        
        self.member_search_issue.delete(0, 'end')
        self.book_search_issue.delete(0, 'end')
        self.custom_days_entry.delete(0, 'end')
        self.due_days_var.set("14")
        
        self.selected_member_label.configure(text="No member selected", text_color="gray")
        self.selected_book_label.configure(text="No book selected", text_color="gray")
        
        self.members_listbox.selection_clear(0, ctk.END)
        self.books_listbox.selection_clear(0, ctk.END)
        
        self.load_all_members_for_issue()
        self.load_all_books_for_issue()
        self.update_issue_summary()
        self.check_issue_ready()
    
    def show_return(self):
        """Show book return form"""
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame, 
            text="Return Book", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Main return form frame
        main_frame = ctk.CTkFrame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Active issues list
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        
        ctk.CTkLabel(
            left_frame, 
            text="Active Book Issues", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        # Search and filter frame
        search_frame = ctk.CTkFrame(left_frame)
        search_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=(0, 10))
        self.return_search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Search by member name, book title, or issue ID..."
        )
        self.return_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.return_search_entry.bind('<KeyRelease>', self.search_active_issues)
        
        ctk.CTkButton(
            search_frame, 
            text="Search", 
            command=self.search_active_issues
        ).pack(side="right", padx=(0, 10))
        
        ctk.CTkButton(
            search_frame, 
            text="Show All", 
            command=self.load_active_issues,
            fg_color="gray40"
        ).pack(side="right")
        
        # Active issues treeview
        tree_frame = ctk.CTkFrame(left_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("Issue ID", "Book Title", "Member Name", "Issue Date", "Due Date", "Days Overdue")
        self.issues_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        column_widths = {
            "Issue ID": 80, "Book Title": 200, "Member Name": 150, 
            "Issue Date": 100, "Due Date": 100, "Days Overdue": 100
        }
        
        for col in columns:
            self.issues_tree.heading(col, text=col)
            self.issues_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.issues_tree.yview)
        self.issues_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.issues_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        # Bind selection event
        self.issues_tree.bind('<<TreeviewSelect>>', self.on_issue_select)
        
        # Right side - Return details and action
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", padx=(10, 0), pady=10, ipadx=10)
        
        ctk.CTkLabel(
            right_frame, 
            text="Return Details", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        # Selected issue details
        details_frame = ctk.CTkFrame(right_frame)
        details_frame.pack(fill="x", padx=10, pady=10)
        
        self.details_text = ctk.CTkTextbox(details_frame, height=200, state="disabled")
        self.details_text.pack(fill="x", pady=5)
        
        # Fine calculation frame
        fine_frame = ctk.CTkFrame(right_frame)
        fine_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(fine_frame, text="Fine Calculation", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 10))
        
        # Fine settings
        fine_settings_frame = ctk.CTkFrame(fine_frame)
        fine_settings_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(fine_settings_frame, text="Fine per day:").pack(side="left", padx=(0, 10))
        self.fine_per_day = ctk.CTkEntry(fine_settings_frame, width=80, placeholder_text="10")
        self.fine_per_day.insert(0, "10")
        self.fine_per_day.pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(fine_settings_frame, text="Grace period (days):").pack(side="left", padx=(0, 10))
        self.grace_period = ctk.CTkEntry(fine_settings_frame, width=80, placeholder_text="3")
        self.grace_period.insert(0, "3")
        self.grace_period.pack(side="left")
        
        # Fine display
        self.fine_display_frame = ctk.CTkFrame(fine_frame)
        self.fine_display_frame.pack(fill="x", pady=5)
        
        self.fine_label = ctk.CTkLabel(
            self.fine_display_frame, 
            text="No fine applicable", 
            font=ctk.CTkFont(size=14)
        )
        self.fine_label.pack(pady=10)
        
        # Action buttons
        action_frame = ctk.CTkFrame(right_frame)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        self.return_btn = ctk.CTkButton(
            action_frame,
            text="Process Return",
            command=self.process_return,
            state="disabled",
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            height=40
        )
        self.return_btn.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            action_frame,
            text="Clear Selection",
            command=self.clear_return_selection,
            fg_color="#757575",
            hover_color="#424242"
        ).pack(fill="x", pady=5)
        
        # Statistics frame
        stats_frame = ctk.CTkFrame(right_frame)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(stats_frame, text="Quick Stats", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 10))
        
        self.stats_label = ctk.CTkLabel(
            stats_frame, 
            text="Loading statistics...", 
            font=ctk.CTkFont(size=12)
        )
        self.stats_label.pack(pady=5)
        
        # Initialize
        self.selected_issue_id = None
        self.load_active_issues()
        self.update_return_stats()
    
    def load_active_issues(self):
        """Load all active issues"""
        issues = self.db.get_active_issues()
        self.all_issues = issues
        self.filtered_issues = issues.copy()
        self.update_issues_treeview()
    
    def update_issues_treeview(self):
        """Update issues treeview with filtered results"""
        # Clear existing items
        for item in self.issues_tree.get_children():
            self.issues_tree.delete(item)
        
        from datetime import datetime
        
        for issue in self.filtered_issues:
            issue_id, book_title, member_name, issue_date, due_date = issue
            
            # Calculate days overdue
            due_datetime = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
            today = datetime.now()
            days_overdue = (today - due_datetime).days
            
            # Format dates for display
            issue_date_display = issue_date.split()[0] if issue_date else "N/A"
            due_date_display = due_date.split()[0] if due_date else "N/A"
            
            values = (issue_id, book_title, member_name, issue_date_display, due_date_display, days_overdue)
            
            # Color code overdue issues
            if days_overdue > 0:
                self.issues_tree.insert("", "end", values=values, tags=('overdue',))
            else:
                self.issues_tree.insert("", "end", values=values)
        
        # Configure tag for overdue items
        self.issues_tree.tag_configure('overdue', background='#ffebee')
    
    def search_active_issues(self, event=None):
        """Search active issues in real-time"""
        search_term = self.return_search_entry.get().lower()
        if not search_term:
            self.filtered_issues = self.all_issues.copy()
        else:
            self.filtered_issues = [
                issue for issue in self.all_issues 
                if (search_term in str(issue[0]).lower() or      # issue_id
                    search_term in issue[1].lower() or           # book_title
                    search_term in issue[2].lower())             # member_name
            ]
        self.update_issues_treeview()
    
    def on_issue_select(self, event):
        """Handle issue selection"""
        selection = self.issues_tree.selection()
        if selection:
            item = selection[0]
            issue_data = self.issues_tree.item(item, 'values')
            self.selected_issue_id = issue_data[0]  # issue_id
            
            # Update details
            self.update_issue_details()
            self.calculate_fine()
            self.return_btn.configure(state="normal")
    
    def update_issue_details(self):
        """Update issue details in the text box"""
        if not self.selected_issue_id:
            return
        
        # Find the selected issue
        selected_issue = None
        for issue in self.all_issues:
            if issue[0] == self.selected_issue_id:
                selected_issue = issue
                break
        
        if selected_issue:
            issue_id, book_title, member_name, issue_date, due_date = selected_issue
            
            from datetime import datetime
            
            # Calculate status
            due_datetime = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
            today = datetime.now()
            days_overdue = (today - due_datetime).days
            status = "Overdue" if days_overdue > 0 else "On Time"
            
            details = f"""📋 ISSUE DETAILS
────────────────────────
📚 Book: {book_title}
👤 Member: {member_name}
🆔 Issue ID: {issue_id}

📅 Issue Date: {issue_date.split()[0]}
⏰ Due Date: {due_date.split()[0]}
📊 Status: {status}

"""
            
            if days_overdue > 0:
                details += f"⚠️  Overdue by: {days_overdue} days\n"
            else:
                days_remaining = (due_datetime - today).days
                if days_remaining >= 0:
                    details += f"✅ Days remaining: {days_remaining} days\n"
                else:
                    details += f"✅ Returned on time\n"
            
            self.details_text.configure(state="normal")
            self.details_text.delete("1.0", "end")
            self.details_text.insert("1.0", details)
            self.details_text.configure(state="disabled")
    
    def calculate_fine(self):
        """Calculate fine for overdue book"""
        if not self.selected_issue_id:
            return
        
        try:
            # Get fine settings
            fine_per_day = float(self.fine_per_day.get() or 10)
            grace_period = int(self.grace_period.get() or 3)
            
            # Find the selected issue
            selected_issue = None
            for issue in self.all_issues:
                if issue[0] == self.selected_issue_id:
                    selected_issue = issue
                    break
            
            if selected_issue:
                from datetime import datetime
                
                issue_id, book_title, member_name, issue_date, due_date = selected_issue
                due_datetime = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
                today = datetime.now()
                days_overdue = (today - due_datetime).days - grace_period
                
                if days_overdue > 0:
                    fine_amount = days_overdue * fine_per_day
                    self.fine_label.configure(
                        text=f"Fine Amount: ₹{fine_amount:.2f}\n({days_overdue} days × ₹{fine_per_day}/day)",
                        text_color="#D32F2F"
                    )
                    self.fine_display_frame.configure(fg_color="#ffebee")
                else:
                    self.fine_label.configure(
                        text="No fine applicable - Within grace period",
                        text_color="#388E3C"
                    )
                    self.fine_display_frame.configure(fg_color="#e8f5e8")
            
        except ValueError:
            self.fine_label.configure(
                text="Invalid fine settings",
                text_color="#F57C00"
            )
    
    def process_return(self):
        """Process book return"""
        if not self.selected_issue_id:
            messagebox.showerror("Error", "Please select an issue to return")
            return
        
        try:
            # Calculate final fine
            fine_per_day = float(self.fine_per_day.get() or 10)
            grace_period = int(self.grace_period.get() or 3)
            fine_amount = 0
            
            # Get issue details for fine calculation
            selected_issue = None
            for issue in self.all_issues:
                if issue[0] == self.selected_issue_id:
                    selected_issue = issue
                    break
            
            if selected_issue:
                from datetime import datetime
                issue_id, book_title, member_name, issue_date, due_date = selected_issue
                due_datetime = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
                today = datetime.now()
                days_overdue = (today - due_datetime).days - grace_period
                
                if days_overdue > 0:
                    fine_amount = days_overdue * fine_per_day
            
            # Confirm return
            confirm_msg = f"Process return for:\n\nBook: {book_title}\nMember: {member_name}"
            if fine_amount > 0:
                confirm_msg += f"\n\nFine Amount: ₹{fine_amount:.2f}"
            
            confirm = messagebox.askyesno("Confirm Return", confirm_msg)
            
            if confirm:
                # Process return in database
                success = self.db.return_book(self.selected_issue_id)
                
                if success:
                    # Record fine if applicable
                    if fine_amount > 0:
                        self.db.record_fine(self.selected_issue_id, fine_amount)
                    
                    messagebox.showinfo(
                        "Success", 
                        f"Book returned successfully!\n\n"
                        f"Book: {book_title}\n"
                        f"Member: {member_name}\n"
                        f"{f'Fine Collected: ₹{fine_amount:.2f}' if fine_amount > 0 else 'No fine applied'}"
                    )
                    
                    # Refresh data
                    self.clear_return_selection()
                    self.load_active_issues()
                    self.update_return_stats()
                else:
                    messagebox.showerror("Error", "Failed to process return")
                    
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def clear_return_selection(self):
        """Clear return selection"""
        self.selected_issue_id = None
        self.issues_tree.selection_remove(self.issues_tree.selection())
        
        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", "Select an issue from the list to view details...")
        self.details_text.configure(state="disabled")
        
        self.fine_label.configure(text="No fine applicable", text_color="gray")
        self.fine_display_frame.configure(fg_color="transparent")
        
        self.return_btn.configure(state="disabled")
    
    def update_return_stats(self):
        """Update return statistics"""
        if not self.all_issues:
            self.stats_label.configure(text="No active issues")
            return
        
        from datetime import datetime
        
        total_issues = len(self.all_issues)
        overdue_issues = 0
        total_fine = 0
        
        fine_per_day = float(self.fine_per_day.get() or 10)
        grace_period = int(self.grace_period.get() or 3)
        
        for issue in self.all_issues:
            issue_id, book_title, member_name, issue_date, due_date = issue
            due_datetime = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
            today = datetime.now()
            days_overdue = (today - due_datetime).days - grace_period
            
            if days_overdue > 0:
                overdue_issues += 1
                total_fine += days_overdue * fine_per_day
        
        stats_text = f"""📊 Active Issues: {total_issues}
⚠️  Overdue: {overdue_issues}
💰 Potential Fine: ₹{total_fine:.2f}"""
        
        self.stats_label.configure(text=stats_text)
    
    def show_issues(self):
        """Show active issues"""
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame, 
            text="Active Issues", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Active issues list implementation
        # ... (code for issues list)

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = LibraryManagementSystem()
    app.run()