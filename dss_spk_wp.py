# Anggota Kelompok:

# *   Adnan Rafiyansyah Majid
# *   Amalia Nur Fitri
# *   Muhammad Zidan Khairan
# *   Rifqy Kurnia Sudarman

import streamlit as st
import pandas as pd
import requests
import json
import re

# dict list = list berisi dictionary = [{key:value},{key:value}]
# dict dict = dictionary berisi dictionary = {key:{key:value},key:{key:value}}
# list list = list berisi list = [[value,value],[value,value]]

# Response request URL berupa JSON jadi dict list
def loadData(url):
  response =requests.get(url)
  data = response.json()
  # ubah JSON list jadi dict list
  st.dataframe(data, use_container_width=True)
  return data

# Ini fungsi-fungsi untuk ngumpulin data

# Ambil values dari keys yang dipilih dalem dict
def getDictValuesByKeys(row,keys,is_keys_exception=False):
  # kalo keynya ada dalam keys, akan dimasukkan atau tidak tergantung is_keys_exception
  return [v for k,v in row.items() if (k in keys) != is_keys_exception]

# Sum semua string angka dalam list
def sumString(values:str):
  total=0
  for maybe_number in values:
    try:
      total += int(maybe_number)
    # Handle untuk jika isi string adalah desimal
    except:
      total += float(maybe_number.replace(',','.'))
    # Kalau isi string bukan angka return 0
  return total

# Tambah pair ke dict dict dari dict list dengan value yang telah diproses oleh func
# {id_key:{+(output_key:func(dict_value))}} 
def ScrapColumnsFromList(output_dict,input_list,output_key,id_key,func,column_keys,is_column_keys_exception=False):
  for row in input_list:
    # Dictionary output keynya di format
    target_dict = output_dict[formatKey(row[id_key])]
    dict_value = getDictValuesByKeys(row,column_keys,is_column_keys_exception)
    value = func(dict_value)
    if output_key in target_dict:
      target_dict[output_key] += value
    else:
      target_dict[output_key] = value

# Tambah pair ke dict dict dari dict dict dengan value yang telah diproses oleh func
# {id_key:{+(output_key:func(dict_value))}}
def ScrapColumnsFromDict(output_dict,input_dict,output_key,func,column_keys,is_column_keys_exception=False):
  for k,v in input_dict.items():
    # Dictionary output keynya di format
    target_dict = output_dict[formatKey(k)]
    dict_value = getDictValuesByKeys(v,column_keys,is_column_keys_exception)
    value = func(dict_value)
    if output_key in target_dict:
      target_dict[output_key] += value
    else:
      target_dict[output_key] = value

# {key:{-(target_key:value)},key:{-(target_key:value)}} remove pair dari dict dalam dict dict berdasarkan target_key
def removeKey(target:dict,target_key):
  for k,v in target.items():
    v.pop(target_key)

# "[010] Sumedang Utara" --> "SUMEDANG UTARA"
def formatKey(input):
  return re.sub('[^a-zA-Z ]+', '', input).rstrip().lstrip().upper()

# Buat yang bentuknya sama kyk di website Sumedang (JSON list, tipe data : dict list)
def dictDictToDictList(input:dict,key):
  output = []
  for k,v in input.items():
    row = {key:k}
    row.update(v)
    output.append(row)
  return output


#ini fungsi-fungsi dict list

# Ambil semua value dari semua kolom yang dipilih (dalam bentuk list yang telah diproses func) dari dict list ke list list
def getColumnsFromDictList(input:list,column_keys,is_column_keys_exception=False,func = lambda x:x):
  output = []
  for dict in input:
    output.append(func(getDictValuesByKeys(dict,column_keys,is_column_keys_exception)))
  return output

# Tambahkan pairs dengan key yang ditentukan dan value dari list ke dict list
# Values : [value1,value2] Target : [{+(key:value1)},{+(key:value2)}]
def addPairsToDictListFromList(target:list,key,values:list):
  for i in range(0,len(target)):
    dict = target[i]
    dict.update({key:values[i]})


# Ini fungsi-fungsi WP

# Return list berisi nilai-nilai input yang sudah dinormalisasi
def normalisasi(weight_list,func = lambda x:x):
  weight_total = 0
  normalised_list = []
  # Sum weight yang telah diproses oleh func
  for weight in weight_list:
    weight_total += func(weight)
  for weight in weight_list:
    normalised_list.append(weight/weight_total)
  return normalised_list

# Buat vektor S dari list list value criteria setiap alternatif dan list bobot
def buatVektorS(alt_table,weight_list):
  s = []
  for i in range(0,len(alt_table)):
    # si = nilai S sebuah alternatif
    si = 1.0
    # alt = list yang berisi nilai-nilai kriteria sebuah alternatif
    alt = alt_table[i]
    for j in range(0,len(alt)):
      try:
        criteria = int(alt[j])
      # Handling jika nilai kriteria desimal
      except:
        criteria = float(alt[j])
      # Handling jika nilai kriteria nol agar tidak ada pembagian oleh nol
      if criteria == 0:
        criteria = 1
      # weight = weight untuk sebuah kriteria
      weight = weight_list[j]
      try:
        si *= pow(criteria,weight)
      except:
        si *= criteria
    s.append(si)
  return s

def wp(alternatives:list,weight_list,criterias,is_criterias_exception=False):
  output = []

  # Deep copy dict list alternatives ke output
  for alt in alternatives:
    output.append(alt.copy())

  alt_table = getColumnsFromDictList(alternatives,criterias,is_criterias_exception)
  weight_list = normalisasi(weight_list,abs)
  s = buatVektorS(alt_table,weight_list)
  v = normalisasi(s)
  addPairsToDictListFromList(output,'V',v)
  output.sort(key=lambda x:x['V'],reverse=True)
  return output


st.header('Meningkatkan pelayanan kesehatan berdasarkan jumlah penderita penyakit di daerah yang membutuhkan di Sumedang')
st.subheader('Source Code  https://github.com/amalianurf/DSS_SPK_Sumedang')
tab1, tab2 = st.tabs(["Data Per Kecamatan", "Perhitungan"])

with tab1:
  # Ambil data dari API website
  st.subheader('Data Penderita Penyakit')
  sakit = loadData('https://opendata.sumedangkab.go.id/index.php/api/61d3b33557f40')
  st.subheader('Data Tenaga Kesehatan')
  tenaga_kesehatan = loadData('https://opendata.sumedangkab.go.id/index.php/api/614409705448f')
  st.subheader('Data Sarana Kesehatan')
  sarana_kesehatan = loadData('https://opendata.sumedangkab.go.id/index.php/api/6143fd7241848')
  st.subheader('Data Jumlah Penduduk')
  penduduk = loadData('https://opendata.sumedangkab.go.id/index.php/api/61493671239d6')
  st.subheader('Data Luas Daerah')
  luas = loadData('https://opendata.sumedangkab.go.id/index.php/api/6149308d7471e')

  # Buat dict dict awal
  alts = {formatKey(alt['1']):{} for alt in sakit[1:-1]}

  # Masukkan data-data yang dibutuhkan ke dictionary awal
  ScrapColumnsFromList(alts,sakit[1:-1],'sakit','1',sumString,['4','5','6','7','8','9','10'])
  ScrapColumnsFromList(alts,tenaga_kesehatan[1:-1],'tenaga kesehatan','2',sumString,['1','2'],True)
  ScrapColumnsFromList(alts,sarana_kesehatan[1:-1],'sarana kesehatan','2',sumString,['1','2'],True)
  ScrapColumnsFromList(alts,penduduk[1:-1],'jumlah penduduk','1',sumString,['4'])
  ScrapColumnsFromList(alts,luas[1:-1],'luas','1',sumString,['3'])

  ScrapColumnsFromDict(alts,alts,'persentase sakit',lambda x : x[0]/x[1]*100,['sakit','jumlah penduduk']),
  ScrapColumnsFromDict(alts,alts,'persentase tenaga kesehatan',lambda x : x[0]/x[1]*100,['tenaga kesehatan','jumlah penduduk']),
  ScrapColumnsFromDict(alts,alts,'sarana kesehatan per km',lambda x : x[0]/x[1],['sarana kesehatan','luas']),
  ScrapColumnsFromList(alts,penduduk[1:-1],'kepadatan penduduk','1',sumString,['7'])
  

  st.subheader('Data yang dikumpulkan')
  st.dataframe(dictDictToDictList(alts,'kecamatan'), use_container_width=True)

  # Remove columns yang sudah tidak terpakai
  removeKey(alts,'sakit')
  removeKey(alts,'tenaga kesehatan')
  removeKey(alts,'jumlah penduduk')
  removeKey(alts,'sarana kesehatan')
  removeKey(alts,'luas')
  
  # ubah jadi bentuk seperti di web sumedang
  alts = dictDictToDictList(alts,'kecamatan')
  

  st.subheader('Data yang digunakan')
  st.dataframe(alts, use_container_width=True)

with tab2:
  alt_json = json.dumps(alts,indent=2)
  c1 = st.number_input('Bobot Persentase Orang yang Sakit',value=3,min_value=0)
  c2 = st.number_input('Bobot Persentase Tenaga Kesehatan',value=3,min_value=0)
  c3 = st.number_input('Bobot Sarana Kesehatan per Km2',value=2,min_value=0)
  c4 = st.number_input('Bobot Kepadatan Penduduk',value=1,min_value=0)
  if st.button('Hitung'):
    weight_list = [c1,c2*-1,c3*-1,c4]
    excepted_columns = ['kecamatan']
    alts = json.loads(alt_json)

    hasil_akhir = wp(alts,weight_list,excepted_columns,True)
    st.subheader('Hasil Akhir')
    st.dataframe(hasil_akhir, use_container_width=True)
    dt = pd.DataFrame(hasil_akhir,index=getColumnsFromDictList(hasil_akhir,['kecamatan'],func = lambda x:x[0]),columns=['V'])
    dt.sort_values(by=['V'],ascending=True)
    st.bar_chart(dt,width=1,)