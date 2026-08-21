# Ledger — Personal Expense Tracker

Aplikasi pencatatan keuangan pribadi berbasis Django, dibangun sebagai proyek kedua dalam Django Project Roadmap (Level: Beginner → Intermediate). Fokus utama proyek ini adalah mengubah aplikasi dari data global menjadi data yang terisolasi per user, sekaligus melatih penggunaan Django Authentication dan integrasi dengan database eksternal (Supabase/PostgreSQL).

---

## Daftar Isi

- [Problem Statement](#problem-statement)
- [Objective](#objective)
- [Fitur](#fitur)
- [Tech Stack](#tech-stack)
- [Architecture Diagram](#architecture-diagram)
- [ERD (Entity Relationship Diagram)](#erd-entity-relationship-diagram)
- [Model & Permission](#model--permission)
- [Instalasi & Setup](#instalasi--setup)
- [Environment Variables](#environment-variables)
- [Menjalankan Aplikasi](#menjalankan-aplikasi)
- [Testing Guide](#testing-guide)
- [Struktur Project](#struktur-project)
- [Known Limitations](#known-limitations)
- [Future Improvements](#future-improvements)
- [Lessons Learned & Design Trade-offs](#lessons-learned--design-trade-offs)

---

## Problem Statement

Banyak orang kesulitan melacak ke mana uang mereka pergi setiap bulan karena pencatatan manual (buku/spreadsheet) mudah terlewat dan tidak memberi ringkasan otomatis. Dibutuhkan aplikasi sederhana yang bisa mencatat pemasukan dan pengeluaran, memberi ringkasan saldo secara instan, serta menjaga privasi data — setiap user hanya bisa melihat data miliknya sendiri.

## Objective

Membangun aplikasi Django full-stack yang mendemonstrasikan:
1. Django Authentication (register, login, logout)
2. Relasi data berbasis `ForeignKey` ke `User` dengan isolasi data yang ketat
3. Business logic aggregation (total income, expense, balance)
4. Integrasi ke database eksternal (Supabase PostgreSQL) di luar SQLite default
5. UI/UX yang konsisten dan profesional menggunakan design system custom

## Fitur

- **Autentikasi penuh** — Register, Login, Logout, dengan validasi password bawaan Django
- **CRUD Transaksi** — Create, Read, Update, Delete untuk transaksi income/expense
- **Isolasi data per user** — setiap user hanya dapat melihat, mengedit, dan menghapus transaksi miliknya sendiri
- **Dashboard ringkasan** — kartu Saldo, Pemasukan, dan Pengeluaran yang dihitung otomatis dari data real-time
- **Filter & Search** — filter transaksi berdasarkan tipe, kategori, dan rentang tanggal
- **Monthly Report** — laporan bulanan dengan breakdown pengeluaran per kategori, dilengkapi visualisasi bar proporsional
- **Dukungan dwibahasa** — laporan bulanan dapat ditampilkan dalam Bahasa Indonesia atau Bahasa Inggris
- **Format mata uang lokal** — semua nominal ditampilkan dalam format Rupiah standar (`Rp 1.800.000,00`)
- **Validasi form** — mencegah input amount negatif dan field wajib yang kosong

## Tech Stack

| Kategori | Teknologi |
|---|---|
| Backend Framework | Django 5.x |
| Database | PostgreSQL (via Supabase) |
| Driver Database | psycopg2-binary |
| Environment Management | python-decouple |
| Frontend | Django Templates, HTML/CSS murni (tanpa framework JS) |
| Font | Fraunces (display), Inter (body), IBM Plex Mono (data numerik) |

## Architecture Diagram

```
Browser (User)
     │
     ▼
Django Views (expenses/views.py)
     │
     ├── Authentication (django.contrib.auth)
     ├── Transaction CRUD (login_required)
     ├── Dashboard Aggregation
     └── Monthly Report Aggregation
     │
     ▼
Django ORM (Models)
     │
     ▼
psycopg2 (PostgreSQL Driver)
     │
     ▼
Supabase (PostgreSQL Database — Session Pooler)
```

Semua request yang membutuhkan data transaksi wajib melalui `@login_required` dan query difilter berdasarkan `request.user`, memastikan tidak ada akses lintas-user baik secara sengaja maupun tidak sengaja (misal manipulasi ID di URL).

## ERD (Entity Relationship Diagram)

```
┌─────────────────────┐         ┌──────────────────────────┐
│        User          │         │       Transaction          │
│  (django.contrib.auth)│        │                            │
├─────────────────────┤         ├──────────────────────────┤
│ id (PK)              │◄───────┤ id (PK)                    │
│ username              │  1   N │ user_id (FK)                │
│ password              │        │ type (IN/EX)                │
│ email                 │        │ category                    │
└─────────────────────┘         │ amount                      │
                                  │ description                 │
                                  │ transaction_date             │
                                  │ created_at                   │
                                  │ updated_at                   │
                                  └──────────────────────────┘
```

**Relasi:** Satu `User` dapat memiliki banyak `Transaction` (one-to-many), dihubungkan lewat `ForeignKey(User, on_delete=models.CASCADE)`. Jika user dihapus, seluruh transaksi miliknya ikut terhapus.

## Model & Permission

### Model `Transaction`

| Field | Tipe | Keterangan |
|---|---|---|
| `user` | ForeignKey → User | Wajib, `on_delete=CASCADE` |
| `type` | CharField (choices) | `'IN'` untuk Income, `'EX'` untuk Expense |
| `category` | CharField | Kategori bebas, mis. "Groceries", "Freelance" |
| `amount` | DecimalField | `max_digits=12, decimal_places=2`, tidak boleh ≤ 0 |
| `description` | TextField | Opsional (`blank=True`) |
| `transaction_date` | DateField | Tanggal transaksi terjadi |
| `created_at` | DateTimeField | Otomatis terisi saat record dibuat |
| `updated_at` | DateTimeField | Otomatis terupdate saat record diubah |

### Aturan Permission

- Semua view Transaction dilindungi `@login_required` — user yang belum login otomatis diarahkan ke halaman login.
- Setiap query detail/edit/delete transaksi menggunakan pola:
  ```python
  get_object_or_404(Transaction, pk=pk, user=request.user)
  ```
  Kombinasi `pk` **dan** `user` ini memastikan user tidak dapat mengakses, mengedit, atau menghapus transaksi milik user lain — percobaan akses akan menghasilkan `404 Not Found`, bukan izin ditolak (untuk menghindari kebocoran informasi soal keberadaan data tersebut).

## Instalasi & Setup

### Prasyarat
- Python 3.10+
- Akun [Supabase](https://supabase.com) (tier gratis sudah cukup)
- Git

### Langkah Instalasi

```bash
# 1. Clone repository
git clone <url-repo-anda>
cd Personal-Expense-Tracker

# 2. Buat & aktifkan virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Buat file .env (lihat bagian Environment Variables di bawah)

# 5. Jalankan migrasi
python manage.py migrate

# 6. Buat superuser (opsional, untuk akses /admin/)
python manage.py createsuperuser

# 7. Jalankan server
python manage.py runserver
```

Buka `http://127.0.0.1:8000/` di browser.

## Environment Variables

Buat file `.env` di root project (sejajar dengan `manage.py`) dengan isi berikut:

```env
SECRET_KEY=<generate dengan get_random_secret_key()>
DEBUG=True
DB_NAME=postgres
DB_USER=postgres.<project-ref-anda>
DB_PASSWORD=<password-database-supabase-anda>
DB_HOST=aws-0-<region>.pooler.supabase.com
DB_PORT=5432
```

**Catatan penting:**
- Kredensial database diambil dari Supabase Dashboard → tombol **Connect** → pilih **Session Pooler** (bukan Direct Connection, karena Direct Connection menggunakan IPv6 yang tidak selalu didukung oleh semua jaringan).
- `SECRET_KEY` untuk Django dan API key Supabase adalah **dua hal yang berbeda** — jangan tertukar.
- File `.env` **tidak boleh** di-commit ke git. Pastikan sudah tercantum di `.gitignore`.

## Menjalankan Aplikasi

```bash
python manage.py runserver
```

| Halaman | URL |
|---|---|
| Dashboard | `/dashboard/` |
| Login | `/accounts/login/` |
| Register | `/register/` |
| Daftar Transaksi | `/transactions/` |
| Tambah Transaksi | `/transactions/add/` |
| Laporan Bulanan | `/reports/monthly/` |
| Django Admin | `/admin/` |

## Testing Guide

Berikut adalah skenario testing manual yang telah dilakukan dan wajib diulang setiap ada perubahan signifikan pada kode:

1. **Alur Autentikasi** — Register akun baru → redirect ke login → login berhasil → redirect ke dashboard.
2. **CRUD Transaksi** — Tambah transaksi (income & expense) → cek muncul di list dan dashboard → edit transaksi → cek perubahan tersimpan → hapus transaksi → cek muncul halaman konfirmasi sebelum benar-benar terhapus.
3. **Validasi Form** — Submit amount negatif/nol → harus ditolak. Submit field wajib kosong → harus ditolak dengan pesan error yang jelas.
4. **Isolasi Data Antar-User** *(paling kritis)* — Login sebagai User A, catat ID salah satu transaksinya. Login sebagai User B, pastikan transaksi User A tidak muncul di list maupun dashboard User B. Coba akses langsung `/transactions/<id>/edit/` milik User A dari sesi User B — harus menghasilkan `404`, bukan form edit.
5. **Akses Tanpa Login** — Akses `/dashboard/` atau `/transactions/` tanpa sesi login aktif — harus redirect otomatis ke halaman login.
6. **Filter & Search** — Filter berdasarkan tipe, kategori (`icontains`, case-insensitive), dan rentang tanggal, baik sendiri maupun kombinasi. Reset filter harus menampilkan seluruh data kembali.
7. **Monthly Report** — Pilih bulan dengan data → cek breakdown kategori dan bar proporsional. Pilih bulan tanpa data → harus menampilkan pesan "tidak ada transaksi", bukan error. Toggle bahasa ID/EN → nama bulan berubah, filter bulan/tahun tidak ter-reset.
8. **Responsive** — Diuji pada breakpoint mobile (contoh: iPhone 12 Pro), layout kartu ringkasan otomatis menyusun ulang menjadi satu kolom.

## Struktur Project

```
Personal-Expense-Tracker/
├── config/                    # Django project settings
│   ├── settings.py
│   └── urls.py
├── expenses/                  # Django app utama
│   ├── models.py              # Model Transaction
│   ├── forms.py                # TransactionForm (ModelForm)
│   ├── views.py                # Semua view (auth, CRUD, dashboard, report)
│   ├── urls.py
│   └── templatetags/
│       └── currency_filters.py # Custom filter format Rupiah
├── templates/
│   ├── base.html                # Layout induk + design system
│   ├── registration/
│   │   ├── login.html
│   │   └── register.html
│   └── expenses/
│       ├── dashboard.html
│       ├── transaction_list.html
│       ├── transaction_form.html
│       ├── transaction_confirm_delete.html
│       └── monthly_report.html
├── .env                        # Kredensial (tidak di-commit)
├── .gitignore
├── requirements.txt
└── manage.py
```

## Known Limitations

- Kategori transaksi masih berupa `CharField` bebas teks, belum berupa model `Category` terpisah — berpotensi menghasilkan variasi penulisan kategori yang tidak konsisten (mis. "Coffee" vs "coffee").
- Belum ada fitur pagination pada daftar transaksi — untuk jumlah data yang sangat besar, performa list bisa menurun.
- Password reset menggunakan console email backend (development mode), belum terhubung ke SMTP asli untuk pengiriman email produksi.
- Belum ada export data (CSV/PDF) untuk laporan bulanan.
- Currency filter (`rupiah`) hanya mendukung format Rupiah, belum multi-currency.

## Future Improvements

- Migrasi field `category` menjadi model `Category` terpisah dengan relasi `ForeignKey`, memungkinkan manajemen kategori dan mencegah duplikasi penulisan.
- Tambahkan pagination pada daftar transaksi.
- Tambahkan grafik tren pengeluaran bulanan (line/bar chart) menggunakan library seperti Chart.js.
- Export laporan bulanan ke PDF/CSV.
- Setup SMTP asli untuk fitur password reset di lingkungan produksi.
- Tambahkan dark mode.

## Lessons Learned & Design Trade-offs

- **`ForeignKey` + filter eksplisit vs Row Level Security (RLS):** Karena aplikasi ini terhubung ke Supabase melalui koneksi database langsung (bukan Supabase Client API), isolasi data ditangani sepenuhnya di level aplikasi Django (`filter(user=request.user)`), bukan lewat RLS Supabase. Trade-off ini disadari sejak awal — cocok untuk skala aplikasi personal, namun untuk skala multi-tenant yang lebih besar, kombinasi dengan RLS akan lebih aman sebagai lapisan pertahanan tambahan.
- **Direct Connection vs Session Pooler:** Direct Connection Supabase menggunakan IPv6 secara default, yang ternyata tidak didukung oleh sebagian jaringan pengembangan. Session Pooler dipilih sebagai solusi karena mendukung IPv4, dengan trade-off overhead koneksi yang sedikit lebih tinggi dibanding koneksi langsung — dapat diterima untuk skala development/personal project.
- **`choices` kode singkat (`'IN'`/`'EX'`) vs kata penuh (`'income'`/`'expense'`):** Keputusan menyimpan kode singkat di database lebih hemat ruang penyimpanan, namun mengharuskan konsistensi ketat di seluruh view dan template — pelajaran pentingnya adalah mendefinisikan `choices` di satu tempat sejak awal dan tidak mengubahnya di tengah jalan tanpa migrasi data yang sesuai.
- **`commit=False` pada form save:** Pola ini penting dipahami untuk kasus di mana field model (seperti `user`) sengaja tidak dimasukkan ke form demi keamanan, namun tetap wajib diisi sebelum data disimpan ke database.

---

*Proyek ini merupakan bagian dari Django Project Roadmap — Level 2: Personal Expense Tracker, dengan fokus kompetensi Authentication dan isolasi data user-specific.*