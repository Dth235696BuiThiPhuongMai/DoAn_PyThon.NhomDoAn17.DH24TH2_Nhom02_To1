import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    #'SERVER=ADMIN-PC;'  
    'SERVER=localhost\\SQLEXPRESS01;'
    'DATABASE=QuanLyTuyenDuLich;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

list_di = ["Hà Nội", "Đà Nẵng", "Hồ Chí Minh"]
mien_bac = ["Tràng An-Tam Cốc-Bái Đính-Hoa Lư", "Mộc Châu-Điện Biên-Sapa",
            "Hà Giang-Cao Bằng", "Ninh Bình-Hạ Long-Sapa", "Vịnh Hạ Long-Hạ Long Park-Bãi Cháy-Yên Tử"]
mien_trung = ["Quy Nhơn-Phú Yên", "Pleiku-Kontum- Măng Đen",
              "Hội An-Bà Nà Hills-Núi Thần Tài", "Phan Thiết-Mũi Né", "Quảng Bình-Suối Moọc- Động Thiên Đường"]
mien_nam = ["Tiền Giang-Bến Tre- An Giang-Cần Thơ", "Vũng Tàu", "Phú Quốc", "Tây Ninh"]

root = tk.Tk()
root.title("Quản Lý Tuyến Du Lịch")
root.geometry("1000x600")
root.configure(bg="#FFFACD")

frame = tk.LabelFrame(root, text="Danh sách tuyến du lịch", font=("Arial", 12, "bold"), bg="#FFFACD", width=850, height=280)
frame.place(x=70, y=270)

columns = ("maTuyen", "ddDi", "ddDen","tt")

tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)

tree.heading("maTuyen", text="Mã Tuyến")
tree.heading("ddDi", text="Địa Điểm Đi")
tree.heading("ddDen", text="Địa Điểm Đến")
tree.heading("tt", text="Trạng Thái")

tree.column("maTuyen", width=150, anchor="center")
tree.column("ddDi", width=150, anchor="center")
tree.column("ddDen", width=300, anchor="center")
tree.column("tt", width=100, anchor ="center")

scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
scrollbar.pack(side="right", fill="y")

def auto_maTuyen():
    ma_list_tree = [tree.item(item)['values'][0].strip() for item in tree.get_children()]

    cursor.execute("SELECT maTuyen FROM TUYENDULICH")
    ma_list_sql = [row[0].strip() for row in cursor.fetchall()]

    # Gộp danh sách
    ma_list = list(set(ma_list_tree + ma_list_sql))

    if not ma_list:
        return "TD0001"
    
    so_list = sorted([int(ma[2:]) for ma in ma_list if ma[2:].isdigit()])
    next_num = so_list[-1] + 1 
    return f"TD{next_num:04d}"


tk.Label(root, text="Quản Lý Tuyến Du Lịch", font=("Arial", 20, "bold"), bg="#FFFACD").place(x=330, y=40)

tk.Label(root, text="Mã Tuyến:", font=("Arial", 12), bg="#FFFACD").place(x=200, y=130)
entry_matuyen = tk.Entry(root, width=50)
entry_matuyen.place(x=350, y=130)
entry_matuyen.config(state="readonly")

tk.Label(root, text="Địa Điểm Đi:", font=("Arial", 12), bg="#FFFACD").place(x=200, y=170)
entry_ddDi = ttk.Combobox(root, width=48, values=list_di, state="normal")
entry_ddDi.place(x=350, y=170)
entry_ddDi.set("")

tk.Label(root, text="Địa Điểm Đến:", font=("Arial", 12), bg="#FFFACD").place(x=200, y=210)
entry_ddDen = ttk.Combobox(root, width=48, values=[], state="normal")
entry_ddDen.place(x=350, y=210)
entry_ddDen.set("")

def cap_nhat_ddDen(event=None):
    di = entry_ddDi.get()
    if di == "Hà Nội":
        den_list = mien_bac.copy()
    elif di == "Đà Nẵng":
        den_list = mien_trung.copy()
    elif di == "Hồ Chí Minh":
        den_list = mien_nam.copy()
    else:
        den_list = []

    cursor.execute("SELECT ddDen FROM TUYENDULICH WHERE ddDi=? AND trangThai=N'Hoạt động'", (di,))

    csdl_den = [row[0] for row in cursor.fetchall()]
    tree_den = [tree.item(item, "values")[2] for item in tree.get_children() if tree.item(item, "values")[1] == di]

    den_list = [d for d in den_list if d not in csdl_den and d not in tree_den]

    entry_ddDen['values'] = den_list
    entry_ddDen.set("")

entry_ddDi.bind("<<ComboboxSelected>>", cap_nhat_ddDen)

def load_data():
    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("SELECT maTuyen, ddDi, ddDen, trangThai FROM TUYENDULICH where trangThai=N'Hoạt động'")
    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", "end", values=(row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip()))

def lam_moi_form():
    entry_ddDi.set("")
    entry_ddDen.set("")
    entry_matuyen.config(state='normal')
    entry_matuyen.delete(0, tk.END)
    entry_matuyen.insert(0, auto_maTuyen())
    entry_matuyen.config(state='readonly')

def them():
    ma = auto_maTuyen()
    di = entry_ddDi.get()
    den = entry_ddDen.get()
    if not di or not den:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn địa điểm đi và đến")
        return
    tree.insert("", "end", values=(ma, di, den, "Hoạt động"))
    lam_moi_form()

def xoa():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Vui lòng chọn tuyến để xóa!")
        return
    
    confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tuyến này không?")
    if confirm:
        for item in selected:
            ma = tree.item(item, "values")[0]

            tree.delete(item)

            cursor.execute("UPDATE TUYENDULICH SET trangThai=N'Đã xóa' WHERE maTuyen=?", (ma,))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã xóa tuyến du lịch!")
        lam_moi_form()
        load_data()

def sua(): 
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Vui lòng chọn tuyến để sửa!")
        return

    maTuyen = tree.item(selected[0])['values'][0].strip()
    ddDi = entry_ddDi.get().strip()
    ddDen = entry_ddDen.get().strip()

    if not ddDi or not ddDen:
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng chọn đầy đủ địa điểm đi và đến!")
        return

    tree.item(selected[0], values=(maTuyen, ddDi, ddDen, "Hoạt động"))

    cursor.execute(
        "UPDATE TUYENDULICH SET ddDi=?, ddDen=?, trangThai=N'Hoạt động' WHERE maTuyen=?",
        (ddDi, ddDen, maTuyen)
    )
    conn.commit()

    messagebox.showinfo("Thành công", "Đã cập nhật thông tin tuyến du lịch!")
    lam_moi_form()

def luu():
    try:
        for item in tree.get_children():
            maTuyen, ddDi, ddDen, tt = tree.item(item, "values")
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM TUYENDULICH WHERE maTuyen=?)
                    INSERT INTO TUYENDULICH (maTuyen, ddDi, ddDen, trangThai)
                    VALUES (?, ?, ?, N'Hoạt động')
                ELSE
                    UPDATE TUYENDULICH
                    SET ddDi=?, ddDen=?, trangThai=N'Hoạt động'
                    WHERE maTuyen=?
            """, (maTuyen, maTuyen, ddDi, ddDen, ddDi, ddDen, maTuyen))
        
        conn.commit()
        messagebox.showinfo("Thành công", "Đã lưu và đồng bộ dữ liệu với CSDL!")
        load_data()
        lam_moi_form()
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lưu dữ liệu thất bại!\n{e}")

def huy():
    lam_moi_form()

def thoat():
    root.destroy()

button_style = {"font": ("Times New Roman", 13, "bold"), "bg": "#B0E0E6", "width": 8, "height": 1}

btn_them = tk.Button(root, text="Thêm", **button_style, command=them)
btn_them.place(x=870, y=120)

btn_xoa = tk.Button(root, text="Xóa", **button_style, command=xoa)
btn_xoa.place(x=870, y=200)

btn_sua = tk.Button(root, text="Sửa", **button_style, command=sua)
btn_sua.place(x=870, y=280)

btn_huy = tk.Button(root, text="Hủy", **button_style, command=huy)
btn_huy.place(x=870, y=360)

btn_luu = tk.Button(root, text="Lưu", **button_style, command=luu)
btn_luu.place(x=870, y=440)

btn_thoat = tk.Button(root, text="Thoát", **button_style, command=thoat)
btn_thoat.place(x = 870, y=520)

lam_moi_form()
load_data()

root.mainloop()