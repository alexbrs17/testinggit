# NOVLI Bot 🤖

Bot Telegram untuk manajemen tiket FEGE (Ethernet First-Mile) dan monitoring performa jaringan di wilayah Sumbagut.

## Fitur Utama

- **Manajemen Tiket**: Membuat, menutup, dan memantau status tiket teknis
- **Ringkasan & Statistik**: Menampilkan ringkasan tiket berdasarkan prioritas dan status
- **Monitoring KPI**: Melihat laporan grafik performa jaringan (payload, availability, packet loss, TNL)
- **Sinkronisasi Database**: Sinkronisasi data dari Sharepoint dan otomatis membuat tiket
- **Manajemen User**: Registrasi user dengan role berbeda (ADMIN, PIC, GUEST)
- **Import Data**: Mengimpor data CSV/Excel ke database
- **Role-Based Access**: Kontrol akses berdasarkan role dan NOP (Network Operating Point)

## Prasyarat

- Python 3.8 atau lebih tinggi
- PostgreSQL 12 atau lebih tinggi
- Telegram Bot Token (dari [@BotFather](https://t.me/BotFather))
- pip (Python Package Manager)

## Instalasi

### 1. Clone Repository

```bash
cd /path/to/your/projects
git clone git@github.com:budpoetra/novli-bot.git
cd novli-bot
```

### 2. Buat Virtual Environment

```bash
# Untuk Windows
python -m venv venv
venv\Scripts\activate

# Untuk macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

#### a. Buat Database di PostgreSQL

```sql
CREATE DATABASE my_postgres;
```

#### b. Jalankan Schema SQL

```bash
psql -U postgres -d my_postgres -f database.sql
```

Atau gunakan database tool favorit Anda untuk menjalankan file `database.sql`.

### 5. Konfigurasi Environment

Salin file `.env.example` menjadi `.env` dan sesuaikan nilai-nilainya:

```bash
cp .env.example .env
```

Edit `.env` dengan informasi berikut:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Database Configuration
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=my_postgres
DB_USER=postgres
DB_PASSWORD=your_password

# Bot Settings
BOT_TIMEZONE=Asia/Jakarta
AUTH_ENABLED=true

# NOP Configuration
NOP_ALLOWED=ACEH,BINJAI,MEDAN,PEMATANG SIANTAR,PADANG SIDEMPUAN,RANTAU PRAPAT,ALL

# Role-Based Commands
PIC_ALLOWED_COMMANDS=start,help,summary,list,ticket,close,kpi
GUEST_ALLOWED_COMMANDS=start,help,summary

# Group Configuration
GROUP_ID_ALLOWED=ACEH:-5237206510,BINJAI:-5237206511,MEDAN:-5237206512,PEMATANG SIANTAR:-5237206513,PADANG SIDEMPUAN:-5237206519,RANTAU PRAPAT:-5237206515

# Ticket Settings
REOPEN_TICKET_THRESHOLD=3
```

**Petunjuk mendapatkan Bot Token:**

1. Buka [@BotFather](https://t.me/BotFather) di Telegram
2. Ketik `/newbot` dan ikuti instruksi
3. Salin token yang diberikan ke variabel `TELEGRAM_BOT_TOKEN`

## Menjalankan Bot

### 1. Pastikan Virtual Environment Aktif

```bash
# Untuk Windows
venv\Scripts\activate

# Untuk macOS/Linux
source venv/bin/activate
```

### 2. Jalankan Bot

```bash
python bot.py
```

Anda akan melihat output seperti:

```
2026-01-17 10:30:45 | INFO | __main__ | Initializing Telegram bot...
2026-01-17 10:30:46 | INFO | __main__ | Database connection OK and tables verified.
2026-01-17 10:30:47 | INFO | __main__ | Bot started
```

### 3. Test Bot

Kirim pesan `/start` ke bot di Telegram untuk memastikan bot berjalan dengan baik.

**Last Updated**: 18 Januari 2026
"# testinggit" 
