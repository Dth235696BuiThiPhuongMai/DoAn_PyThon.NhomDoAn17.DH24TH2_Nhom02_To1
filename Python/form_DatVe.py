import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc
from datetime import datetime, date

conn = pyodbc.connect(
    'DRIVER={SQL Server};'
   #'SERVER=ADMIN-PC;'
    'SERVER=localhost\\SQLEXPRESS01;'
    'DATABASE=QuanLyTuyenDuLich;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

root = tk.Tk()
root.title("Quản Lý Đặt Vé")
root.geometry("1000x650")
root.config(bg="#fff8dc")

frame_tree = tk.LabelFrame(root, text="Thông Tin Đặt Vé", font=("Arial", 12, "bold"), bg="#fff8dc", width=790, height=400)
frame_tree.place(x=50, y=250)

columns = ("maVe", "maCD", "maKH", "ngDat", "trangThai", "giaVe", "soLuong", "thanhTien")
tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10)
tree.heading("maVe", text="Mã Vé")
tree.heading("maCD", text="Mã Chuyến Đi")
tree.heading("maKH", text="Mã Khách Hàng")
tree.heading("ngDat", text="Ngày Đặt")
tree.heading("soLuong", text="Số Lượng")
tree.heading("giaVe", text="Giá Vé")
tree.heading("trangThai", text="Trạng Thái")
tree.heading("thanhTien", text="Thành Tiền")

tree.column("maVe", width=90, anchor="center")
tree.column("maCD", width=90, anchor="center")
tree.column("maKH", width=95, anchor="center")
tree.column("ngDat", width=80, anchor="center")
tree.column("soLuong", width=70, anchor="center")
tree.column("giaVe", width=90, anchor="center")
tree.column("trangThai", width=100, anchor="center")
tree.column("thanhTien", width=120, anchor="center")

scrollbar_v = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
scrollbar_h = ttk.Scrollbar(frame_tree, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
tree.place(x=10, y=10, width=750, height=340)
scrollbar_v.place(x=765, y=10, width=15, height=350)
scrollbar_h.place(x=10, y=355, width=755, height=15)

def load_data():
    for i in tree.get_children():
        tree.delete(i)
    cursor.execute("SELECT maVe, maCD, maKH, ngDat, trangThai, giaVe, soluong, thanhTien FROM DATVE")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=(row[0].strip(), row[1].strip(), row[2].strip(), row[3], row[4], row[5], row[6], row[7]))

def auto_maVe():
    cursor.execute("SELECT maVe FROM DATVE")
    ma_list = [row[0] for row in cursor.fetchall()]
    if not ma_list:
        return "VE00000001"
    so_list = sorted([int(ma[2:]) for ma in ma_list if ma[2:].isdigit()])
    next_num = 1
    for num in so_list:
        if num == next_num:
            next_num += 1
        elif num > next_num:
            break
    return f"VE{next_num:08d}"

def lay_danh_sach_ma_khach_hang():
    cursor.execute("SELECT maKh FROM KHACHHANG")
    data = cursor.fetchall()
    ds_ma = [row[0] for row in data]  # lấy cột maKh
    return ds_ma

def lay_danh_sach_ma_chuyen_di():
    cursor.execute("SELECT maCD FROM CHUYENDI")
    data = cursor.fetchall()
    ds_cd = [row[0] for row in data]  # lấy cột maKh
    return ds_cd

def lam_moi_form():
    entry_maVe.config(state='normal')
    entry_maVe.delete(0, tk.END)
    entry_maVe.insert(0, auto_maVe())
    entry_maVe.config(state='readonly')

    entry_maKH.set("")
    entry_maCD.set("")
    date_ngDat.set_date(date.today())
    entry_trangThai.delete(0, tk.END)
    entry_giaVe.delete(0, tk.END)
    spin_soLuong.delete(0, tk.END)

def them():
    maVe = auto_maVe()
    maKH = entry_maKH.get().strip()
    maCD = entry_maCD.get().strip()
    ngDat = date_ngDat.get_date().strftime('%Y-%m-%d')
    trangThai = entry_trangThai.get().strip()
    giaVe = float(entry_giaVe.get().strip())
    soluong = int(spin_soLuong.get().strip())
    thanhTien = giaVe * soluong

    if not trangThai or not giaVe or not soluong:
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ thông tin!")
        return

    tree.insert("", "end", values=(maVe,  maCD, maKH, ngDat, trangThai, giaVe, soluong, thanhTien))
    lam_moi_form()

def xoa():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Vui lòng chọn vé để xóa!")
        return
    confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa?")
    if confirm:
        tree.delete(selected[0])
        lam_moi_form()

def sua():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Vui lòng chọn khách hàng để sửa!")
        return

    maVe = tree.item(selected[0])['values'][0]
    maCD = entry_maCD.get().strip()
    maKH = entry_maKH.get().strip()
    ngDat = date_ngDat.get_date().strftime('%Y-%m-%d')
    trangThai = entry_trangThai.get().strip()
    giaVe = float(entry_giaVe.get().strip())
    soluong = int(spin_soLuong.get().strip())
    thanhTien = giaVe * soluong


    messagebox.showinfo("Thành công","Đã cập nhật thông tin khách hàng")

    tree.item(selected[0], values=(maVe,  maCD, maKH, ngDat, trangThai, giaVe, soluong, thanhTien))
    
deleted_items = []  # danh sách toàn cục

def luu():
    for item in tree.get_children():
        maVe,  maCD, maKH, ngDat, trangThai, giaVe, soluong, thanhTien = tree.item(item, "values")

        cursor.execute("SELECT 1 FROM DATVE WHERE maVe=?", (maVe,))

        if cursor.fetchone():
            cursor.execute(
                "UPDATE DATVE SET maCD=?, maKH=?, ngDat=?, trangThai=?, giaVe=?, soluong=?, thanhTien=? WHERE maVe=?",
                (maCD, maKH, ngDat, trangThai, giaVe, soluong, thanhTien, maVe)
            )
        else:
            cursor.execute(
                "INSERT INTO DATVE (maVe, maCD, maKH, ngDat, trangThai, giaVe, soluong, thanhTien) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (maVe, maCD, maKH, ngDat, trangThai, giaVe, soluong, thanhTien)
            )

    for maKH in deleted_items:
        cursor.execute("DELETE FROM KHACHHANG WHERE maKH=?", (maKH,))
    deleted_items.clear()

    conn.commit()
    messagebox.showinfo("Thành công", "Đã lưu dữ liệu vào CSDL!")
    load_data()
    lam_moi_form()

def huy():
    lam_moi_form()

def hien_thi_chi_tiet(event=None):
    selected = tree.selection()
    if selected:
        maVe, maCD, maKh, ngDat, trangThai, giaVe, soluong, _ = tree.item(selected[0], "values")

        entry_maVe.config(state='normal')
        entry_maVe.delete(0, tk.END)
        entry_maVe.insert(0, maVe)
        entry_maVe.config(state='readonly')

        entry_maKH.set(maKh)
        entry_maCD.set(maCD)

        ngay = datetime.strptime(ngDat, '%Y-%m-%d').date()
        date_ngDat.set_date(ngay)

        entry_trangThai.set(trangThai)

        entry_giaVe.delete(0, tk.END)
        entry_giaVe.insert(0, giaVe)

        spin_soLuong.delete(0, tk.END)
        spin_soLuong.insert(0, soluong)

        giaVe = float(giaVe)
        soluong = int(soluong)
        
def thoat():
    root.destroy()

btn_home = tk.Button(root, text="Về Trang Chủ", font=("Times New Roman", 10, "bold"), bg="white", relief="groove", command=quit)
btn_home.place(x=50, y=30)

title_label = tk.Label(root, text="Quản Lý Đặt Vé", font=("Arial", 20, "bold"), bg="#fff8dc")
title_label.place(x=400, y=45)

frame_tree = tk.Frame(root, bg="#fff8dc")
frame_tree.place(x=100, y=100)

tk.Label(frame_tree, text="Mã Vé", bg="#fff8dc", font=("Times New Roman", 12)).grid(row=0, column=0, sticky="w", pady=5)
entry_maVe = tk.Entry(frame_tree, width=30)
entry_maVe.grid(row=0, column=1, padx=10, pady=5)
entry_maVe.config(state='readonly')

tk.Label(frame_tree, text="Số Lượng", font=("Times New Roman", 12), bg="#fff8dc").grid(row=0, column=2, sticky="w", padx=10, pady=5)
spin_soLuong = tk.Spinbox(frame_tree, from_=1, to=100, width=10)
spin_soLuong.grid(row=0, column=3, padx=10, pady=5, columnspan=2)

tk.Label(frame_tree, text="Mã Chuyến Đi", bg="#fff8dc", font=("Times New Roman", 12)).grid(row=2, column=0, sticky="w", pady=5)
entry_maCD = ttk.Combobox(frame_tree, width=30, values=lay_danh_sach_ma_chuyen_di(),state="readonly")
entry_maCD.grid(row=2, column=1, padx=10, pady=5)
entry_maCD.set("")

tk.Label(frame_tree, text="Giá Vé", bg="#fff8dc", font=("Times New Roman", 12)).grid(row=1, column=2, sticky="w", padx=10)
entry_giaVe = tk.Entry(frame_tree, width=30)
entry_giaVe.grid(row=1, column=3, padx=10, pady=5, columnspan=2)

tk.Label(frame_tree, text="Mã Khách Hàng", bg="#fff8dc", font=("Times New Roman", 12)).grid(row=1, column=0, sticky="w", pady=5)
entry_maKH = ttk.Combobox(frame_tree, width=30, state='readonly', values=lay_danh_sach_ma_khach_hang())
entry_maKH.grid(row=1, column=1, padx=10, pady=5)
entry_maKH.set("")

tk.Label(frame_tree, text="Trạng Thái", bg="#fff8dc", font=("Times New Roman", 12)).grid(row=2, column=2, sticky="w", padx=10)
entry_trangThai = ttk.Combobox(frame_tree, width=30, values=["đã thanh toán","chưa thanh toán"], state='readonly')
entry_trangThai.grid(row=2, column=3, padx=10, pady=5, columnspan=2)
entry_trangThai.set("")

tk.Label(frame_tree, text="Ngày Đặt", bg="#fff8dc", font=("Times New Roman", 12)).grid(row=3, column=0, sticky="w", padx=5)
date_ngDat = DateEntry(frame_tree, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='d/m/yyyy')
date_ngDat.grid(row=3, column=1, padx=10, pady=5)


button_style = {"font": ("Times New Roman", 13, "bold"), "bg": "#B0E0E6", "width": 8, "height": 1}

btn_them = tk.Button(root, text="Thêm", **button_style, command=them)
btn_them.place(x=880, y=130)

btn_xoa = tk.Button(root, text="Xóa", **button_style, command=xoa)
btn_xoa.place(x=880, y=210)

btn_sua = tk.Button(root, text="Sửa", **button_style, command=sua)
btn_sua.place(x=880, y=290)

btn_huy = tk.Button(root, text="Hủy", **button_style, command=huy)
btn_huy.place(x=880, y=370)

btn_luu = tk.Button(root, text="Lưu", **button_style, command=luu)
btn_luu.place(x=880, y=450)

btn_thoat = tk.Button(root, text="Thoát", **button_style, command=thoat)
btn_thoat.place(x=880, y=530)

tree.bind("<<TreeviewSelect>>", hien_thi_chi_tiet)

lam_moi_form()
load_data()

root.mainloop()