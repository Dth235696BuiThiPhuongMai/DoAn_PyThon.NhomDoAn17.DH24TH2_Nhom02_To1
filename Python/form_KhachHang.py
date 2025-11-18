import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
import pyodbc

conn = pyodbc.connect(
    'DRIVER={SQL Server};'
   #'SERVER=ADMIN-PC;'
    'SERVER=localhost\\SQLEXPRESS01;'
    'DATABASE=QuanLyTuyenDuLich;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

root = tk.Tk()
root.title("Quản Lý Khách Hàng")
root.geometry("1000x650")
root.configure(bg="#FFFACD")

frame_tree = tk.LabelFrame(root, text="Danh sách khách hàng", font=("Times New Roman", 12), bg="#fff8dc", width=800, height=400)
frame_tree.place(x=50, y=200)

columns = ("maKh", "hoTen", "sdt", "phai", "ngsinh", "dchi")
tree = ttk.Treeview(frame_tree, columns=columns, show="headings")
tree.heading("maKh", text="Mã Khách Hàng")
tree.heading("hoTen", text="Họ tên")
tree.heading("sdt", text="Số điện thoại")
tree.heading("phai", text="Giới Tính")
tree.heading("ngsinh", text="Ngày Sinh")
tree.heading("dchi", text="Địa Chỉ")

tree.column("maKh", width = 100, anchor="center")
tree.column("hoTen", width = 150)
tree.column("sdt", width = 120, anchor="center")
tree.column("phai", width = 80, anchor="center")
tree.column("ngsinh", width = 100, anchor="center")
tree.column("dchi", width = 250)

scrollbar_v = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview) #dọc
scrollbar_h = ttk.Scrollbar(frame_tree, orient="horizontal", command=tree.xview) #ngang
tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
tree.place(x=10, y=10, width=760, height=340)

scrollbar_v.place(x=770, y=10, width=20, height=360)
scrollbar_h.place(x=10, y=350, width=750, height=20)

def load_data():
    for i in tree.get_children():
        tree.delete(i)

    cursor.execute("SELECT maKH, hoTen, sdt, phai, ngsinh, dchi FROM KHACHHANG")
    rows = cursor.fetchall()
    
    for row in rows:
        tree.insert("", "end", values=(row[0].strip(), row[1].strip(), row[2], row[3], row[4], row[5].strip()))

def auto_maKh():
    if reusable_ids:
        return reusable_ids.pop(0)

    ma_list = [tree.item(item)['values'][0].strip() for item in tree.get_children()]
    
    if not ma_list:
        return "KH0001"
    
    so_list = sorted([int(ma[2:]) for ma in ma_list if ma[2:].isdigit()])

    next_num = 1
    for num in so_list:
        if num == next_num:
            next_num += 1
        elif num > next_num:
            break
    return f"KH{next_num:04d}"

def lam_moi_form():
    entry_maKH.config(state='normal')
    entry_maKH.delete(0, tk.END)
    entry_maKH.insert(0, auto_maKh())
    entry_maKH.config(state='readonly')

    entry_ten.delete(0, tk.END)
    entry_sdt.delete(0, tk.END)
    entry_diachi.delete(0, tk.END)
    gender.set("Nam")
    date_ngaysinh.set_date(date.today())

def them():
    maKH = auto_maKh()
    hoTen = entry_ten.get().strip()
    sdt = entry_sdt.get()
    phai = gender.get()  
    ngsinh = date_ngaysinh.get_date()
    dchi = entry_diachi.get().strip()

    if not (hoTen or sdt):
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ thông tin!")
        return
    if not (sdt.isdigit() and len(sdt) == 10 and sdt.startswith("0")):
        messagebox.showerror("Lỗi", "Số điện thoại phải bắt đầu bằng 0 và đủ 10 số!")
        return
    for item in tree.get_children():
        sdt_in_tree = str(tree.item(item)['values'][2]).zfill(10)
        if sdt_in_tree == sdt:
            messagebox.showerror("Lỗi","Số điện thoại đã tồn tại!")
            return

    tree.insert("", "end", values=(maKH, hoTen, sdt, phai, ngsinh, dchi))
    messagebox.showinfo("Thành công", f"Đã thêm khách hàng {hoTen} với mã {maKH}")
    lam_moi_form()

deleted_items = []  # danh sách toàn cục
reusable_ids = [] # cắt mã đã bị xoá

def xoa():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Vui lòng chọn khách hàng để xóa!")
        return
    
    confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa?")
    if confirm:
        maKH = tree.item(selected[0])['values'][0]
        deleted_items.append(maKH)
        tree.delete(selected[0])
        lam_moi_form()

def sua():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Vui lòng chọn khách hàng để sửa!")
        return

    maKH = tree.item(selected[0])['values'][0].strip()
    hoTen = entry_ten.get().strip()
    sdt = entry_sdt.get().strip()
    phai = gender.get()
    ngsinh = date_ngaysinh.get_date()
    dchi = entry_diachi.get().strip()
    messagebox.showinfo("Thành công","Đã cập nhật thông tin khách hàng")

    tree.item(selected[0], values=(maKH, hoTen, sdt, phai, ngsinh, dchi))

def luu():
    for item in tree.get_children():
        maKH, hoTen, sdt, phai, ngsinh, dchi = tree.item(item, "values")

        if not (sdt.isdigit() and len(sdt) == 10 and sdt.startswith("0")):
            messagebox.showwarning("Bỏ qua", f"SĐT {sdt} của {hoTen} không hợp lệ, không lưu vào CSDL!")
            continue

        cursor.execute("SELECT 1 FROM KHACHHANG WHERE maKH=?", (maKH,))

        if cursor.fetchone():
            cursor.execute(
                "UPDATE KHACHHANG SET hoTen=?, sdt=?, phai=?, ngsinh=?, dchi=? WHERE maKH=?",
                (hoTen, sdt, phai, ngsinh, dchi, maKH)
            )
        else:
            cursor.execute(
                "INSERT INTO KHACHHANG (maKH, hoTen, sdt, phai, ngsinh, dchi) VALUES (?, ?, ?, ?, ?, ?)",
                (maKH, hoTen, sdt, phai, ngsinh, dchi)
            )

    for maKH in deleted_items:
        cursor.execute("DELETE FROM KHACHHANG WHERE maKH=?", (maKH,))
    deleted_items.clear()

    conn.commit()
    messagebox.showinfo("Thành công", "Đã lưu dữ liệu vào CSDL!")
    load_data()
    lam_moi_form()

def hien_thi_chi_tiet(event):
    selected = tree.selection()
    if selected:
        ma, ten, sdt, phai_val, ngsinh, dchi = tree.item(selected[0], "values")
        entry_maKH.config(state='normal')
        entry_maKH.delete(0, tk.END)
        entry_maKH.insert(0, ma)
        entry_maKH.config(state='readonly')

        entry_ten.delete(0, tk.END)
        entry_ten.insert(0, ten)

        entry_sdt.delete(0, tk.END)
        entry_sdt.insert(0, sdt)

        gender.set(phai_val)

        if isinstance(ngsinh, str):
            year, month, day = map(int, ngsinh.split('-'))
            date_ngaysinh.set_date(date(year, month, day))
        else:
            date_ngaysinh.set_date(ngsinh)

        entry_diachi.delete(0, tk.END)
        entry_diachi.insert(0, dchi)

def huy():
    lam_moi_form()

def thoat():
    root.destroy()


tk.Label(root, text="Quản Lý Khách Hàng", bg="#FFFACD", fg="black", font=("Times New Roman", 22, "bold")).place(x=330, y=20)

frame_input = tk.Frame(root, bg="#FFFACD", width=900, height=120)
frame_input.place(x=50, y=70)

tk.Label(frame_input, text="Mã Khách Hàng", bg="#FFFACD").place(x=10, y=10)
entry_maKH = tk.Entry(frame_input, width=10)
entry_maKH.place(x=130, y=10)
entry_maKH.config(state='readonly')

tk.Label(frame_input, text="Tên Khách Hàng", bg="#FFFACD").place(x=200, y=10)
entry_ten = tk.Entry(frame_input, width=30)
entry_ten.place(x=320, y=10)

tk.Label(frame_input, text="Giới Tính", bg="#FFFACD").place(x=10, y=50)
gender = tk.StringVar(value="Nam")
tk.Radiobutton(frame_input, text="Nam", variable=gender, value="Nam", bg="#FFFACD").place(x=70, y=48)
tk.Radiobutton(frame_input, text="Nữ", variable=gender, value="Nữ", bg="#FFFACD").place(x=130, y=48)

tk.Label(frame_input, text="Ngày Sinh", bg="#FFFACD").place(x=200, y=50)
date_ngaysinh = DateEntry(frame_input, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
date_ngaysinh.place(x=280, y=50)

tk.Label(frame_input, text="Số Điện Thoại", bg="#FFFACD").place(x=400, y=50)
entry_sdt = tk.Entry(frame_input, width=30)
entry_sdt.place(x=530, y=50)

tk.Label(frame_input, text="Địa Chỉ", bg="#FFFACD").place(x=10, y=90)
entry_diachi = tk.Entry(frame_input, width=70)
entry_diachi.place(x=130, y=90)

tree.bind("<<TreeviewSelect>>", hien_thi_chi_tiet)

button_style = {"font": ("Times New Roman", 13, "bold"), "bg": "#B0E0E6", "width": 8, "height": 1}
tk.Button(root, text="Thêm", **button_style, command=them).place(x=870, y=120)
tk.Button(root, text="Xóa", **button_style, command=xoa).place(x=870, y=200)
tk.Button(root, text="Sửa", **button_style, command=sua).place(x=870, y=280)
tk.Button(root, text="Hủy", **button_style, command=huy).place(x=870, y=360)
tk.Button(root, text="Lưu", **button_style, command=luu).place(x=870, y=440)
tk.Button(root, text="Thoát", **button_style, command=thoat).place(x=870, y=520)

load_data()
lam_moi_form()

root.mainloop()