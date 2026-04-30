import pandas as pd, time, re, glob, getpass, platform, telebot
from sqlalchemy import create_engine
from datetime import datetime
from tqdm import tqdm

#Паттерны
engine = create_engine("mysql+pymysql://"ВАШ ЛОГИН":"ВАШ ПАРОЛЬ"@172.16.10.63/marketing")                                       # Коннектор SQL
date = datetime.now().strftime('%d.%m %H:%M:%S')                                                                         # Текущая дата
bot = telebot.TeleBot("6116617842:AAHrJDfbe2NqfxI1rWWIoxUsGTTfKTNCk_E")                                                  # Токен telegram бота
re_1 = r'[^0-9,.;/]'                                                                                                     # Регулярное выражение для отсева букв, пробелов
re_2 = r'[^0-9]'                                                                                                         # Регулярное выражение для отсева знаков

def SendTelegram(status):
	# Получение информации о компьютере
	UserName = getpass.getuser()                                                                                         # Имя пользователя (обычно оно User - не информативно)
	CompName = platform.node()                                                                                           # Имя компьютера
	chat_id = '5249664773'                                                                                               # ID моей телеги
	if status == "try": # Если связь с телегой установлена
		bot.send_message(chat_id, date+" пользователь "+UserName+" ("+CompName+") успешно воспользовался скриптом для подсчёта коммуникаций") #Отправка сообщения
	elif status == "except1": # Если нет подключения к SQL серверу
		bot.send_message(chat_id, "ERROR: " + date+" пользователь "+UserName+" ("+CompName+") неудачно запустил скрипт для подсчёта коммуникаций - не подключил VPN") #Отправка сообщения
	elif status == "except2": # Если нет подключения к SQL серверу
		bot.send_message(chat_id, "ERROR: " + date+" пользователь "+UserName+" ("+CompName+") неудачно запустил скрипт для подсчёта коммуникаций - либо не закрыл файл, либо в файле нет подходящих колонок") #Отправка сообщения

def CollectData(FileLocation):                                                                                           # Чтение одного или нескольких excel фалов .xlsx
	GroupFile = [item for item in glob.glob(FileLocation)]                                                               # Собираем файлы в список
	itter = 0                                                                                                            # Переменная для подсчёта удачных повторений скрипта
	for Filename in tqdm(GroupFile): # Вводные для progress bar
		if not 'Результат валидации' in str(Filename):
			print(Filename, "Началась загрузка excel файла: ", datetime.time(datetime.now()))
			try:
				File = pd.read_excel(Filename, usecols=['Номер телефона', 'Дата начала', 'Дата конца'])                  # Чтение excel-файла
				dfEX = pd.DataFrame(File)                                                                                # Формирование dataframe
				#Обработка фрейма данных
				dfEX['Дата начала'] = pd.to_datetime(dfEX['Дата начала'], dayfirst=True)                                 # Преобразование столбца дат в даты SQL формата
				dfEX['Дата конца'] = pd.to_datetime(dfEX['Дата конца'], dayfirst=True)                                   # Преобразование столбца дат в даты SQL формата
				dfEX['Номер телефона'].astype('str')                                                                     # Преобразование столбца с номерами телефонов в строчный формат
				dfEX['Номер телефона'] = dfEX['Номер телефона'].apply(lambda x: max(re.sub(re_2, ',', re.sub(re_1, '', str(x))).lstrip(',').split(',', 10), key=len)[-10:])
				dfEX['Номер телефона'] = dfEX['Номер телефона'].loc[dfEX['Номер телефона'].str.len().between(10, 11)]    # Выбор номера телефона определённого формата
				dfEX = dfEX.groupby(pd.Grouper(key='Номер телефона')).min().reset_index()                                # Группировка с удалением дубликатов и выбором наименьшей даты
				# Создание списков для итерирования
				list_of_numbers = list(filter(None, dfEX['Номер телефона'].tolist()))                                    # Получение списка из номеров телефонов в excel файле
				list_of_date_start = list(filter(None, dfEX['Дата начала'].tolist()))                                    # Получение списка из номеров дат начала в excel файле
				list_of_date_finish = list(filter(None, dfEX['Дата конца'].tolist()))                                    # Получение списка из дат окончания в excel файле
				first_date = min(list_of_date_start); end_date = max(list_of_date_finish)                                # Присвоение нижней и верхней границы из списка (для обрезки базы)
				print("Созданы списки для проверки по файлу " + FileLocation + " . Теперь начнём считать...")
				# Анализ по базе westcall
				dfSQLwestcallNew = dfSQLwestcall.loc[((dfSQLwestcall['Дата звонка'] >= first_date) & (dfSQLwestcall['Дата звонка'] <= end_date))] # Обрезка базы по датам
				dfSQLwestcallNew = dfSQLwestcallNew.loc[(dfSQLwestcallNew['Телефон'].str.contains('|'.join(list(filter(None, list_of_numbers))), na=False))] # Обрезка базы по номерам телефонов в файле
				print("В базе westcall " + str(len(dfSQLwestcallNew['Телефон'])) + " подходящих записей по номерам телефонов")
				dfSQLwestcallTT = dfSQLwestcallNew.groupby('Принадлежность').agg({'Телефон': ['count']}).reset_index()   # Группировка по принадлежности
				# Анализ по базе bitrix
				dfSQLbitrixNew = dfSQLbitrix.loc[((dfSQLbitrix['Дата создания'] >= first_date) & (dfSQLbitrix['Дата создания'] <= end_date))]          # Обрезка базы по датам
				dfSQLbitrixNew = dfSQLbitrixNew.loc[(dfSQLbitrixNew['Телефон'].str.contains('|'.join(list(filter(None, list_of_numbers))), na=False))] # Обрезка базы по номерам телефонов в файле
				print("В базе bitrix " + str(len(dfSQLbitrixNew['Телефон'])) + " подходящих записей по номерам телефонов")
				dfSQLbitrixTT = dfSQLbitrixNew.groupby('Тип источника').agg({'Телефон': ['count']}).reset_index()        # Группировка по типу источников
				try:
					with pd.ExcelWriter(Filename, engine='openpyxl', mode='a') as writer:                                # Дополнение excel файла новыми листами
						try:
							dfSQLwestcallNew.to_excel(writer, sheet_name='Коммуникации westcall', index=False)
							dfSQLbitrixNew.to_excel(writer, sheet_name='Коммуникации bitrix', index=False)
							dfSQLwestcallTT.to_excel(writer, sheet_name='Группировка по принадлежности')
							dfSQLbitrixTT.to_excel(writer, sheet_name='Группировка по типам источников')
							itter += 1
						except: pass
				except:	print("В файле" + Filename + " уже присутствуют листы с аналитикой :("); time.sleep(5)
			except Exception as e:
				print(f'Произошла ошибка: {e}'); print("Возможно у Вас открыт excel файл, который Вы пытаетесь валидировать или колонки названы неправильно"); time.sleep(5) #Обработка ошибки

	print("Все файлы обработаны")
	if itter > 0: SendTelegram("try")
	else: SendTelegram("except2")

#Получение данных из SQL
try:
	lightquery_1 = "SELECT * FROM westcall"                                                                              # SQL запрос в базу westcall
	lightquery_2 = "SELECT * FROM bitrix"                                                                                # SQL запрос в базу bitrix
	print("Начинается загрузка SQL базы westcall (может занять пару минут)..."); dfSQLwestcall = pd.read_sql(lightquery_1, engine); print("База westcall загружена") # Чтение MySQL westcall, получение dataframe
	print("Начинается загрузка SQL базы bitrix (может занять пару минут)..."); dfSQLbitrix = pd.read_sql(lightquery_2, engine); print("База bitrix загружена") # Чтение MySQL bitrix, получение dataframe
	print("Теперь возмусь за ваши файлы")
except Exception:
	print("Не могу подключится к SQL серверу. Проверьте подключение к VPN и перезапустите приложение")
	SendTelegram("except1")
	time.sleep(5); exit()

CollectData('*.xlsx')
