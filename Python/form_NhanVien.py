import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date, datetime
import pyodbc
import re

conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=localhost\\SQLEXPRESS01;'
    # 'SERVER=ADMIN-PC;'
    'DATABASE=QuanLyTuyenDuLich;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

root = tk.Tk()
root.title("Quản Lý Nhân Viên")
root.geometry("1000x650")
root.configure(bg="#FFFACD")

deleted_items = []
reusable_ids = []

def auto_maNV():
    ma_list_tree = [tree.item(item)['values'][0].strip() for item in tree.get_children()]

    cursor.execute("SELECT maNV FROM NHANVIEN")
    ma_list_sql = [row[0].strip() for row in cursor.fetchall()]
    
    # Gộp mã
    ma_list = list(set(ma_list_tree + ma_list_sql))
    
    if not ma_list:
        return "NV0001"
    
    so_list = sorted([int(ma[2:]) for ma in ma_list if ma[2:].isdigit()])
    next_num = so_list[-1] + 1
    return f"NV{next_num:04d}"

def load_nam():
    # lấy năm từ danh sách chuyến đi
    cursor.execute("SELECT DISTINCT YEAR(ngKh) FROM CHUYENDI ORDER BY YEAR(ngKh)")
    nam_list = [str(r[0]) for r in cursor.fetchall()]
    combo_nam['values'] = nam_list
    if nam_list:
        combo_nam.set(nam_list[0])
    else:
        combo_nam.set(str(date.today().year))

def lam_moi_form():
    tree.selection_remove(tree.selection())

    entry_maNV.config(state='normal')
    entry_maNV.delete(0, tk.END)
    entry_maNV.insert(0, auto_maNV())
    entry_maNV.config(state='readonly')

    entry_socccd.delete(0, tk.END)

    entry_hoTen.delete(0, tk.END)

    entry_sdt.delete(0, tk.END)

    combo_phai.set("Chọn giới tính")

    date_ngsinh.set_date(date.today())

    entry_dchi.delete(0, tk.END)

    combo_chucvu.set("Chọn chức vụ")

# Ẩn cột lương
def toggle_luong_visibility(show=True):
    if show:
        tree["displaycolumns"] = ("maNV","so_cccd","hoTen","sdt","phai","ngsinh","dchi","chucVu","soChuyen","luong")
    else:
        tree["displaycolumns"] = ("maNV","so_cccd","hoTen","sdt","phai","ngsinh","dchi","chucVu","soChuyen")

tree_frame = tk.LabelFrame(root, text="Danh sách nhân viên", font=("Times New Roman",12), bg="#fff8dc", width=900, height=400)
tree_frame.place(x=50, y=280)

columns = ("maNV","so_cccd","hoTen","sdt","phai","ngsinh","dchi","chucVu","soChuyen","luong")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
for col, text, width in zip(columns,
                            ["Mã NV","Số CCCD","Họ Tên","SĐT","Giới Tính","Ngày Sinh","Địa Chỉ","Chức Vụ","Số Chuyến","Lương Thực Lãnh"],
                            [80,100,150,100,60,100,150,100,80,120]):
    tree.heading(col, text=text)
    tree.column(col, width=width, anchor="center")

scrollbar_v = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview) # thanh trượt dọc
scrollbar_h = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview) # thanh trươtcj ngang
tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

tree.grid(row=0, column=0, sticky="nsew", padx=(5,0), pady=(5,0))

scrollbar_v.grid(row=0, column=1, sticky="ns", pady=(5,0))
scrollbar_h.grid(row=1, column=0, sticky="ew", padx=(5,0))

tree_frame.grid_rowconfigure(0, weight=1)
tree_frame.grid_columnconfigure(0, weight=1)

toggle_luong_visibility(False)

def load_data():
    tree.delete(*tree.get_children())
    cursor.execute("SELECT maNV, so_cccd, hoTen, sdt, phai, ngSinh, dchi, chucVu FROM NHANVIEN")
    nhanviens = cursor.fetchall()
    cursor.execute("""
        SELECT cn.maNV, COUNT(*) 
        FROM CHUYENDI_NHANVIEN cn
        JOIN CHUYENDI c ON cn.maCD = c.maCD
        GROUP BY cn.maNV
    """)
    chuyens = dict(cursor.fetchall())

    for nv in nhanviens:
        maNV, so_cccd, hoTen, sdt, phai, ngSinh, dchi, chucVu = nv
        soChuyen = chuyens.get(maNV, 0)
        if chucVu == "Cơ Trưởng":
            luong_cb = 2000000
        elif chucVu == "Hướng Dẫn Viên":
            luong_cb = 1800000
        else:
            luong_cb = 1200000
        luong_thuc = luong_cb * soChuyen
        tree.insert("", "end", values=(
            str(maNV),
            str(so_cccd).zfill(12),
            str(hoTen),
            str(sdt).zfill(10),
            str(phai),
            str(ngSinh),
            str(dchi),
            str(chucVu),
            str(soChuyen),
            str(luong_thuc)
        ))

def xem_luong():
    thang_str = combo_thang.get()
    nam_str = combo_nam.get()
    if not thang_str or not nam_str:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn tháng và năm!")
        return
    thang = int(thang_str)
    nam = int(nam_str)

    tree.delete(*tree.get_children())
    cursor.execute("SELECT maNV, so_cccd, hoTen, sdt, phai, ngSinh, dchi, chucVu FROM NHANVIEN")
    nhanviens = cursor.fetchall()

    cursor.execute("""
        SELECT cn.maNV, COUNT(*) 
        FROM CHUYENDI_NHANVIEN cn
        JOIN CHUYENDI c ON cn.maCD = c.maCD
        WHERE MONTH(c.ngKh)=? AND YEAR(c.ngKh)=? 
        GROUP BY cn.maNV
    """, (thang, nam))
    chuyens = dict(cursor.fetchall())

    for nv in nhanviens:
        maNV, so_cccd, hoTen, sdt, phai, ngSinh, dchi, chucVu = nv
        soChuyen = chuyens.get(maNV,0)
        if chucVu == "Cơ Trưởng":
            luong_cb = 2000000
        elif chucVu == "Hướng Dẫn Viên":
            luong_cb = 1800000
        else:
            luong_cb = 1200000
        luong_thuc = luong_cb * soChuyen
        tree.insert("", "end", values=(
            str(maNV),
            str(so_cccd).zfill(12),
            str(hoTen),
            str(sdt).zfill(10),
            str(phai),
            str(ngSinh),
            str(dchi),
            str(chucVu),
            str(soChuyen),
            str(luong_thuc)
        ))

    toggle_luong_visibility(True)

def kiem_tra_cccd(so_cccd: str) -> bool:
    return bool(re.fullmatch(r"0\d{11}", so_cccd))


def them():
    maNV = auto_maNV()  
    so_cccd = entry_socccd.get().strip()
    hoTen = entry_hoTen.get()
    sdt = entry_sdt.get().strip()
    phai = combo_phai.get()
    ngSinh = date_ngsinh.get_date().strftime('%Y-%m-%d')
    dchi = entry_dchi.get()
    chucVu = combo_chucvu.get()

    if not kiem_tra_cccd(so_cccd):
        messagebox.showerror("Lỗi","Số CCCD phải 12 số bắt đầu 0")
        return
    if not (hoTen and sdt and chucVu):
        messagebox.showwarning("Thiếu dữ liệu","Nhập đầy đủ thông tin!")
        return

    # Kiểm tra trùng CCCD trên Treeview
    for item in tree.get_children():
        cccd_in_tree = str(tree.item(item)['values'][1]).zfill(12)
        if cccd_in_tree == so_cccd:
            messagebox.showerror("Lỗi","Số CCCD đã tồn tại!")
            return
    # Kiểm tra trùng SĐT trên Treeview
    for item in tree.get_children():
        sdt_in_tree = str(tree.item(item)['values'][3]).zfill(10)
        if sdt_in_tree == sdt:
            messagebox.showerror("Lỗi","Số điện thoại đã tồn tại!")
            return

    tree.insert("", "end", values=(maNV, so_cccd, hoTen, sdt, phai, ngSinh, dchi, chucVu,0,0))
    lam_moi_form()

def xoa():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn","Chọn nhân viên để xóa!")
        return
    confirm = messagebox.askyesno("Xác nhận","Bạn có chắc muốn xóa?")
    if confirm:
        maNV = tree.item(selected[0])['values'][0]
        deleted_items.append(maNV)
        reusable_ids.append(maNV)
        tree.delete(selected[0])
        lam_moi_form()

def chon_nhan_vien(event):
    selected = tree.selection()
    if not selected:
        return
    item = tree.item(selected[0])['values']
    if not item:
        return

    entry_maNV.config(state='normal')
    entry_maNV.delete(0, tk.END)
    entry_maNV.insert(0, str(item[0]))
    entry_maNV.config(state='readonly')

    entry_socccd.delete(0, tk.END)
    entry_socccd.insert(0, str(item[1]).zfill(12))

    entry_hoTen.delete(0, tk.END)
    entry_hoTen.insert(0, str(item[2]))

    entry_sdt.delete(0, tk.END)
    entry_sdt.insert(0, str(item[3]).zfill(10))

    combo_phai.set(str(item[4]))
    date_ngsinh.set_date(datetime.strptime(str(item[5]), '%Y-%m-%d').date())
    entry_dchi.delete(0, tk.END)
    entry_dchi.insert(0, str(item[6]))
    combo_chucvu.set(str(item[7]))

tree.bind("<<TreeviewSelect>>", chon_nhan_vien)

def sua():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn","Chọn nhân viên để sửa!")
        return
    
    maNV = tree.item(selected[0])['values'][0]
    so_cccd = entry_socccd.get().strip().zfill(12)
    sdt = entry_sdt.get().strip().zfill(10)

    # Kiểm tra CCCD hợp lệ và trùng
    if not kiem_tra_cccd(so_cccd):
        messagebox.showerror("Lỗi","CCCD phải 12 số bắt đầu 0")
        return
    for item in tree.get_children():
        if tree.item(item)['values'][1] == so_cccd and tree.item(item)['values'][0] != maNV:
            messagebox.showerror("Lỗi","CCCD đã tồn tại!")
            return

    hoTen = entry_hoTen.get()
    sdt = entry_sdt.get()
    phai = combo_phai.get()
    ngSinh = date_ngsinh.get_date().strftime('%Y-%m-%d')
    dchi = entry_dchi.get()
    chucVu = combo_chucvu.get()

    tree.item(selected[0], values=(maNV, so_cccd, hoTen, sdt, phai, ngSinh, dchi, chucVu, 0, 0))
    lam_moi_form()

def luu():
    for item in tree.get_children():
        maNV, so_cccd, hoTen, sdt, phai, ngSinh, dchi, chucVu, _, _ = tree.item(item,"values")
        cursor.execute("SELECT 1 FROM NHANVIEN WHERE maNV=?", (maNV,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE NHANVIEN SET so_cccd=?, hoTen=?, sdt=?, phai=?, ngSinh=?, dchi=?, chucVu=?
                WHERE maNV=?
            """,(so_cccd, hoTen, sdt, phai, ngSinh, dchi, chucVu, maNV))
        else:
            cursor.execute("""
                INSERT INTO NHANVIEN(maNV,so_cccd,hoTen,sdt,phai,ngSinh,dchi,chucVu)
                VALUES(?,?,?,?,?,?,?,?)
            """,(maNV, so_cccd, hoTen, sdt, phai, ngSinh, dchi, chucVu))
    for maNV in deleted_items:
        cursor.execute("DELETE FROM NHANVIEN WHERE maNV=?", (maNV,))
    deleted_items.clear()
    conn.commit()
    load_data()
    lam_moi_form()
    messagebox.showinfo("Thành công","Đã lưu vào CSDL!")

def huy():
    lam_moi_form()

def thoat():
    root.destroy()

tk.Label(root, text="Quản Lý Nhân Viên", font=("Arial",20,"bold"), bg="#FFFACD").place(x=330,y=20)
form_frame = tk.Frame(root,bg="#FFFACD")
form_frame.place(x=80,y=60)

tk.Label(form_frame,text="Mã NV:", bg="#FFFACD").grid(row=0,column=0,padx=5,pady=5,sticky="w")
entry_maNV = tk.Entry(form_frame,width=25)
entry_maNV.grid(row=0,column=1,padx=5,pady=5)

tk.Label(form_frame,text="Số CCCD:", bg="#FFFACD").grid(row=0,column=2,padx=5,pady=5,sticky="w")
entry_socccd = tk.Entry(form_frame,width=25)
entry_socccd.grid(row=0,column=3,padx=5,pady=5)

tk.Label(form_frame,text="Họ tên:", bg="#FFFACD").grid(row=0,column=4,padx=5,pady=5,sticky="w")
entry_hoTen = tk.Entry(form_frame,width=25)
entry_hoTen.grid(row=0,column=5,padx=5,pady=5)

tk.Label(form_frame,text="SĐT:", bg="#FFFACD").grid(row=1,column=0,padx=5,pady=5,sticky="w")
entry_sdt = tk.Entry(form_frame,width=25)
entry_sdt.grid(row=1,column=1,padx=5,pady=5)

tk.Label(form_frame,text="Giới tính:", bg="#FFFACD").grid(row=1,column=2,padx=5,pady=5,sticky="w")
combo_phai = ttk.Combobox(form_frame,width=22,state="readonly",values=["Nam","Nữ"])
combo_phai.set("Chọn giới tính")
combo_phai.grid(row=1,column=3,padx=5,pady=5)

tk.Label(form_frame,text="Ngày sinh:", bg="#FFFACD").grid(row=2,column=0,padx=5,pady=5,sticky="w")
date_ngsinh = DateEntry(form_frame,width=23,date_pattern="dd/mm/yyyy")
date_ngsinh.grid(row=2,column=1,padx=5,pady=5)

tk.Label(form_frame,text="Địa chỉ:", bg="#FFFACD").grid(row=2,column=2,padx=5,pady=5,sticky="w")
entry_dchi = tk.Entry(form_frame,width=25)
entry_dchi.grid(row=2,column=3,padx=5,pady=5)

tk.Label(form_frame,text="Chức vụ:", bg="#FFFACD").grid(row=3,column=0,padx=5,pady=5,sticky="w")
combo_chucvu = ttk.Combobox(form_frame,width=22,state="readonly",values=["Cơ Trưởng","Hướng Dẫn Viên","Nhân Viên"])
combo_chucvu.set("Chọn chức vụ")
combo_chucvu.grid(row=3,column=1,padx=5,pady=5)

tk.Label(form_frame,text="Tháng:", bg="#FFFACD").grid(row=3,column=2,padx=5,pady=5,sticky="w")
combo_thang = ttk.Combobox(form_frame,width=5,state="readonly",values=[str(i) for i in range(1,13)])
combo_thang.set(str(date.today().month))
combo_thang.grid(row=3,column=2,padx=(60,0),sticky="w")

tk.Label(form_frame,text="Năm:", bg="#FFFACD").grid(row=3,column=3,padx=5,pady=5,sticky="w")
combo_nam = ttk.Combobox(form_frame,width=7,state="readonly")
combo_nam.grid(row=3,column=3,padx=(45,0),sticky="w")

btn_xemluong = tk.Button(form_frame,text="👁 Xem lương",bg="#ADD8E6",font=("Arial",10,"bold"),command=xem_luong)
btn_xemluong.grid(row=3,column=4,padx=10,pady=5)

btn_them = tk.Button(root,text="Thêm",bg="#87cefa",font=("Arial",12,"bold"),width=10,command=them)
btn_them.place(x=100,y=235)
btn_sua = tk.Button(root,text="Sửa",bg="#87cefa",font=("Arial",12,"bold"),width=10,command=sua)
btn_sua.place(x=240,y=235)
btn_xoa = tk.Button(root,text="Xóa",bg="#87cefa",font=("Arial",12,"bold"),width=10,command=xoa)
btn_xoa.place(x=380,y=235)
btn_huy = tk.Button(root,text="Hủy",bg="#87cefa",font=("Arial",12,"bold"),width=10,command=huy)
btn_huy.place(x=520,y=235)
btn_luu = tk.Button(root,text="Lưu",bg="#87cefa",font=("Arial",12,"bold"),width=10,command=luu)
btn_luu.place(x=660,y=235)
btn_thoat = tk.Button(root,text="Thoát",bg="#87cefa",font=("Arial",12,"bold"),width=10,command=thoat)
btn_thoat.place(x=800,y=235)

load_nam()

load_data()
lam_moi_form()

root.mainloop()
