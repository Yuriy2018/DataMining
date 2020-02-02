import shutil
import PyPDF2
from PIL import Image
import pytesseract
import time
import os

from pymongo import MongoClient

mongo_client = MongoClient()

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

pdf_file_path = 'data_for_parse/4696_4.pdf'

# todo отсортировать файлы jpg и pdf



# todo Извлеч jpg из pdf  и сохранить в папке изображений
def extract_pdf_image(pdf_file_path):

    result = []

    for page_num in range(0, pdf_file.getNumPages()):
        page = pdf_file.getPage(page_num)
        page_obj = page['/Resources']['/XObject'].getObject()

        Im = str(page_obj)[2:6]

        if page_obj[Im].get('/Subtype') == '/Image':
            size = (page_obj[Im]['/Width'], page_obj[Im]['/Height'])
            data = page_obj[Im]._data
            if page_obj[Im]['/ColorSpace'] == '/DeviceRGB':
                mode = 'RGB'
            else:
                mode = 'P'

            if page_obj[Im]['/Filter'] == '/FlateDecode':
                file_type = 'png'
            elif page_obj[Im]['/Filter'] == '/DCTDecode':
                file_type = 'jpg'
            elif page_obj[Im]['/Filter'] == '/JPXDecode':
                file_type = 'jp2'
            else:
                file_type = 'bmp'

            result_strict = {
              'page': page_num,
              'size': size,
              'data': data,
              'mode': mode,
              'file_type': file_type,
            }
            result.append(result_strict)
    return result



def save_pdf_image(file_name,f_path,*pdf_strich):

        result = {} # Полученные номера будем собирать в словарь, ключ это будет номерСтраницы, значение - сам номер.
        for item in pdf_strich[0]:
            name = f"{file_name}_#_{item['page']}.{item['file_type']}"
            fullnameImg = f"{f_path}/{name}"
            with open(fullnameImg, 'wb') as image:
                image.write(item['data'])

            number = extract_number(fullnameImg)  # сразу с полученного файла jpeg пытаемся получить номер
            if number != None:
                nPage = str(item['page'])
                result[nPage] = number
        return result


# todo Извлеч номер кассы из поля

def extract_number(file_path):
    img_obj = Image.open(file_path)
    text = pytesseract.image_to_string(img_obj, 'rus')
    pattern = 'заводской (серийный) номер'
    pattern2 = 'заводской номер'
    # result = {}
    for idx, line in enumerate(text.split('\n')):
        if line.lower().find(pattern) + 1 or line.lower().find(pattern2) + 1:
            eng_text = pytesseract.image_to_string(img_obj, 'eng')
            number = eng_text.split('\n')[idx].rstrip('}').rstrip('|').rstrip(';').rstrip('"').rstrip('—').rstrip('_').rstrip(' ').split(' ')[-1] # Удаляем все возможные знаки препинания, чтобы последним элементом[-1] получать номер.
            return number.rstrip(' ')
            # print(1)
        # print(1)
    # todo при отсутствии распознования вернуть соответствиуещее сообщить или error
    # return result




# todo сохранить все в БД MONGO



def SaveDB(full_path,listNumbers,status):

    item = {'full fath': full_path,
            'status': status,
            'numbers': listNumbers,
            }

    database = mongo_client['parse_PDF']
    collection = database['PDF_number']
    collection.insert_one(item)


directory = r'C:\Users\Yuriy\PycharmProjects\Python_GB\DataMining\readPDF\data_for_parse\СКД_Поверка весов'
Images_path = r'C:\Users\Yuriy\PycharmProjects\Python_GB\DataMining\readPDF\data_for_parse\Images'
if __name__== '__main__':

    for root, dirs, files in os.walk(directory): # Считываем содержимое основной папки
        for file in files:
            fullName = root + '\\' + file # Получаем полное имя до файла
            ext = file.split('.')[-1]

            if ext == 'pdf':

                try:  # Попытаемся обработать pdf файл
                    pdf_result = extract_pdf_image(fullName)
                except:
                    SaveDB(fullName,None,'fail') # если не получитиься, то запишим как неудача.

                name = file.split('.')[0] # олучаем имя файла
                listNumbers = save_pdf_image(name,Images_path,pdf_result)
                SaveDB(fullName,listNumbers,'success')


            elif ext == 'jpg':

                Number = extract_number(fullName)
                listNumbers = {'0': Number}
                SaveDB(fullName, listNumbers,'success')

            else:
                print(ext)



