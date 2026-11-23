import uuid
from datetime import datetime


class DompetEmoney:
    def __init__(self, saldo_awal: int = 0):
        self.__saldo = saldo_awal

    def get_saldo(self) -> int:
        return self.__saldo

    def top_up(self, nominal: int) -> bool:
        if nominal <= 0:
            return False
        self.__saldo += nominal
        return True

    def bayar(self, nominal: int) -> bool:
        if nominal <= 0 or self.__saldo < nominal:
            return False
        self.__saldo -= nominal
        return True


class KartuMultiTrip:
    def __init__(self, nomor_kartu: str, saldo_awal: int = 0):
        self.nomor_kartu = nomor_kartu
        self.__saldo = saldo_awal

    def get_saldo(self) -> int:
        return self.__saldo

    def top_up(self, nominal: int) -> bool:
        if nominal <= 0:
            return False
        self.__saldo += nominal
        return True

    def tap_bayar(self, nominal: int) -> bool:
        if nominal <= 0 or self.__saldo < nominal:
            return False
        self.__saldo -= nominal
        return True


class TiketPerjalanan:
    def __init__(self, asal: str, tujuan: str, daftar_moda: list, total_tarif: int, poin_reward: int):
        self.id_tiket = f"TKT-{uuid.uuid4().hex[:6].upper()}"
        self.asal = asal
        self.tujuan = tujuan
        self.daftar_moda = daftar_moda
        self.total_tarif = total_tarif
        self.poin_reward = poin_reward
        self.waktu_pesan = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.status = "AKTIF"

    def __str__(self) -> str:
        rute_str = " -> ".join(self.daftar_moda)
        return f"[{self.id_tiket}] {self.asal} ke {self.tujuan} ({rute_str}) | Rp{self.total_tarif:,}"


class Misi:
    def __init__(self, id_misi: str, judul: str, target: int, reward_poin: int):
        self.id_misi = id_misi
        self.judul = judul
        self.target = target
        self.progres = 0
        self.reward_poin = reward_poin
        self.selesai = False

    def tambah_progres(self, langkah: int = 1) -> bool:
        if self.selesai:
            return False
        self.progres += langkah
        if self.progres >= self.target:
            self.progres = self.target
            self.selesai = True
            return True  # Menandakan misi baru saja tuntas
        return False


class AkunKomuter:
    def __init__(self, user_id: str, nama: str, saldo_awal: int = 50000, poin_awal: int = 0):
        self.user_id = user_id
        self.nama = nama
        self.__poin = poin_awal
        self.streak = 1
        self.dompet = DompetEmoney(saldo_awal)
        self.kmt = None
        self.riwayat_tiket = []

    def get_poin(self) -> int:
        return self.__poin

    def get_level(self) -> str:
        if self.__poin >= 1000:
            return "Komuter Sultan"
        elif self.__poin >= 300:
            return "Komuter Andalan"
        return "Komuter Pemula"

    def tambah_poin(self, jumlah: int) -> None:
        if jumlah > 0:
            self.__poin += jumlah

    def kurangi_poin(self, jumlah: int) -> bool:
        if jumlah <= 0 or self.__poin < jumlah:
            return False
        self.__poin -= jumlah
        return True

    def tautkan_kmt(self, nomor_kartu: str, saldo_awal: int = 20000) -> None:
        self.kmt = KartuMultiTrip(nomor_kartu, saldo_awal)

    def beli_tiket(self, asal: str, tujuan: str, daftar_moda: list, total_tarif: int, poin_reward: int, metode: str = "EMONEY"):
        berhasil_bayar = False
        if metode == "EMONEY":
            berhasil_bayar = self.dompet.bayar(total_tarif)
        elif metode == "KMT" and self.kmt is not None:
            berhasil_bayar = self.kmt.tap_bayar(total_tarif)

        if not berhasil_bayar:
            return None

        tiket_baru = TiketPerjalanan(asal, tujuan, daftar_moda, total_tarif, poin_reward)
        self.riwayat_tiket.append(tiket_baru)
        self.tambah_poin(poin_reward)
        return tiket_baru


# Blok uji coba mandiri (hanya jalan jika file ini di-run langsung)
if __name__ == "__main__":
    user = AkunKomuter("U01", "Budi", saldo_awal=50000)
    tiket = user.beli_tiket("Blok M", "Sudirman", ["MRT", "Jalan Kaki"], 6000, 50, metode="EMONEY")
    print("Tiket berhasil:", tiket)
    print("Sisa saldo E-Money:", user.dompet.get_saldo())
    print("Poin & Level sekarang:", user.get_poin(), "-", user.get_level())