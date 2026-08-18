# ==========================================
# 1. Fungsi Mengganti Karakter (Replace Characters)
# ==========================================
def replace_characters(teks, kamus_pengganti):
    """
    Fungsi ini mengganti setiap huruf dalam 'teks' berdasarkan aturan di 'kamus_pengganti'.
    Jika huruf ada di kamus, maka akan diganti. Jika tidak, huruf tetap sama.
    """
    hasil_teks = "" # Variabel untuk menyimpan teks hasil
    for huruf in teks: # Looping (perulangan) setiap huruf di dalam teks
        if huruf in kamus_pengganti: # Cek apakah huruf ada di dalam dictionary kamus_pengganti
            hasil_teks += kamus_pengganti[huruf] # Jika ada, tambahkan huruf penggantinya
        else: 
            hasil_teks += huruf # Jika tidak ada, tambahkan huruf aslinya
     
    return hasil_teks # Mengembalikan teks yang sudah diproses

# Contoh Penggunaan:
input_string = "hello world"
input_dic = {'h': 'j', 'e': 'i', 'l': 'm'}
# Output diharapkan: "jimmo wormd" (h->j, e->i, l->m)
print(replace_characters(input_string, input_dic))


# ==========================================
# 2. Fungsi Mencari Karakter Unik Pertama (First Unique Character)
# ==========================================
def first_unique_char(s):
    """
    Fungsi ini mencari huruf pertama dalam string yang tidak memiliki duplikat (hanya muncul 1 kali).
    Mengembalikan indeks (posisi) huruf tersebut, atau -1 jika semua huruf memiliki duplikat.
    """
    hitung_huruf = {} # Dictionary untuk menghitung frekuensi kemunculan tiap huruf
    
    # Langkah 1: Menghitung jumlah kemunculan setiap huruf
    for huruf in s: 
        if huruf in hitung_huruf: 
            hitung_huruf[huruf] += 1 # Jika huruf sudah ada, tambah jumlahnya
        else: 
            hitung_huruf[huruf] = 1 # Jika belum ada, set jumlahnya jadi 1
            
    # Langkah 2: Mencari huruf pertama yang jumlah kemunculannya persis 1
    for i in range(len(s)):
        if hitung_huruf[s[i]] == 1:
            return i # Mengembalikan indeks huruf tersebut
            
    return -1 # Mengembalikan -1 jika tidak ada karakter yang unik

# Contoh Penggunaan:
input_s = first_unique_char("aabb")
# Output diharapkan: -1 (karena 'a' dan 'b' muncul lebih dari sekali)
print(input_s)
      

# ==========================================
# 3. Fungsi Mencari Elemen Paling Sering Muncul (Top K Frequent Elements)
# ==========================================
def topFrequent(nums, k):
    """
    Fungsi ini mencari 'k' buah angka yang paling sering muncul di dalam list 'nums'.
    """
    hitung = {} # Dictionary untuk menyimpan frekuensi kemunculan angka

    # Langkah 1: Menghitung frekuensi setiap angka
    for num in nums:
        if num in hitung:  
            hitung[num] += 1
        else: 
            hitung[num] = 1

    frekuensi_list = []
    
    # Langkah 2: Memindahkan data dari dictionary ke list of list dengan format [jumlah, angka]
    for angka, jumlah in hitung.items():
        frekuensi_list.append([jumlah, angka])

    # Langkah 3: Mengurutkan list secara menurun (descending) berdasarkan jumlah terbanyak
    frekuensi_list.sort(reverse=True)
    
    hasil = []
    
    # Langkah 4: Mengambil 'k' angka teratas (yang paling sering muncul)
    for i in range(k):
        hasil.append(frekuensi_list[i][1]) # Mengambil angkanya saja
        
    return hasil # Mengembalikan list angka terbanyak

# Contoh Penggunaan:
nums = [1, 1, 1, 2, 2, 3]
k = 2
# Output diharapkan: [1, 2] (karena 1 muncul 3x, dan 2 muncul 2x)
print(topFrequent(nums, k))