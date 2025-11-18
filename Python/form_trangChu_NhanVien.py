import tkinter as tk
import pyodbc
import subprocess

conn = pyodbc.connect(
            'DRIVER={SQL Server};'
           #'SERVER=ADMIN-PC;'
            'SERVER=localhost\\SQLEXPRESS01;'
            'DATABASE=QuanLyTuyenDuLich;'
            'Trusted_Connection=yes;'
        )
cursor = conn.cursor()

def open_form_KhachHang():
    subprocess.Popen(["python", "form_KhachHang.py"])

def open_form_ChuyenDi():
    subprocess.Popen(["python", "form_NhanVien.py"])

def open_form_DatVe():
    subprocess.Popen(["python", "form_DatVe.py"])

def open_form_TuyenDuLich():
    subprocess.Popen(["python", "form_TuyenDuLich.py"])

def thoat():
    root.destroy()

root = tk.Tk()
root.title("Trang Chủ - Nhân Viên")
root.geometry("1000x650")
root.configure(bg="#FFFACD")

frame = tk.Frame(root, bg="#FFFACD", padx=40, pady=40, relief="groove", bd=2)
frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(frame, text="Trang Chủ", font=("Arial", 26, "bold"), bg="#FFFACD").grid(row=0, column=0, columnspan=2, pady=20)

tk.Button(frame, text="Quản Lý Khách Hàng", bg="#ADD8E6", font=("Arial", 14), width=20, height=2, command=open_form_KhachHang).grid(row=1, column=0, padx=30, pady=20)
tk.Button(frame, text="Quản Lý Chuyến Đi", bg="#ADD8E6", font=("Arial", 14), width=20, height=2, command=open_form_ChuyenDi).grid(row=1, column=1, padx=30, pady=20)

tk.Button(frame, text="Quản Lý Đặt Vé", bg="#ADD8E6", font=("Arial", 14), width=20, height=2, command=open_form_DatVe).grid(row=2, column=0, padx=30, pady=20)
tk.Button(frame, text="Quản Lý Tuyến Du Lịch", bg="#ADD8E6", font=("Arial", 14), width=20, height=2, command=open_form_TuyenDuLich).grid(row=2, column=1, padx=30, pady=20)

tk.Button(root, text="Thoát", font=("Arial", 12), command=thoat).place(x=920, y=600)

root.mainloop()