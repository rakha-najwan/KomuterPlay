import os
import sys
import json
import sqlite3

# Pastikan folder utama proyek terbaca saat file ini di-Run langsung di VS Code
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.models import AkunKomuter, TiketPerjalanan

DB_PATH = os.path.join(BASE_DIR, "data", "komuterplay.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                saldo_emoney INTEGER NOT NULL,
                poin INTEGER NOT NULL,
                streak INTEGER NOT NULL,
                kmt_nomor TEXT,
                kmt_saldo INTEGER DEFAULT 0,
                voucher_json TEXT DEFAULT '[]'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mutasi_saldo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                tipe TEXT NOT NULL,
                nominal INTEGER NOT NULL,
                waktu TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS riwayat_tiket (
                id_tiket TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                asal TEXT NOT NULL,
                tujuan TEXT NOT NULL,
                moda_json TEXT NOT NULL,
                total_tarif INTEGER NOT NULL,
                poin_reward INTEGER NOT NULL,
                waktu_pesan TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)


def simpan_akun(user: AkunKomuter) -> None:
    init_db()
    kmt_nomor = user.kmt.nomor_kartu if user.kmt else None
    kmt_saldo = user.kmt.get_saldo() if user.kmt else 0
    voucher_json = json.dumps(user.voucher_aktif)

    with get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO users
            (user_id, nama, saldo_emoney, poin, streak, kmt_nomor, kmt_saldo, voucher_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user.user_id,
            user.nama,
            user.dompet.get_saldo(),
            user.get_poin(),
            user.streak,
            kmt_nomor,
            kmt_saldo,
            voucher_json
        ))

        conn.execute("DELETE FROM mutasi_saldo WHERE user_id = ?", (user.user_id,))
        for tipe, nominal, waktu in user.dompet.riwayat_mutasi:
            conn.execute("""
                INSERT INTO mutasi_saldo (user_id, tipe, nominal, waktu)
                VALUES (?, ?, ?, ?)
            """, (user.user_id, tipe, nominal, waktu))

        for tiket in user.riwayat_tiket:
            conn.execute("""
                INSERT OR REPLACE INTO riwayat_tiket
                (id_tiket, user_id, asal, tujuan, moda_json, total_tarif, poin_reward, waktu_pesan, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tiket.id_tiket,
                user.user_id,
                tiket.asal,
                tiket.tujuan,
                json.dumps(tiket.daftar_moda),
                tiket.total_tarif,
                tiket.poin_reward,
                tiket.waktu_pesan,
                tiket.status
            ))


def muat_akun(user_id: str = "U01", nama_default: str = "Budi Komuter") -> AkunKomuter:
    init_db()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()

        if row is None:
            user_baru = AkunKomuter(user_id, nama_default, saldo_awal=50000, poin_awal=120)
            simpan_akun(user_baru)
            return user_baru

        user = AkunKomuter(
            row["user_id"],
            row["nama"],
            saldo_awal=row["saldo_emoney"],
            poin_awal=row["poin"]
        )
        user.streak = row["streak"]
        user.voucher_aktif = json.loads(row["voucher_json"])

        if row["kmt_nomor"]:
            user.tautkan_kmt(row["kmt_nomor"], row["kmt_saldo"])

        mutasi_rows = conn.execute(
            "SELECT tipe, nominal, waktu FROM mutasi_saldo WHERE user_id = ? ORDER BY id ASC",
            (user_id,)
        ).fetchall()
        user.dompet.riwayat_mutasi = [(m["tipe"], m["nominal"], m["waktu"]) for m in mutasi_rows]

        tiket_rows = conn.execute(
            "SELECT * FROM riwayat_tiket WHERE user_id = ?",
            (user_id,)
        ).fetchall()
        for t in tiket_rows:
            tiket_obj = TiketPerjalanan(
                t["asal"],
                t["tujuan"],
                json.loads(t["moda_json"]),
                t["total_tarif"],
                t["poin_reward"]
            )
            tiket_obj.id_tiket = t["id_tiket"]
            tiket_obj.waktu_pesan = t["waktu_pesan"]
            tiket_obj.status = t["status"]
            user.riwayat_tiket.append(tiket_obj)

        return user


if __name__ == "__main__":
    akun = muat_akun("U01", "Budi Komuter")
    print("Saldo awal dari DB:", akun.dompet.get_saldo())
    akun.dompet.top_up(25000)
    simpan_akun(akun)

    akun_reload = muat_akun("U01")
    print("Saldo setelah reload DB:", akun_reload.dompet.get_saldo())
    print("Riwayat mutasi:", akun_reload.dompet.riwayat_mutasi)