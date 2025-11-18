import tkinter as tk
from tkinter import messagebox
import pyodbc
import subprocess


def login():
    username = entry_user.get()
    password = entry_pass.get()

    conn = pyodbc.connect(
            'DRIVER={SQL Server};'
           #'SERVER=ADMIN-PC;'
            'SERVER=localhost\\SQLEXPRESS01;'
            'DATABASE=QuanLyTuyenDuLich;'
            'Trusted_Connection=yes;'    
        )
    cursor = conn.cursor()
    cursor.execute("SELECT VaiTro FROM TaiKhoan WHERE TenDangNhap=? AND MatKhau=?", (username, password))
    result = cursor.fetchone()
        
    if result:
            role = result[0]
            if role == "QuanLy":
                subprocess.Popen(["python", "form_trangChu_QuanLy.py"])
            elif role == "NhanVien":
                subprocess.Popen(["python", "form_trangChu_NhanVien.py"])  
    else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu!")
    conn.close()

def thoat():
    root.destroy()

root = tk.Tk()
root.title("Login Form")
root.geometry("1000x650")
root.configure(bg="#FFFACD")


frame_login = tk.Frame(root, bg="#FFFACD", padx=40, pady=40, relief="groove", bd=2)
frame_login.place(relx=0.5, rely=0.5, anchor="center")

label_title = tk.Label(frame_login, text="Login", font=("Arial", 26, "bold"), bg="#FFFACD")
label_title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

label_user = tk.Label(frame_login, text="User:", font=("Arial", 16), bg="#FFFACD")
label_user.grid(row=1, column=0, sticky="e", pady=10, padx=10)
entry_user = tk.Entry(frame_login, width=30, font=("Arial", 14))
entry_user.grid(row=1, column=1, pady=10, padx=10)

label_pass = tk.Label(frame_login, text="Password:", font=("Arial", 16), bg="#FFFACD")
label_pass.grid(row=2, column=0, sticky="e", pady=10, padx=10)
entry_pass = tk.Entry(frame_login, width=30, show="*", font=("Arial", 14))
entry_pass.grid(row=2, column=1, pady=10, padx=10)

def on_enter(e):
    e.widget["background"] = "#7EC8E3"

def on_leave(e):
    e.widget["background"] = "#ADD8E6"

button_frame = tk.Frame(frame_login, bg="#FFFACD")
button_frame.grid(row=3, column=0, columnspan=2, pady=25)

button_ok = tk.Button(button_frame, text="OK", bg="#ADD8E6", width=12, height=1, font=("Arial", 14), command=login)
button_ok.grid(row=0, column=0, padx=20)
button_ok.bind("<Enter>", on_enter)
button_ok.bind("<Leave>", on_leave)

button_cancel = tk.Button(button_frame, text="Cancel", bg="#ADD8E6", width=12, height=1, font=("Arial", 14), command=thoat)
button_cancel.grid(row=0, column=1, padx=20)
button_cancel.bind("<Enter>", on_enter)
button_cancel.bind("<Leave>", on_leave)

entry_user.focus()

root.mainloop()