CREATE DATABASE QuanLyTuyenDuLich;
GO

USE QuanLyTuyenDuLich;
GO


CREATE TABLE KHACHHANG (
    maKH VARCHAR(6) PRIMARY KEY 
        CHECK (maKH LIKE 'KH[0-9][0-9][0-9][0-9]'),
    hoTen NVARCHAR(50) NOT NULL,
    phai NVARCHAR(3) CHECK (phai IN (N'nam', N'nữ')),
    ngSinh DATE,
    sdt VARCHAR(10) UNIQUE
		constraint chk_sdt_KH check (sdt like '0[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
    dchi NVARCHAR(100)
);

CREATE TABLE NHANVIEN (
    maNV VARCHAR(6) PRIMARY KEY 
        CHECK (maNV LIKE 'NV[0-9][0-9][0-9][0-9]'),
    so_cccd VARCHAR(12) UNIQUE,
    hoTen NVARCHAR(50) NOT NULL,
    chucVu NVARCHAR(20),
    phai NVARCHAR(3) CHECK (phai IN (N'nam', N'nữ')),
    ngSinh DATE,
    sdt VARCHAR(10) UNIQUE
		constraint chk_sdt_NV check (sdt like '0[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
    dchi NVARCHAR(100),
    luong FLOAT
);

CREATE TABLE TUYENDULICH (
    maTuyen VARCHAR(6) PRIMARY KEY 
        CHECK (maTuyen LIKE 'TD[0-9][0-9][0-9][0-9]'),
    ddDi NVARCHAR(100) NOT NULL,
    ddDen NVARCHAR(100) NOT NULL,
    trangThai NVARCHAR(30) DEFAULT N'Hoạt động'
);

CREATE TABLE CHUYENDI (
    maCD VARCHAR(6) PRIMARY KEY 
        CHECK (maCD LIKE 'CD[0-9][0-9][0-9][0-9]'),
    ngKh DATE,
    tgKh TIME,
    maTuyen VARCHAR(6),
    trangThai NVARCHAR(30) DEFAULT N'Hoạt động',
    FOREIGN KEY (maTuyen) REFERENCES TUYENDULICH(maTuyen)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE CHUYENDI_NHANVIEN (
    maCD VARCHAR(6),
    maNV VARCHAR(6),
    PRIMARY KEY (maCD, maNV),
    FOREIGN KEY (maCD) REFERENCES CHUYENDI(maCD)
        ON DELETE CASCADE,
    FOREIGN KEY (maNV) REFERENCES NHANVIEN(maNV)
        ON DELETE CASCADE
);

CREATE TABLE DATVE (
    maVe VARCHAR(10) PRIMARY KEY
		constraint chk_maVe check (maVe like 'MV[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
    maKH VARCHAR(6),
    maCD VARCHAR(6),
    ngDat DATE,
    trangThai NVARCHAR(50),
    thanhTien FLOAT,
    giaVe FLOAT,
    soLuong INT,
    FOREIGN KEY (maKH) REFERENCES KHACHHANG(maKH)
		ON DELETE CASCADE,
    FOREIGN KEY (maCD) REFERENCES CHUYENDI(maCD)
		ON DELETE CASCADE
);

CREATE TABLE DOANHTHU (
    maCD VARCHAR(6) PRIMARY KEY,
    giaVe FLOAT,
    tongTien FLOAT,
    soLuong INT,
    FOREIGN KEY (maCD) REFERENCES CHUYENDI(maCD)
		ON DELETE CASCADE
);

CREATE TABLE TaiKhoan (
    TenDangNhap NVARCHAR(50) PRIMARY KEY,
    MatKhau NVARCHAR(50) NOT NULL,
    VaiTro NVARCHAR(20) NOT NULL
);

INSERT INTO TaiKhoan VALUES
(N'quanly', N'toilaquanly', N'QuanLy'),
(N'nhanvien', N'emchaosep', N'NhanVien');


select * from TUYENDULICH;
select * from CHUYENDI;
select * from CHUYENDI_NHANVIEN;
select * from DATVE;
select * from KHACHHANG;
select * from DOANHTHU;
select * from NHANVIEN; 







