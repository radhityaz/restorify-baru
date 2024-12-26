import streamlit as st
import psycopg2
from psycopg2 import sql, extras
import pandas as pd

# -------------------- KONEKSI DATABASE --------------------
def get_connection():
    try:
        conn = psycopg2.connect(
            dbname=st.secrets["database"]["dbname"],
            user=st.secrets["database"]["user"],
            password=st.secrets["database"]["password"],
            host=st.secrets["database"]["host"],
            port=st.secrets["database"]["port"]
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None


# -------------------- MEMBUAT TABEL --------------------
def create_tables():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        # Membuat tabel karyawan
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS karyawan (
                karyawan_id TEXT PRIMARY KEY,
                employee_name TEXT NOT NULL,
                position TEXT NOT NULL,
                fingerprint_id TEXT
            )
        ''')
        
        # Membuat tabel pelanggan
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pelanggan (
                pelanggan_id TEXT PRIMARY KEY,
                cus_name TEXT NOT NULL,
                contact_info TEXT NOT NULL
            )
        ''')
        
        # Membuat tabel supplier
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplier (
                supplier_id TEXT PRIMARY KEY,
                supplier_name TEXT NOT NULL,
                address TEXT NOT NULL
            )
        ''')
        
        # Membuat tabel bahan_baku
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bahan_baku (
                bahan_id TEXT PRIMARY KEY,
                nama_bahan TEXT NOT NULL,
                stock INTEGER NOT NULL,
                satuan TEXT NOT NULL,
                harga_bahan NUMERIC NOT NULL,
                supplier_id TEXT,
                FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id)
            )
        ''')
        
        # Membuat tabel menu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu (
                menu_id TEXT PRIMARY KEY,
                nama_menu TEXT NOT NULL,
                harga NUMERIC NOT NULL
            )
        ''')
        
        # Membuat tabel transaksi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaksi (
                transaksi_id TEXT PRIMARY KEY,
                tanggal_pembelian DATE NOT NULL,
                pelanggan_id TEXT,
                karyawan_id TEXT,
                total_transaksi NUMERIC NOT NULL,
                FOREIGN KEY (pelanggan_id) REFERENCES pelanggan(pelanggan_id),
                FOREIGN KEY (karyawan_id) REFERENCES karyawan(karyawan_id)
            )
        ''')
        
        # Membuat tabel feedback
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id TEXT PRIMARY KEY,
                pelanggan_id TEXT,
                karyawan_id TEXT,
                tanggal DATE NOT NULL,
                rating INTEGER NOT NULL,
                komentar TEXT,
                FOREIGN KEY (pelanggan_id) REFERENCES pelanggan(pelanggan_id),
                FOREIGN KEY (karyawan_id) REFERENCES karyawan(karyawan_id)
            )
        ''')
        
        # Membuat tabel absensi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS absensi (
                absensi_id TEXT PRIMARY KEY,
                karyawan_id TEXT,
                tanggal DATE NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (karyawan_id) REFERENCES karyawan(karyawan_id)
            )
        ''')
        
        conn.commit()
        st.success("Tabel berhasil dibuat atau sudah ada.")
        
        # Memasukkan data awal jika tabel kosong
        insert_initial_data(conn, cursor)
        
    except Exception as e:
        st.error(f"Error creating tables: {e}")
    finally:
        cursor.close()
        conn.close()

# -------------------- MEMASUKKAN DATA AWAL --------------------
def insert_initial_data(conn, cursor):
    try:
        # Cek apakah tabel karyawan kosong
        cursor.execute('SELECT COUNT(*) FROM karyawan')
        count = cursor.fetchone()[0]
        if count == 0:
            karyawan_data = [
                ('K001', 'Ahmad Fauzi', 'Manager', 'FP001'),
                ('K002', 'Siti Aminah', 'Waiter', 'FP002'),
                ('K003', 'Budi Santoso', 'Chef', 'FP003'),
                ('K004', 'Rina Marlina', 'Cashier', 'FP004'),
                ('K005', 'Dewi Lestari', 'Operational', 'FP005')
            ]
            cursor.executemany('''
                INSERT INTO karyawan (karyawan_id, employee_name, position, fingerprint_id)
                VALUES (%s, %s, %s, %s)
            ''', karyawan_data)
            st.info("Data karyawan awal berhasil ditambahkan.")

        # Cek apakah tabel pelanggan kosong
        cursor.execute('SELECT COUNT(*) FROM pelanggan')
        count = cursor.fetchone()[0]
        if count == 0:
            pelanggan_data = [
                ('P001', 'Mansur', 'mansur123@contohemail.com'),
                ('P002', 'Sir Joko', 'joko456@contohemail.com'),
                ('P003', 'Pak Amba', 'amba789@contohemail.com'),
                ('P004', 'Ibu Tukam', 'tukam101112@contohemail.com'),
                ('P005', 'Maemunah', 'maemunah131415@contohemail.com')
            ]
            cursor.executemany('''
                INSERT INTO pelanggan (pelanggan_id, cus_name, contact_info)
                VALUES (%s, %s, %s)
            ''', pelanggan_data)
            st.info("Data pelanggan awal berhasil ditambahkan.")

        # Cek apakah tabel supplier kosong
        cursor.execute('SELECT COUNT(*) FROM supplier')
        count = cursor.fetchone()[0]
        if count == 0:
            supplier_data = [
                ('S001', 'Supplier A', 'Jl. Raya No.1'),
                ('S002', 'Supplier B', 'Jl. Merdeka No.2'),
                ('S003', 'Supplier C', 'Jl. Sudirman No.3'),
                ('S004', 'Supplier D', 'Jl. Thamrin No.4'),
                ('S005', 'Supplier E', 'Jl. Diponegoro No.5')
            ]
            cursor.executemany('''
                INSERT INTO supplier (supplier_id, supplier_name, address)
                VALUES (%s, %s, %s)
            ''', supplier_data)
            st.info("Data supplier awal berhasil ditambahkan.")

        # Cek apakah tabel bahan_baku kosong
        cursor.execute('SELECT COUNT(*) FROM bahan_baku')
        count = cursor.fetchone()[0]
        if count == 0:
            bahan_baku_data = [
                ('B001', 'Beras', 100, 'kg', 50000, 'S001'),
                ('B002', 'Gula', 200, 'kg', 30000, 'S002'),
                ('B003', 'Minyak Goreng', 150, 'liter', 40000, 'S003'),
                ('B004', 'Telur', 500, 'butir', 5000, 'S004'),
                ('B005', 'Daging Sapi', 80, 'kg', 100000, 'S005')
            ]
            cursor.executemany('''
                INSERT INTO bahan_baku (bahan_id, nama_bahan, stock, satuan, harga_bahan, supplier_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', bahan_baku_data)
            st.info("Data bahan baku awal berhasil ditambahkan.")

        # Cek apakah tabel menu kosong
        cursor.execute('SELECT COUNT(*) FROM menu')
        count = cursor.fetchone()[0]
        if count == 0:
            menu_data = [
                ('M001', 'Nasi Goreng', 25000),
                ('M002', 'Mie Ayam', 20000),
                ('M003', 'Sate Ayam', 30000),
                ('M004', 'Ayam Bakar', 35000),
                ('M005', 'Es Teh Manis', 8000)
            ]
            cursor.executemany('''
                INSERT INTO menu (menu_id, nama_menu, harga)
                VALUES (%s, %s, %s)
            ''', menu_data)
            st.info("Data menu awal berhasil ditambahkan.")

        # Cek apakah tabel transaksi kosong
        cursor.execute('SELECT COUNT(*) FROM transaksi')
        count = cursor.fetchone()[0]
        if count == 0:
            transaksi_data = [
                ('T001', '2024-04-01', 'P001', 'K001', 50000),
                ('T002', '2024-04-02', 'P002', 'K002', 40000),
                ('T003', '2024-04-03', 'P003', 'K003', 60000),
                ('T004', '2024-04-04', 'P004', 'K004', 35000),
                ('T005', '2024-04-05', 'P005', 'K005', 45000)
            ]
            cursor.executemany('''
                INSERT INTO transaksi (transaksi_id, tanggal_pembelian, pelanggan_id, karyawan_id, total_transaksi)
                VALUES (%s, %s, %s, %s, %s)
            ''', transaksi_data)
            st.info("Data transaksi awal berhasil ditambahkan.")

        # Cek apakah tabel feedback kosong
        cursor.execute('SELECT COUNT(*) FROM feedback')
        count = cursor.fetchone()[0]
        if count == 0:
            feedback_data = [
                ('F001', 'P001', 'K001', '2024-04-01', 5, 'Pelayanan sangat baik!'),
                ('F002', 'P002', 'K002', '2024-04-02', 4, 'Makanan enak, cepat saji.'),
                ('F003', 'P003', 'K003', '2024-04-03', 5, 'Chef hebat!'),
                ('F004', 'P004', 'K004', '2024-04-04', 3, 'Kasir ramah.'),
                ('F005', 'P005', 'K005', '2024-04-05', 4, 'Operasional lancar.')
            ]
            cursor.executemany('''
                INSERT INTO feedback (feedback_id, pelanggan_id, karyawan_id, tanggal, rating, komentar)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', feedback_data)
            st.info("Data feedback awal berhasil ditambahkan.")

        # Cek apakah tabel absensi kosong
        cursor.execute('SELECT COUNT(*) FROM absensi')
        count = cursor.fetchone()[0]
        if count == 0:
            absensi_data = [
                ('A001', 'K001', '2024-04-01', 'Hadir'),
                ('A002', 'K002', '2024-04-01', 'Hadir'),
                ('A003', 'K003', '2024-04-01', 'Hadir'),
                ('A004', 'K004', '2024-04-01', 'Hadir'),
                ('A005', 'K005', '2024-04-01', 'Hadir')
            ]
            cursor.executemany('''
                INSERT INTO absensi (absensi_id, karyawan_id, tanggal, status)
                VALUES (%s, %s, %s, %s)
            ''', absensi_data)
            st.info("Data absensi awal berhasil ditambahkan.")
        
        conn.commit()
    except Exception as e:
        st.error(f"Error inserting initial data: {e}")

# -------------------- CRUD FUNCTIONS --------------------
# -------------------- KARYAWAN --------------------
# Tambah Karyawan
def tambah_karyawan(karyawan_id, employee_name, position, fingerprint_id=None):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO karyawan (karyawan_id, employee_name, position, fingerprint_id)
            VALUES (%s, %s, %s, %s)
        ''', (karyawan_id, employee_name, position, fingerprint_id))
        conn.commit()
        st.success("Data karyawan berhasil ditambahkan.")
    except psycopg2.IntegrityError:
        conn.rollback()
        st.error("Error: ID Karyawan sudah ada.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error adding karyawan: {e}")
    finally:
        cursor.close()
        conn.close()

# Lihat Karyawan
def lihat_karyawan():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor(cursor_factory=extras.DictCursor)
    try:
        cursor.execute('SELECT * FROM karyawan')
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows, columns=['ID Karyawan', 'Nama', 'Posisi', 'Fingerprint ID'])
            st.dataframe(df)
            
            # Opsi download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='daftar_karyawan.csv',
                mime='text/csv',
            )
        else:
            st.info("Belum ada data karyawan.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    finally:
        cursor.close()
        conn.close()

# Perbarui Karyawan
def perbarui_karyawan(karyawan_id, employee_name=None, position=None, fingerprint_id=None):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    fields = []
    params = []
    if employee_name:
        fields.append("employee_name = %s")
        params.append(employee_name)
    if position:
        fields.append("position = %s")
        params.append(position)
    if fingerprint_id is not None:
        fields.append("fingerprint_id = %s")
        params.append(fingerprint_id)
    
    if not fields:
        st.warning("Tidak ada field yang diperbarui.")
        return
    
    params.append(karyawan_id)
    sql_query = f"UPDATE karyawan SET {', '.join(fields)} WHERE karyawan_id = %s"
    
    try:
        cursor.execute(sql_query, params)
        if cursor.rowcount == 0:
            st.warning("Karyawan tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data karyawan berhasil diperbarui.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error updating karyawan: {e}")
    finally:
        cursor.close()
        conn.close()

# Hapus Karyawan
def hapus_karyawan(karyawan_id):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM karyawan WHERE karyawan_id = %s', (karyawan_id,))
        if cursor.rowcount == 0:
            st.warning("Karyawan tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data karyawan berhasil dihapus.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error deleting karyawan: {e}")
    finally:
        cursor.close()
        conn.close()

# -------------------- PELANGGAN --------------------
# Tambah Pelanggan
def tambah_pelanggan(pelanggan_id, cus_name, contact_info):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO pelanggan (pelanggan_id, cus_name, contact_info)
            VALUES (%s, %s, %s)
        ''', (pelanggan_id, cus_name, contact_info))
        conn.commit()
        st.success("Data pelanggan berhasil ditambahkan.")
    except psycopg2.IntegrityError:
        conn.rollback()
        st.error("Error: ID Pelanggan sudah ada.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error adding pelanggan: {e}")
    finally:
        cursor.close()
        conn.close()

# Lihat Pelanggan
def lihat_pelanggan():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor(cursor_factory=extras.DictCursor)
    try:
        cursor.execute('SELECT * FROM pelanggan')
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows, columns=['ID Pelanggan', 'Nama Pelanggan', 'Kontak Informasi'])
            st.dataframe(df)
            
            # Opsi download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='daftar_pelanggan.csv',
                mime='text/csv',
            )
        else:
            st.info("Belum ada data pelanggan.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    finally:
        cursor.close()
        conn.close()

# Perbarui Pelanggan
def perbarui_pelanggan(pelanggan_id, cus_name=None, contact_info=None):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    fields = []
    params = []
    if cus_name:
        fields.append("cus_name = %s")
        params.append(cus_name)
    if contact_info:
        fields.append("contact_info = %s")
        params.append(contact_info)
    
    if not fields:
        st.warning("Tidak ada field yang diperbarui.")
        return
    
    params.append(pelanggan_id)
    sql_query = f"UPDATE pelanggan SET {', '.join(fields)} WHERE pelanggan_id = %s"
    
    try:
        cursor.execute(sql_query, params)
        if cursor.rowcount == 0:
            st.warning("Pelanggan tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data pelanggan berhasil diperbarui.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error updating pelanggan: {e}")
    finally:
        cursor.close()
        conn.close()

# Hapus Pelanggan
def hapus_pelanggan(pelanggan_id):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM pelanggan WHERE pelanggan_id = %s', (pelanggan_id,))
        if cursor.rowcount == 0:
            st.warning("Pelanggan tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data pelanggan berhasil dihapus.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error deleting pelanggan: {e}")
    finally:
        cursor.close()
        conn.close()

# -------------------- SUPPLIER --------------------
# Tambah Supplier
def tambah_supplier(supplier_id, supplier_name, address):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO supplier (supplier_id, supplier_name, address)
            VALUES (%s, %s, %s)
        ''', (supplier_id, supplier_name, address))
        conn.commit()
        st.success("Data supplier berhasil ditambahkan.")
    except psycopg2.IntegrityError:
        conn.rollback()
        st.error("Error: ID Supplier sudah ada.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error adding supplier: {e}")
    finally:
        cursor.close()
        conn.close()

# Lihat Supplier
def lihat_supplier():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor(cursor_factory=extras.DictCursor)
    try:
        cursor.execute('SELECT * FROM supplier')
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows, columns=['ID Supplier', 'Nama Supplier', 'Alamat'])
            st.dataframe(df)
            
            # Opsi download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='daftar_supplier.csv',
                mime='text/csv',
            )
        else:
            st.info("Belum ada data supplier.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    finally:
        cursor.close()
        conn.close()

# Perbarui Supplier
def perbarui_supplier(supplier_id, supplier_name=None, address=None):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    fields = []
    params = []
    if supplier_name:
        fields.append("supplier_name = %s")
        params.append(supplier_name)
    if address:
        fields.append("address = %s")
        params.append(address)
    
    if not fields:
        st.warning("Tidak ada field yang diperbarui.")
        return
    
    params.append(supplier_id)
    sql_query = f"UPDATE supplier SET {', '.join(fields)} WHERE supplier_id = %s"
    
    try:
        cursor.execute(sql_query, params)
        if cursor.rowcount == 0:
            st.warning("Supplier tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data supplier berhasil diperbarui.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error updating supplier: {e}")
    finally:
        cursor.close()
        conn.close()

# Hapus Supplier
def hapus_supplier(supplier_id):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM supplier WHERE supplier_id = %s', (supplier_id,))
        if cursor.rowcount == 0:
            st.warning("Supplier tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data supplier berhasil dihapus.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error deleting supplier: {e}")
    finally:
        cursor.close()
        conn.close()

# -------------------- BAHAN BAKU --------------------
# Tambah Bahan Baku
def tambah_bahan_baku(bahan_id, nama_bahan, stock, satuan, harga_bahan, supplier_id):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO bahan_baku (bahan_id, nama_bahan, stock, satuan, harga_bahan, supplier_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (bahan_id, nama_bahan, stock, satuan, harga_bahan, supplier_id))
        conn.commit()
        st.success("Data bahan baku berhasil ditambahkan.")
    except psycopg2.IntegrityError:
        conn.rollback()
        st.error("Error: ID Bahan Baku sudah ada.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error adding bahan baku: {e}")
    finally:
        cursor.close()
        conn.close()

# Lihat Bahan Baku
def lihat_bahan_baku():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor(cursor_factory=extras.DictCursor)
    try:
        cursor.execute('SELECT * FROM bahan_baku')
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows, columns=['ID Bahan Baku', 'Nama Bahan', 'Stock', 'Satuan', 'Harga Bahan', 'ID Supplier'])
            st.dataframe(df)
            
            # Opsi download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='daftar_bahan_baku.csv',
                mime='text/csv',
            )
        else:
            st.info("Belum ada data bahan baku.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    finally:
        cursor.close()
        conn.close()

# Perbarui Bahan Baku
def perbarui_bahan_baku(bahan_id, nama_bahan=None, stock=None, satuan=None, harga_bahan=None, supplier_id=None):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    fields = []
    params = []
    if nama_bahan:
        fields.append("nama_bahan = %s")
        params.append(nama_bahan)
    if stock is not None:
        fields.append("stock = %s")
        params.append(stock)
    if satuan:
        fields.append("satuan = %s")
        params.append(satuan)
    if harga_bahan is not None:
        fields.append("harga_bahan = %s")
        params.append(harga_bahan)
    if supplier_id:
        fields.append("supplier_id = %s")
        params.append(supplier_id)
    
    if not fields:
        st.warning("Tidak ada field yang diperbarui.")
        return
    
    params.append(bahan_id)
    sql_query = f"UPDATE bahan_baku SET {', '.join(fields)} WHERE bahan_id = %s"
    
    try:
        cursor.execute(sql_query, params)
        if cursor.rowcount == 0:
            st.warning("Bahan Baku tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data bahan baku berhasil diperbarui.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error updating bahan baku: {e}")
    finally:
        cursor.close()
        conn.close()

# Hapus Bahan Baku
def hapus_bahan_baku(bahan_id):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM bahan_baku WHERE bahan_id = %s', (bahan_id,))
        if cursor.rowcount == 0:
            st.warning("Bahan Baku tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data bahan baku berhasil dihapus.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error deleting bahan baku: {e}")
    finally:
        cursor.close()
        conn.close()

# -------------------- MENU --------------------
# Tambah Menu
def tambah_menu(menu_id, nama_menu, harga):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO menu (menu_id, nama_menu, harga)
            VALUES (%s, %s, %s)
        ''', (menu_id, nama_menu, harga))
        conn.commit()
        st.success("Data menu berhasil ditambahkan.")
    except psycopg2.IntegrityError:
        conn.rollback()
        st.error("Error: ID Menu sudah ada.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error adding menu: {e}")
    finally:
        cursor.close()
        conn.close()

# Lihat Menu
def lihat_menu():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor(cursor_factory=extras.DictCursor)
    try:
        cursor.execute('SELECT * FROM menu')
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows, columns=['ID Menu', 'Nama Menu', 'Harga'])
            st.dataframe(df)
            
            # Opsi download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='daftar_menu.csv',
                mime='text/csv',
            )
        else:
            st.info("Belum ada data menu.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    finally:
        cursor.close()
        conn.close()

# Perbarui Menu
def perbarui_menu(menu_id, nama_menu=None, harga=None):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    fields = []
    params = []
    if nama_menu:
        fields.append("nama_menu = %s")
        params.append(nama_menu)
    if harga is not None:
        fields.append("harga = %s")
        params.append(harga)
    
    if not fields:
        st.warning("Tidak ada field yang diperbarui.")
        return
    
    params.append(menu_id)
    sql_query = f"UPDATE menu SET {', '.join(fields)} WHERE menu_id = %s"
    
    try:
        cursor.execute(sql_query, params)
        if cursor.rowcount == 0:
            st.warning("Menu tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data menu berhasil diperbarui.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error updating menu: {e}")
    finally:
        cursor.close()
        conn.close()

# Hapus Menu
def hapus_menu(menu_id):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM menu WHERE menu_id = %s', (menu_id,))
        if cursor.rowcount == 0:
            st.warning("Menu tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data menu berhasil dihapus.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error deleting menu: {e}")
    finally:
        cursor.close()
        conn.close()

# -------------------- TRANSAKSI --------------------
# Tambah Transaksi
def tambah_transaksi(transaksi_id, tanggal_pembelian, pelanggan_id, karyawan_id, total_transaksi):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO transaksi (transaksi_id, tanggal_pembelian, pelanggan_id, karyawan_id, total_transaksi)
            VALUES (%s, %s, %s, %s, %s)
        ''', (transaksi_id, tanggal_pembelian, pelanggan_id, karyawan_id, total_transaksi))
        conn.commit()
        st.success("Data transaksi berhasil ditambahkan.")
    except psycopg2.IntegrityError:
        conn.rollback()
        st.error("Error: ID Transaksi sudah ada.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error adding transaksi: {e}")
    finally:
        cursor.close()
        conn.close()

# Lihat Transaksi
def lihat_transaksi():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor(cursor_factory=extras.DictCursor)
    try:
        cursor.execute('SELECT * FROM transaksi')
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows, columns=['ID Transaksi', 'Tanggal Pembelian', 'ID Pelanggan', 'ID Karyawan', 'Total Transaksi'])
            st.dataframe(df)
            
            # Opsi download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='daftar_transaksi.csv',
                mime='text/csv',
            )
        else:
            st.info("Belum ada data transaksi.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    finally:
        cursor.close()
        conn.close()

# Perbarui Transaksi
def perbarui_transaksi(transaksi_id, tanggal_pembelian=None, pelanggan_id=None, karyawan_id=None, total_transaksi=None):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    fields = []
    params = []
    if tanggal_pembelian:
        fields.append("tanggal_pembelian = %s")
        params.append(tanggal_pembelian)
    if pelanggan_id:
        fields.append("pelanggan_id = %s")
        params.append(pelanggan_id)
    if karyawan_id:
        fields.append("karyawan_id = %s")
        params.append(karyawan_id)
    if total_transaksi is not None:
        fields.append("total_transaksi = %s")
        params.append(total_transaksi)
    
    if not fields:
        st.warning("Tidak ada field yang diperbarui.")
        return
    
    params.append(transaksi_id)
    sql_query = f"UPDATE transaksi SET {', '.join(fields)} WHERE transaksi_id = %s"
    
    try:
        cursor.execute(sql_query, params)
        if cursor.rowcount == 0:
            st.warning("Transaksi tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data transaksi berhasil diperbarui.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error updating transaksi: {e}")
    finally:
        cursor.close()
        conn.close()

# Hapus Transaksi
def hapus_transaksi(transaksi_id):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM transaksi WHERE transaksi_id = %s', (transaksi_id,))
        if cursor.rowcount == 0:
            st.warning("Transaksi tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data transaksi berhasil dihapus.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error deleting transaksi: {e}")
    finally:
        cursor.close()
        conn.close()

# -------------------- FEEDBACK --------------------
# Tambah Feedback
def tambah_feedback(feedback_id, pelanggan_id, karyawan_id, tanggal, rating, komentar):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO feedback (feedback_id, pelanggan_id, karyawan_id, tanggal, rating, komentar)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (feedback_id, pelanggan_id, karyawan_id, tanggal, rating, komentar))
        conn.commit()
        st.success("Data feedback berhasil ditambahkan.")
    except psycopg2.IntegrityError:
        conn.rollback()
        st.error("Error: ID Feedback sudah ada.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error adding feedback: {e}")
    finally:
        cursor.close()
        conn.close()

# Lihat Feedback
def lihat_feedback():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor(cursor_factory=extras.DictCursor)
    try:
        cursor.execute('SELECT * FROM feedback')
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows, columns=['ID Feedback', 'ID Pelanggan', 'ID Karyawan', 'Tanggal', 'Rating', 'Komentar'])
            st.dataframe(df)
            
            # Opsi download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='daftar_feedback.csv',
                mime='text/csv',
            )
        else:
            st.info("Belum ada data feedback.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    finally:
        cursor.close()
        conn.close()

# Perbarui Feedback
def perbarui_feedback(feedback_id, pelanggan_id=None, karyawan_id=None, tanggal=None, rating=None, komentar=None):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    fields = []
    params = []
    if pelanggan_id:
        fields.append("pelanggan_id = %s")
        params.append(pelanggan_id)
    if karyawan_id:
        fields.append("karyawan_id = %s")
        params.append(karyawan_id)
    if tanggal:
        fields.append("tanggal = %s")
        params.append(tanggal)
    if rating is not None:
        fields.append("rating = %s")
        params.append(rating)
    if komentar:
        fields.append("komentar = %s")
        params.append(komentar)
    
    if not fields:
        st.warning("Tidak ada field yang diperbarui.")
        return
    
    params.append(feedback_id)
    sql_query = f"UPDATE feedback SET {', '.join(fields)} WHERE feedback_id = %s"
    
    try:
        cursor.execute(sql_query, params)
        if cursor.rowcount == 0:
            st.warning("Feedback tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data feedback berhasil diperbarui.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error updating feedback: {e}")
    finally:
        cursor.close()
        conn.close()

# Hapus Feedback
def hapus_feedback(feedback_id):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM feedback WHERE feedback_id = %s', (feedback_id,))
        if cursor.rowcount == 0:
            st.warning("Feedback tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data feedback berhasil dihapus.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error deleting feedback: {e}")
    finally:
        cursor.close()
        conn.close()

# -------------------- ABSENSI SIDIK JARI --------------------
# Tambah Absensi
def tambah_absensi(absensi_id, karyawan_id, tanggal, status):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO absensi (absensi_id, karyawan_id, tanggal, status)
            VALUES (%s, %s, %s, %s)
        ''', (absensi_id, karyawan_id, tanggal, status))
        conn.commit()
        st.success("Data absensi berhasil ditambahkan.")
    except psycopg2.IntegrityError:
        conn.rollback()
        st.error("Error: ID Absensi sudah ada.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error adding absensi: {e}")
    finally:
        cursor.close()
        conn.close()

# Lihat Absensi
def lihat_absensi():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor(cursor_factory=extras.DictCursor)
    try:
        cursor.execute('SELECT * FROM absensi')
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows, columns=['ID Absensi', 'ID Karyawan', 'Tanggal', 'Status'])
            st.dataframe(df)
            
            # Opsi download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='daftar_absensi.csv',
                mime='text/csv',
            )
        else:
            st.info("Belum ada data absensi.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    finally:
        cursor.close()
        conn.close()

# Perbarui Absensi
def perbarui_absensi(absensi_id, karyawan_id=None, tanggal=None, status=None):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    fields = []
    params = []
    if karyawan_id:
        fields.append("karyawan_id = %s")
        params.append(karyawan_id)
    if tanggal:
        fields.append("tanggal = %s")
        params.append(tanggal)
    if status:
        fields.append("status = %s")
        params.append(status)
    
    if not fields:
        st.warning("Tidak ada field yang diperbarui.")
        return
    
    params.append(absensi_id)
    sql_query = f"UPDATE absensi SET {', '.join(fields)} WHERE absensi_id = %s"
    
    try:
        cursor.execute(sql_query, params)
        if cursor.rowcount == 0:
            st.warning("Absensi tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data absensi berhasil diperbarui.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error updating absensi: {e}")
    finally:
        cursor.close()
        conn.close()

# Hapus Absensi
def hapus_absensi(absensi_id):
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM absensi WHERE absensi_id = %s', (absensi_id,))
        if cursor.rowcount == 0:
            st.warning("Absensi tidak ditemukan.")
        else:
            conn.commit()
            st.success("Data absensi berhasil dihapus.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error deleting absensi: {e}")
    finally:
        cursor.close()
        conn.close()

# -------------------- CRUD UI --------------------
# -------------------- KARYAWAN --------------------
def manage_karyawan():
    st.header("Kelola Data Karyawan")
    action = st.selectbox("Pilih Aksi", ["Tambah", "Lihat", "Perbarui", "Hapus"])
    
    if action == "Tambah":
        st.subheader("Tambah Data Karyawan")
        with st.form("form_tambah_karyawan"):
            karyawan_id = st.text_input("ID Karyawan")
            employee_name = st.text_input("Nama Karyawan")
            position = st.selectbox("Posisi", ["Waiter", "Cashier", "Chef", "Manager", "Operational"])
            fingerprint_id = st.text_input("ID Sidik Jari (Opsional)")
            submit = st.form_submit_button("Simpan")
            
            if submit:
                if not karyawan_id or not employee_name or not position:
                    st.error("Semua field wajib diisi (kecuali sidik jari opsional).")
                else:
                    tambah_karyawan(karyawan_id, employee_name, position, fingerprint_id)
    
    elif action == "Lihat":
        st.subheader("Daftar Karyawan")
        lihat_karyawan()
    
    elif action == "Perbarui":
        st.subheader("Perbarui Data Karyawan")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT karyawan_id, employee_name FROM karyawan')
        karyawan_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if karyawan_list:
            karyawan_ids = [f"{k[0]} - {k[1]}" for k in karyawan_list]
            selected_karyawan = st.selectbox("Pilih Karyawan", karyawan_ids)
            karyawan_id = selected_karyawan.split(" - ")[0]
            
            with st.form("form_perbarui_karyawan"):
                employee_name = st.text_input("Nama Karyawan")
                position = st.selectbox("Posisi", ["Waiter", "Cashier", "Chef", "Manager", "Operational"])
                fingerprint_id = st.text_input("ID Sidik Jari (Opsional)")
                submit = st.form_submit_button("Perbarui")
                
                if submit:
                    if not employee_name or not position:
                        st.error("Nama dan Posisi wajib diisi.")
                    else:
                        perbarui_karyawan(karyawan_id, employee_name, position, fingerprint_id)
        else:
            st.info("Belum ada data karyawan.")
    
    elif action == "Hapus":
        st.subheader("Hapus Data Karyawan")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT karyawan_id, employee_name FROM karyawan')
        karyawan_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if karyawan_list:
            karyawan_ids = [f"{k[0]} - {k[1]}" for k in karyawan_list]
            selected_karyawan = st.selectbox("Pilih Karyawan", karyawan_ids)
            karyawan_id = selected_karyawan.split(" - ")[0]
            
            if st.button("Hapus"):
                hapus_karyawan(karyawan_id)
        else:
            st.info("Belum ada data karyawan.")

# -------------------- PELANGGAN --------------------
def manage_pelanggan():
    st.header("Kelola Data Pelanggan")
    action = st.selectbox("Pilih Aksi", ["Tambah", "Lihat", "Perbarui", "Hapus"])
    
    if action == "Tambah":
        st.subheader("Tambah Data Pelanggan")
        with st.form("form_tambah_pelanggan"):
            pelanggan_id = st.text_input("ID Pelanggan")
            cus_name = st.text_input("Nama Pelanggan")
            contact_info = st.text_input("Kontak Informasi")
            submit = st.form_submit_button("Simpan")
            
            if submit:
                if not pelanggan_id or not cus_name or not contact_info:
                    st.error("Semua field wajib diisi.")
                else:
                    tambah_pelanggan(pelanggan_id, cus_name, contact_info)
    
    elif action == "Lihat":
        st.subheader("Daftar Pelanggan")
        lihat_pelanggan()
    
    elif action == "Perbarui":
        st.subheader("Perbarui Data Pelanggan")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT pelanggan_id, cus_name FROM pelanggan')
        pelanggan_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if pelanggan_list:
            pelanggan_ids = [f"{p[0]} - {p[1]}" for p in pelanggan_list]
            selected_pelanggan = st.selectbox("Pilih Pelanggan", pelanggan_ids)
            pelanggan_id = selected_pelanggan.split(" - ")[0]
            
            with st.form("form_perbarui_pelanggan"):
                cus_name = st.text_input("Nama Pelanggan")
                contact_info = st.text_input("Kontak Informasi")
                submit = st.form_submit_button("Perbarui")
                
                if submit:
                    if not cus_name or not contact_info:
                        st.error("Nama dan Kontak Informasi wajib diisi.")
                    else:
                        perbarui_pelanggan(pelanggan_id, cus_name, contact_info)
        else:
            st.info("Belum ada data pelanggan.")
    
    elif action == "Hapus":
        st.subheader("Hapus Data Pelanggan")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT pelanggan_id, cus_name FROM pelanggan')
        pelanggan_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if pelanggan_list:
            pelanggan_ids = [f"{p[0]} - {p[1]}" for p in pelanggan_list]
            selected_pelanggan = st.selectbox("Pilih Pelanggan", pelanggan_ids)
            pelanggan_id = selected_pelanggan.split(" - ")[0]
            
            if st.button("Hapus"):
                hapus_pelanggan(pelanggan_id)
        else:
            st.info("Belum ada data pelanggan.")

# -------------------- SUPPLIER --------------------
def manage_supplier():
    st.header("Kelola Data Supplier")
    action = st.selectbox("Pilih Aksi", ["Tambah", "Lihat", "Perbarui", "Hapus"])
    
    if action == "Tambah":
        st.subheader("Tambah Data Supplier")
        with st.form("form_tambah_supplier"):
            supplier_id = st.text_input("ID Supplier")
            supplier_name = st.text_input("Nama Supplier")
            address = st.text_input("Alamat")
            submit = st.form_submit_button("Simpan")
            
            if submit:
                if not supplier_id or not supplier_name or not address:
                    st.error("Semua field wajib diisi.")
                else:
                    tambah_supplier(supplier_id, supplier_name, address)
    
    elif action == "Lihat":
        st.subheader("Daftar Supplier")
        lihat_supplier()
    
    elif action == "Perbarui":
        st.subheader("Perbarui Data Supplier")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT supplier_id, supplier_name FROM supplier')
        supplier_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if supplier_list:
            supplier_ids = [f"{s[0]} - {s[1]}" for s in supplier_list]
            selected_supplier = st.selectbox("Pilih Supplier", supplier_ids)
            supplier_id = selected_supplier.split(" - ")[0]
            
            with st.form("form_perbarui_supplier"):
                supplier_name = st.text_input("Nama Supplier")
                address = st.text_input("Alamat")
                submit = st.form_submit_button("Perbarui")
                
                if submit:
                    if not supplier_name or not address:
                        st.error("Nama dan Alamat wajib diisi.")
                    else:
                        perbarui_supplier(supplier_id, supplier_name, address)
        else:
            st.info("Belum ada data supplier.")
    
    elif action == "Hapus":
        st.subheader("Hapus Data Supplier")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT supplier_id, supplier_name FROM supplier')
        supplier_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if supplier_list:
            supplier_ids = [f"{s[0]} - {s[1]}" for s in supplier_list]
            selected_supplier = st.selectbox("Pilih Supplier", supplier_ids)
            supplier_id = selected_supplier.split(" - ")[0]
            
            if st.button("Hapus"):
                hapus_supplier(supplier_id)
        else:
            st.info("Belum ada data supplier.")

# -------------------- BAHAN BAKU --------------------
def manage_bahan_baku():
    st.header("Kelola Data Bahan Baku")
    action = st.selectbox("Pilih Aksi", ["Tambah", "Lihat", "Perbarui", "Hapus"])
    
    if action == "Tambah":
        st.subheader("Tambah Data Bahan Baku")
        with st.form("form_tambah_bahan_baku"):
            bahan_id = st.text_input("ID Bahan Baku")
            nama_bahan = st.text_input("Nama Bahan")
            stock = st.number_input("Stock", min_value=0, step=1)
            satuan = st.selectbox("Satuan", ["kg", "liter", "butir", "pack", "pcs"])
            harga_bahan = st.number_input("Harga Bahan", min_value=0.0, step=1000.0)
            supplier_id = st.text_input("ID Supplier")
            submit = st.form_submit_button("Simpan")
            
            if submit:
                if not bahan_id or not nama_bahan or not satuan or not harga_bahan or not supplier_id:
                    st.error("Semua field wajib diisi.")
                else:
                    tambah_bahan_baku(bahan_id, nama_bahan, stock, satuan, harga_bahan, supplier_id)
    
    elif action == "Lihat":
        st.subheader("Daftar Bahan Baku")
        lihat_bahan_baku()
    
    elif action == "Perbarui":
        st.subheader("Perbarui Data Bahan Baku")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT bahan_id, nama_bahan FROM bahan_baku')
        bahan_baku_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if bahan_baku_list:
            bahan_ids = [f"{b[0]} - {b[1]}" for b in bahan_baku_list]
            selected_bahan = st.selectbox("Pilih Bahan Baku", bahan_ids)
            bahan_id = selected_bahan.split(" - ")[0]
            
            with st.form("form_perbarui_bahan_baku"):
                nama_bahan = st.text_input("Nama Bahan")
                stock = st.number_input("Stock", min_value=0, step=1)
                satuan = st.selectbox("Satuan", ["kg", "liter", "butir", "pack", "pcs"])
                harga_bahan = st.number_input("Harga Bahan", min_value=0.0, step=1000.0)
                supplier_id = st.text_input("ID Supplier")
                submit = st.form_submit_button("Perbarui")
                
                if submit:
                    if not nama_bahan or not satuan or not harga_bahan or not supplier_id:
                        st.error("Nama, Satuan, Harga Bahan, dan ID Supplier wajib diisi.")
                    else:
                        perbarui_bahan_baku(bahan_id, nama_bahan, stock, satuan, harga_bahan, supplier_id)
        else:
            st.info("Belum ada data bahan baku.")
    
    elif action == "Hapus":
        st.subheader("Hapus Data Bahan Baku")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT bahan_id, nama_bahan FROM bahan_baku')
        bahan_baku_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if bahan_baku_list:
            bahan_ids = [f"{b[0]} - {b[1]}" for b in bahan_baku_list]
            selected_bahan = st.selectbox("Pilih Bahan Baku", bahan_ids)
            bahan_id = selected_bahan.split(" - ")[0]
            
            if st.button("Hapus"):
                hapus_bahan_baku(bahan_id)
        else:
            st.info("Belum ada data bahan baku.")

# -------------------- MENU --------------------
def manage_menu():
    st.header("Kelola Data Menu")
    action = st.selectbox("Pilih Aksi", ["Tambah", "Lihat", "Perbarui", "Hapus"])
    
    if action == "Tambah":
        st.subheader("Tambah Data Menu")
        with st.form("form_tambah_menu"):
            menu_id = st.text_input("ID Menu")
            nama_menu = st.text_input("Nama Menu")
            harga = st.number_input("Harga Menu", min_value=0.0, step=1000.0)
            submit = st.form_submit_button("Simpan")
            
            if submit:
                if not menu_id or not nama_menu or not harga:
                    st.error("Semua field wajib diisi.")
                else:
                    tambah_menu(menu_id, nama_menu, harga)
    
    elif action == "Lihat":
        st.subheader("Daftar Menu")
        lihat_menu()
    
    elif action == "Perbarui":
        st.subheader("Perbarui Data Menu")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT menu_id, nama_menu FROM menu')
        menu_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if menu_list:
            menu_ids = [f"{m[0]} - {m[1]}" for m in menu_list]
            selected_menu = st.selectbox("Pilih Menu", menu_ids)
            menu_id = selected_menu.split(" - ")[0]
            
            with st.form("form_perbarui_menu"):
                nama_menu = st.text_input("Nama Menu")
                harga = st.number_input("Harga Menu", min_value=0.0, step=1000.0)
                submit = st.form_submit_button("Perbarui")
                
                if submit:
                    if not nama_menu or not harga:
                        st.error("Nama dan Harga Menu wajib diisi.")
                    else:
                        perbarui_menu(menu_id, nama_menu, harga)
        else:
            st.info("Belum ada data menu.")
    
    elif action == "Hapus":
        st.subheader("Hapus Data Menu")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT menu_id, nama_menu FROM menu')
        menu_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if menu_list:
            menu_ids = [f"{m[0]} - {m[1]}" for m in menu_list]
            selected_menu = st.selectbox("Pilih Menu", menu_ids)
            menu_id = selected_menu.split(" - ")[0]
            
            if st.button("Hapus"):
                hapus_menu(menu_id)
        else:
            st.info("Belum ada data menu.")

# -------------------- TRANSAKSI --------------------
def manage_transaksi():
    st.header("Kelola Data Transaksi")
    action = st.selectbox("Pilih Aksi", ["Tambah", "Lihat", "Perbarui", "Hapus"])
    
    if action == "Tambah":
        st.subheader("Tambah Data Transaksi")
        with st.form("form_tambah_transaksi"):
            transaksi_id = st.text_input("ID Transaksi")
            tanggal_pembelian = st.date_input("Tanggal Pembelian")
            pelanggan_id = st.text_input("ID Pelanggan")
            karyawan_id = st.text_input("ID Karyawan")
            total_transaksi = st.number_input("Total Transaksi", min_value=0.0, step=1000.0)
            submit = st.form_submit_button("Simpan")
            
            if submit:
                if not transaksi_id or not tanggal_pembelian or not total_transaksi:
                    st.error("Semua field wajib diisi.")
                else:
                    tambah_transaksi(transaksi_id, tanggal_pembelian, pelanggan_id, karyawan_id, total_transaksi)
    
    elif action == "Lihat":
        st.subheader("Daftar Transaksi")
        lihat_transaksi()
    
    elif action == "Perbarui":
        st.subheader("Perbarui Data Transaksi")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT transaksi_id, tanggal_pembelian FROM transaksi')
        transaksi_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if transaksi_list:
            transaksi_ids = [f"{t[0]} - {t[1]}" for t in transaksi_list]
            selected_transaksi = st.selectbox("Pilih Transaksi", transaksi_ids)
            transaksi_id = selected_transaksi.split(" - ")[0]
            
            with st.form("form_perbarui_transaksi"):
                tanggal_pembelian = st.date_input("Tanggal Pembelian")
                pelanggan_id = st.text_input("ID Pelanggan")
                karyawan_id = st.text_input("ID Karyawan")
                total_transaksi = st.number_input("Total Transaksi", min_value=0.0, step=1000.0)
                submit = st.form_submit_button("Perbarui")
                
                if submit:
                    if not tanggal_pembelian or not total_transaksi:
                        st.error("Tanggal dan Total Transaksi wajib diisi.")
                    else:
                        perbarui_transaksi(transaksi_id, tanggal_pembelian, pelanggan_id, karyawan_id, total_transaksi)
        else:
            st.info("Belum ada data transaksi.")
    
    elif action == "Hapus":
        st.subheader("Hapus Data Transaksi")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT transaksi_id, tanggal_pembelian FROM transaksi')
        transaksi_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if transaksi_list:
            transaksi_ids = [f"{t[0]} - {t[1]}" for t in transaksi_list]
            selected_transaksi = st.selectbox("Pilih Transaksi", transaksi_ids)
            transaksi_id = selected_transaksi.split(" - ")[0]
            
            if st.button("Hapus"):
                hapus_transaksi(transaksi_id)
        else:
            st.info("Belum ada data transaksi.")

# -------------------- FEEDBACK --------------------
def manage_feedback():
    st.header("Kelola Data Feedback")
    action = st.selectbox("Pilih Aksi", ["Tambah", "Lihat", "Perbarui", "Hapus"])
    
    if action == "Tambah":
        st.subheader("Tambah Data Feedback")
        with st.form("form_tambah_feedback"):
            feedback_id = st.text_input("ID Feedback")
            pelanggan_id = st.text_input("ID Pelanggan")
            karyawan_id = st.text_input("ID Karyawan")
            tanggal = st.date_input("Tanggal")
            rating = st.slider("Rating", min_value=1, max_value=5, step=1)
            komentar = st.text_area("Komentar")
            submit = st.form_submit_button("Simpan")
            
            if submit:
                if not feedback_id or not pelanggan_id or not karyawan_id or not tanggal or not rating:
                    st.error("Semua field wajib diisi kecuali komentar.")
                else:
                    tambah_feedback(feedback_id, pelanggan_id, karyawan_id, tanggal, rating, komentar)
    
    elif action == "Lihat":
        st.subheader("Daftar Feedback")
        lihat_feedback()
    
    elif action == "Perbarui":
        st.subheader("Perbarui Data Feedback")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT feedback_id, tanggal FROM feedback')
        feedback_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if feedback_list:
            feedback_ids = [f"{f[0]} - {f[1]}" for f in feedback_list]
            selected_feedback = st.selectbox("Pilih Feedback", feedback_ids)
            feedback_id = selected_feedback.split(" - ")[0]
            
            with st.form("form_perbarui_feedback"):
                pelanggan_id = st.text_input("ID Pelanggan")
                karyawan_id = st.text_input("ID Karyawan")
                tanggal = st.date_input("Tanggal")
                rating = st.slider("Rating", min_value=1, max_value=5, step=1)
                komentar = st.text_area("Komentar")
                submit = st.form_submit_button("Perbarui")
                
                if submit:
                    if not pelanggan_id or not karyawan_id or not tanggal or not rating:
                        st.error("ID Pelanggan, ID Karyawan, Tanggal, dan Rating wajib diisi.")
                    else:
                        perbarui_feedback(feedback_id, pelanggan_id, karyawan_id, tanggal, rating, komentar)
        else:
            st.info("Belum ada data feedback.")
    
    elif action == "Hapus":
        st.subheader("Hapus Data Feedback")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT feedback_id, tanggal FROM feedback')
        feedback_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if feedback_list:
            feedback_ids = [f"{f[0]} - {f[1]}" for f in feedback_list]
            selected_feedback = st.selectbox("Pilih Feedback", feedback_ids)
            feedback_id = selected_feedback.split(" - ")[0]
            
            if st.button("Hapus"):
                hapus_feedback(feedback_id)
        else:
            st.info("Belum ada data feedback.")

# -------------------- ABSENSI SIDIK JARI --------------------
def manage_absensi():
    st.header("Kelola Data Absensi Sidik Jari")
    action = st.selectbox("Pilih Aksi", ["Tambah", "Lihat", "Perbarui", "Hapus"])
    
    if action == "Tambah":
        st.subheader("Tambah Data Absensi")
        with st.form("form_tambah_absensi"):
            absensi_id = st.text_input("ID Absensi")
            karyawan_id = st.text_input("ID Karyawan")
            tanggal = st.date_input("Tanggal")
            status = st.selectbox("Status", ["Hadir", "Tidak Hadir", "Izin", "Cuti"])
            submit = st.form_submit_button("Simpan")
            
            if submit:
                if not absensi_id or not karyawan_id or not tanggal or not status:
                    st.error("Semua field wajib diisi.")
                else:
                    tambah_absensi(absensi_id, karyawan_id, tanggal, status)
    
    elif action == "Lihat":
        st.subheader("Daftar Absensi")
        lihat_absensi()
    
    elif action == "Perbarui":
        st.subheader("Perbarui Data Absensi")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT absensi_id, tanggal FROM absensi')
        absensi_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if absensi_list:
            absensi_ids = [f"{a[0]} - {a[1]}" for a in absensi_list]
            selected_absensi = st.selectbox("Pilih Absensi", absensi_ids)
            absensi_id = selected_absensi.split(" - ")[0]
            
            with st.form("form_perbarui_absensi"):
                karyawan_id = st.text_input("ID Karyawan")
                tanggal = st.date_input("Tanggal")
                status = st.selectbox("Status", ["Hadir", "Tidak Hadir", "Izin", "Cuti"])
                submit = st.form_submit_button("Perbarui")
                
                if submit:
                    if not karyawan_id or not tanggal or not status:
                        st.error("ID Karyawan, Tanggal, dan Status wajib diisi.")
                    else:
                        perbarui_absensi(absensi_id, karyawan_id, tanggal, status)
        else:
            st.info("Belum ada data absensi.")
    
    elif action == "Hapus":
        st.subheader("Hapus Data Absensi")
        conn = get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute('SELECT absensi_id, tanggal FROM absensi')
        absensi_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if absensi_list:
            absensi_ids = [f"{a[0]} - {a[1]}" for a in absensi_list]
            selected_absensi = st.selectbox("Pilih Absensi", absensi_ids)
            absensi_id = selected_absensi.split(" - ")[0]
            
            if st.button("Hapus"):
                hapus_absensi(absensi_id)
        else:
            st.info("Belum ada data absensi.")

# -------------------- FUNGSI LAPORAN --------------------
def total_transaksi_per_hari():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT tanggal_pembelian, SUM(total_transaksi) as total
            FROM transaksi
            GROUP BY tanggal_pembelian
            ORDER BY tanggal_pembelian DESC
        ''')
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows, columns=['Tanggal', 'Total Transaksi'])
            st.dataframe(df)
            
            # Opsi download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='total_transaksi_per_hari.csv',
                mime='text/csv',
            )
        else:
            st.info("Belum ada transaksi.")
    except Exception as e:
        st.error(f"Error fetching laporan: {e}")
    finally:
        cursor.close()
        conn.close()

def stok_bahan_baku_laporan():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT nama_bahan, stock, satuan
            FROM bahan_baku
            ORDER BY nama_bahan ASC
        ''')
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows, columns=['Nama Bahan', 'Stok', 'Satuan'])
            st.dataframe(df)
            
            # Opsi download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='stok_bahan_baku.csv',
                mime='text/csv',
            )
        else:
            st.info("Belum ada data bahan baku.")
    except Exception as e:
        st.error(f"Error fetching laporan: {e}")
    finally:
        cursor.close()
        conn.close()

def feedback_per_karyawan():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT k.employee_name, AVG(f.rating) as rata_rata_rating
            FROM feedback f
            JOIN karyawan k ON f.karyawan_id = k.karyawan_id
            GROUP BY k.employee_name
            ORDER BY rata_rata_rating DESC
        ''')
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows, columns=['Nama Karyawan', 'Rata-rata Rating'])
            st.dataframe(df)
            
            # Opsi download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='feedback_per_karyawan.csv',
                mime='text/csv',
            )
        else:
            st.info("Belum ada feedback.")
    except Exception as e:
        st.error(f"Error fetching laporan: {e}")
    finally:
        cursor.close()
        conn.close()

def absensi_per_karyawan():
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT k.employee_name, COUNT(a.absensi_id) as total_absensi,
                   SUM(CASE WHEN a.status = 'Hadir' THEN 1 ELSE 0 END) as hadir,
                   SUM(CASE WHEN a.status = 'Tidak Hadir' THEN 1 ELSE 0 END) as tidak_hadir,
                   SUM(CASE WHEN a.status = 'Izin' THEN 1 ELSE 0 END) as izin,
                   SUM(CASE WHEN a.status = 'Cuti' THEN 1 ELSE 0 END) as cuti
            FROM absensi a
            JOIN karyawan k ON a.karyawan_id = k.karyawan_id
            GROUP BY k.employee_name
            ORDER BY k.employee_name ASC
        ''')
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows, columns=['Nama Karyawan', 'Total Absensi', 'Hadir', 'Tidak Hadir', 'Izin', 'Cuti'])
            st.dataframe(df)
            
            # Opsi download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='absensi_per_karyawan.csv',
                mime='text/csv',
            )
        else:
            st.info("Belum ada data absensi.")
    except Exception as e:
        st.error(f"Error fetching laporan absensi: {e}")
    finally:
        cursor.close()
        conn.close()

# -------------------- MAIN APP --------------------
def main():
    st.set_page_config(page_title="Restorify", layout="wide")
    st.title("Restorify")
    
    # Pastikan tabel sudah dibuat dan data awal sudah diisi
    create_tables()
    
    menu_options = [
        "Beranda",
        "Karyawan",
        "Pelanggan",
        "Supplier",
        "Bahan Baku",
        "Menu",
        "Transaksi",
        "Feedback",
        "Absensi Sidik Jari",
        "Laporan"  # Tambahkan menu laporan
    ]
    
    selected_menu = st.sidebar.selectbox("Navigasi", menu_options)
    
    if selected_menu == "Beranda":
        st.subheader("Selamat Datang di Sistem Manajemen Restoran")
        st.write("""
            Aplikasi ini membantu Anda dalam mengelola operasi restoran secara efisien.
            Anda dapat mengelola data karyawan, pelanggan, supplier, bahan baku, menu, transaksi,
            feedback, dan juga fitur absensi sidik jari (mockup). Tubes Manajemen Data (Radhitya, Chindy, Hasyir)
        """)
        st.image(
            "https://img.freepik.com/free-vector/woman-wearing-medical-mask-client_52683-41295.jpg",
            use_container_width=True
        )
    
    elif selected_menu == "Karyawan":
        manage_karyawan()
    
    elif selected_menu == "Pelanggan":
        manage_pelanggan()
    
    elif selected_menu == "Supplier":
        manage_supplier()
    
    elif selected_menu == "Bahan Baku":
        manage_bahan_baku()
    
    elif selected_menu == "Menu":
        manage_menu()
    
    elif selected_menu == "Transaksi":
        manage_transaksi()
    
    elif selected_menu == "Feedback":
        manage_feedback()
    
    elif selected_menu == "Absensi Sidik Jari":
        manage_absensi()
    
    elif selected_menu == "Laporan":
        st.header("Laporan Sistem Manajemen Restoran")
        laporan_options = ["Total Transaksi per Hari", "Stok Bahan Baku", "Feedback per Karyawan", "Absensi per Karyawan"]
        selected_laporan = st.selectbox("Pilih Laporan", laporan_options)
        
        if selected_laporan == "Total Transaksi per Hari":
            total_transaksi_per_hari()
        elif selected_laporan == "Stok Bahan Baku":
            stok_bahan_baku_laporan()
        elif selected_laporan == "Feedback per Karyawan":
            feedback_per_karyawan()
        elif selected_laporan == "Absensi per Karyawan":
            absensi_per_karyawan()

# -------------------- PENUTUP --------------------
if __name__ == "__main__":
    main()
