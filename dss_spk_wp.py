import streamlit as st

st.write("""
##COBA APP
Hello *World!*
""")

import requests
import json
import re
from IPython.display import Javascript

"""dict dict = dictionary of dictionary {key:{key:value},key:{key:value}}

dict list = list of dictionary [{key:value},{key:value}]
"""

# Response request URL jadi dict list
def fetchJson(url):
  print(url)
  response =requests.get(url)
  data = response.json()
  print(data)
  return data

# Ambil data dari API website
sakit = fetchJson('https://opendata.sumedangkab.go.id/index.php/api/61d3b33557f40')
tenaga_kesehatan = fetchJson('https://opendata.sumedangkab.go.id/index.php/api/614409705448f')
sarana_kesehatan = fetchJson('https://opendata.sumedangkab.go.id/index.php/api/6143fd7241848')
penduduk = fetchJson('https://opendata.sumedangkab.go.id/index.php/api/61493671239d6')
luas = fetchJson('https://opendata.sumedangkab.go.id/index.php/api/6149308d7471e')

# Ini fungsi-fungsi untuk ngumpulin data

# Ambil values dari keys yang dipilih dalem dict
def getDictValues(row,keys,is_keys_exception=False):
  return [v for k,v in row.items() if (k in keys) != is_keys_exception]

# Sum semua string angka dalam list
def sumString(values:str):
  total=0
  for maybe_number in values:
    # print(maybe_number)
    try:
      total += int(maybe_number)
    except:
      total += float(maybe_number.replace(',','.'))
  return total

# {key_id:{+output_key:func(column_values)}} tambah pair ke dict dalem dict dari dict list diproses oleh func
def ScrapColumnsFromList(output_dict,input_list,output_key,id_key,func,column_keys,is_column_keys_exception=False):
  for row in input_list:
    target_dict = output_dict[formatKey(row[id_key])]
    value = func(getDictValues(row,column_keys,is_column_keys_exception))
    if output_key in target_dict:
      target_dict[output_key] += value
    else:
      target_dict[output_key] = value

# {key:{+output_key:func(column_values)}} tambah pair ke dict dalem dict dari dict dict diproses oleh func
def ScrapColumnsFromDict(output_dict,input_dict,output_key,func,column_keys,is_column_keys_exception=False):
  for k,v in input_dict.items():
    target_dict = output_dict[formatKey(k)]
    value = func(getDictValues(v,column_keys,is_column_keys_exception))
    if output_key in target_dict:
      target_dict[output_key] += value
    else:
      target_dict[output_key] = value

# {key:{-key:value}} remove key dari dict dict
def removeKey(target:dict,key):
  for k,v in target.items():
    v.pop(key)

# "[010] Sumedang Utara" --> "SUMEDANG UTARA"
def formatKey(input):
  return re.sub('[^a-zA-Z ]+', '', input).rstrip().lstrip().upper()

# Buat dict dict awal
alts = {formatKey(alt['1']):{} for alt in sakit[1:-1]}
print(alts)

# Masukkan data-data yang dibutuhkan ke dictionary awal 
ScrapColumnsFromList(alts,sakit[1:-1],'sakit','1',sumString,['4','5','6','7','8','9','10'])
ScrapColumnsFromList(alts,tenaga_kesehatan[1:-1],'tenaga kesehatan','2',sumString,['1','2'],True)
ScrapColumnsFromList(alts,sarana_kesehatan[1:-1],'sarana kesehatan','2',sumString,['1','2'],True)
ScrapColumnsFromList(alts,penduduk[1:-1],'jumlah penduduk','1',sumString,['4'])
ScrapColumnsFromList(alts,luas[1:-1],'luas','1',sumString,['3'])

ScrapColumnsFromDict(alts,alts,'persentase sakit',lambda x : x[0]/x[1]*100,['sakit','jumlah penduduk'])
ScrapColumnsFromDict(alts,alts,'persentase tenaga kesehatan',lambda x : x[0]/x[1]*100,['tenaga kesehatan','jumlah penduduk'])
ScrapColumnsFromDict(alts,alts,'sarana kesehatan per km',lambda x : x[0]/x[1],['sarana kesehatan','luas'])

ScrapColumnsFromList(alts,penduduk[1:-1],'kepadatan penduduk','1',sumString,['7'])

# alts_lengkap = alts.copy()

# Remove columns yang sudah tidak terpakai
removeKey(alts,'sakit')
removeKey(alts,'tenaga kesehatan')
removeKey(alts,'jumlah penduduk')
removeKey(alts,'sarana kesehatan')
removeKey(alts,'luas')

# Jadiin JSON
alt_json = json.dumps(alts,indent=2)
alt_json

# Buat yang bentuknya sama kyk di website Sumedan
def dictDictToDictList(input:dict,key):
  output = []
  for k,v in input.items():
    row = {key:k}
    row.update(v)
    output.append(row)
  return output

alt_json = json.dumps(dictDictToDictList(alts,'kecamatan'),indent=2)
alt_json

# Ini fungsi WP
def makeTableFromDictList(input:list,column_keys,is_column_keys_exception=False):
  alt_table = []
  for alt in input:
    alt_table.append(getDictValues(alt,column_keys,is_column_keys_exception))
  return alt_table

def normalisasi(weight_list,func = lambda x:x):
  weight_total = 0
  normalised_list = []
  for weight in weight_list:
    weight_total += func(weight)
  for weight in weight_list:
    normalised_list.append(weight/weight_total)
  return normalised_list

def buatVektorS(alt_table,weight_list):
  s = []
  for i in range(0,len(alt_table)):
    si = 1
    alt = alt_table[i]
    for j in range(0,len(alt)):
      try:
        criteria = int(alt[j])
      except:
        criteria = float(alt[j])
      if criteria == 0:
        criteria = 1
      weight = weight_list[j]
      try:
        si *= pow(criteria,weight)
      except:
        si *= criteria
    s.append(si)
  return s

def addPairsToDictListFromList(input:list,key,values:list):
  for i in range(0,len(input)):
    row = input[i]
    row.update({key:values[i]})

def wp(alternatives:list,weight_list,criterias,is_criterias_exception=False):
  output = []
  for alt in alternatives:
    output.append(alt.copy())

  alt_table = makeTableFromDictList(alternatives,criterias,is_criterias_exception)
  weight_list = normalisasi(weight_list,abs)
  s = buatVektorS(alt_table,weight_list)
  v = normalisasi(s)
  addPairsToDictListFromList(output,'V',v)
  output.sort(key=lambda x:x['V'],reverse=True)
  return output

# Jalanin WP nya
weight_list = [1,-1,-1,1]
excepted_columns = ['kecamatan']
alts = json.loads(alt_json)

hasil_akhir = wp(alts,weight_list,excepted_columns,True)

# Jadiin JSON
hasil_akhir_JSON = json.dumps(hasil_akhir,indent=2)
hasil_akhir_JSON

# Jalanin WP nya
weight_list = [1,-1,-1,1]
excepted_columns = ['kecamatan']
alts = json.loads(alt_json)

hasil_akhir = wp(alts,weight_list,excepted_columns,True)

# Jadiin JSON
hasil_akhir_JSON = json.dumps(hasil_akhir,indent=2)
hasil_akhir_JSON

# Jalanin WP nya (test untuk dataset lain)
weight_list = [1,3,5]
columns = ['4','5','6']
alts = sakit[1:-1]

hasil_akhir = wp(alts,weight_list,columns)

# Jadiin JSON
hasil_akhir_JSON = json.dumps(hasil_akhir,indent=2)
hasil_akhir_JSON
