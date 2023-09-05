import telebot, fitz, pathlib
from telebot import types

bot = telebot.TeleBot('6540706711:AAEi-tQ8n-ZA7_Gbz-7H3X8o8nNqfn9ZBlE')

@bot.message_handler(commands=['tk_timetable'])
def step_one(m):
    # bot.send_message(m.chat.id, "Расписание какой группы необходимо узнать?")
    bot.reply_to(m, "Расписание какой группы необходимо узнать?")
    bot.register_next_step_handler(m, get_site_and_rasp)

def get_site_and_rasp(m):
    try:
        import requests, urllib, re, fitz, pathlib
        from bs4 import BeautifulSoup
        cid = m.chat.id

        # отправляем GET-запрос на сайт
        response = requests.get('https://narfu.ru/ltk/obrazovatelnaya/raspisanie/')

        # парсим HTML-код страницы с помощью BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Находим все ссылки на странице, содержащие слово "example"
        links = soup.find_all('a', {'title': re.compile('группы')})

        # Выбираем вторую ссылку из списка
        chosen_link = links[1].get('href') #ИЗМЕНЕНО

        # Выводим найденные ссылки
        for link in links:
            link.get('href')
        chosen_link = 'https://narfu.ru' + chosen_link

        filename = 'расписание.pdf'  # имя файла, под которым его нужно сохранить

        # Скачиваем файл и сохраняем его на устройстве
        urllib.request.urlretrieve(chosen_link, filename)

        doc = fitz.open('расписание.pdf')

        search_text = m.text

        for page_num, page in enumerate(doc):
            text_instances = page.search_for(search_text)
            if len(text_instances) > 0:
                need_page = page_num

        src = fitz.open('расписание.pdf')
        doc = fitz.open()

        num_pages = src.page_count

        last_page = num_pages - 1 
        width, height = fitz.paper_size("a4")
        r = fitz.Rect(0, 0, width, height)
        r1 = r * 0.5
        r3 = r1 + (0, r1.height*0.438, 0, r1.height*0.438)
        r_tab = [r1,r3]
        page = doc.new_page(width=width*0.5, height=height)
        page1 = doc[0]
        page1.number = last_page

        if need_page == last_page: 
            last_page_bool = True
            page.show_pdf_page(r_tab[0], src, need_page) 
        else:
            last_page_bool = False
            page.show_pdf_page(r_tab[0], src, need_page)
            page.show_pdf_page(r_tab[1], src, need_page+1)

        file_rez = "searching_" + search_text + ".pdf"
        doc.save(file_rez, garbage=4, deflate=True)
        doc.close()
        src.close()

        file_name = file_rez
        doc = fitz.open(file_name)
        page = doc[0]

        text_top = page.search_for(search_text)

        rect1 = fitz.Rect(0, 0, 297, text_top[0].y0-50)
        annot = page.add_redact_annot(rect1)
        page.apply_redactions()

        file_non_top = "crop_searching_" + search_text + ".pdf"
        doc.save(file_non_top, garbage=4, deflate=True, clean=True)
        doc.close()

        file_name = file_non_top
        doc = fitz.open(file_name)

        for page in doc:
            text_found = page.search_for(search_text)
            if text_found:
                match0 = text_found[0]
                for i in match0:
                    y0 = match0[1]

        if last_page_bool == False:
            sear_text = 'РАСПИСАНИЕ'
            for page in doc:
                text_found = page.search_for(sear_text)
                if text_found:
                    match1 = text_found[1]
                    for i in match1:   
                        y02 = match1[1]
        else:
            y02 = 310

        mat = fitz.Matrix(300 / 72, 300 / 72)
        clip = fitz.Rect(0, y0, 841, y02)
        pix = page.get_pixmap(matrix=mat, clip=clip)

        img_name = 'page_' + search_text + '.png'

        pix.save(img_name)
        bot.send_photo(cid, open(img_name, 'rb'))
        pix = None

        doc.close()

        file_img = pathlib.Path(file_non_top)
        file_img.unlink()

        file_doc = pathlib.Path(file_rez)
        file_doc.unlink()
            
        file_img = pathlib.Path(img_name)
        file_img.unlink()
    except Exception as e:
        bot.reply_to(m, ' ~_~ Ошибка! Проверьте номер группы +_+')
        print(e)

print('ПОЛНОСТЬЮ ГОТОВ К РАБОТЕ')

bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть
bot.idle()