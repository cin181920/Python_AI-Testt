def replace_characters(teks, kamus_pengganti):
    hasil_teks = ""
    for huruf in teks: 
        if huruf in kamus_pengganti: 
            hasil_teks+=kamus_pengganti[huruf]
        else: 
            hasil_teks+=huruf
     
    return hasil_teks

input_string = "hello world"
input_dic = {'h': 'j', 'e': 'i', 'l': 'm'}
print(replace_characters(input_string,input_dic))


def first_unique_char(s):
    hitung_huruf={}
    for huruf in s : 
        if huruf in hitung_huruf: 
            hitung_huruf[huruf] +=1
        else : 
            hitung_huruf[huruf]=1
    for i in range (len(s)):
        if hitung_huruf[s[i]]==1:
            return i
    return -1

input_s = first_unique_char("aabb")
print(input_s)
      


def topFrequent(nums,k):
    hitung={}

    for num in nums:
        if num in hitung:  
            hitung[num]+=1
        else: 
            hitung[num]=1

    frekuensi_list =[]
    
    for angka, jumlah in hitung.items():
        frekuensi_list.append([jumlah,angka])

    frekuensi_list.sort(reverse=True)
    hasil=[]
    
    for i in range(k):
        hasil.append(frekuensi_list[i][1])
        
    return hasil

nums = [1,1,1,2,2,3]
k = 2

print(topFrequent(nums,k))