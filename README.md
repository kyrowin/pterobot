# Бот для управления вашими серверами в панеле Pterodactyl

<b>1. Загрузка проекта и установка библиотек</b>
1. Скачиваете проект  
  1.1 Если у вас Windows:
   Скачиваете [python](https://www.python.org/downloads/), открываете, <b>в начале установки обязательно нажмите "Add to path"</b>  
   После установки заходите на мой репозиторий  
   Нажимаете CODE, далее Download ZIP.  
   Распоковываете, приступаете к пункту 2.
   <details>
   <summary>Фото</summary>

   ![image](https://github.com/user-attachments/assets/5461b229-ae18-4533-b6c8-d73100196f9a)

   </details>
   1.2 Если у вас Ubuntu(Линуксо-подобные):

   ```
   sudo apt install python3
   sudo apt install python3-pip
   sudo apt install git
   git clone https://github.com/kyrowin/pterobot
   cd pterobot
   ```
2. Установка библиотек
(Действия должны происходить в папке с проектом)   
  2.1.1 Если у вас Windows:
   Нажимаете сочетание клавиш WIN+R  
   Пишите в окно которое открылось: <b>cmd</b>
  2.1

   ```
   pip install -r requirements.txt
   ```
3. Первый запуск и настройка

   Заполните .env.example вашими данными и переименуйте его в .env
   ```
   BOT_TOKEN - Ваш токен бота Telegram
   PTERODACTYL_URL - Ссылка на сайт панели (включая https://)
   PTERODACTYL_API_KEY - API Ключ который вы получили в панели
   ```

   ```
   python pterobot.py
   ```
   
   - Где брать API ключ?
   Заходите в панель, на главной странице кликаете на свою аватарку.
     <details>
     <summary>Фото</summary>
  
     ![image](https://github.com/user-attachments/assets/9ad2e272-9b13-4b6a-ae4f-dfe845ea5b0b)
  
     </details>
  
     Пишите описание к ключу (чтобы не запутатся можно написать: <b>pterobot</b>)
        <details>
     <summary>Фото</summary>
  
     ![image](https://github.com/user-attachments/assets/3d29e99d-27d3-46de-bef3-e97caf20c251)
  
  
     </details>
  
     Ключ который вам покажут и будет тот самый API ключ.
