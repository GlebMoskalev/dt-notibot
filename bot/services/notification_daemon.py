import asyncio
from aiogram import Bot
from .postgresql import DataBase
from datetime import datetime, timedelta
from bot.messages import allert_message


class NotificationDaemon:
    def __init__(self, bot: Bot, db: DataBase):
        self.bot = bot
        self.db = db
        self.check_period = 60
    
    async def run(self):
        while True:
            try:
                print('Start notificated process')

                notificated_events = await self.db.get_notificated_events()
                all_events, total_count = await self.db.get_events_paginated(limit=1e6)
                if total_count != len(all_events):
                    print('НИЧЕГО СЕБЕ КАК МНОГО СОБЫТИЙ: ' + total_count)
                
                all_events = [event['id'] for event in all_events
                              if event['id'] not in notificated_events and
                              (datetime.now() <= event['start_time']) and
                              (event['start_time'] <= (datetime.now() + timedelta(minutes=15)))]

                print(f'Найдено {len(all_events)} подходящих событий')

                chat_ids = await self.db.get_users_by_favorite_events(all_events)
                print(f'События будут отправлены {len(chat_ids)} пользователям')

                for chat_id in chat_ids:
                    try:
                        await self.bot.send_message(chat_id, allert_message(15))
                    except Exception as error:
                        print(f'Не смогли отправить сообщение в чат {chat_id}, ошибка: {error}')
                
                for event in all_events:
                    await self.db.add_notificated_event(event)
            except Exception as error:
                print(f'Something went wrong in notificaton daemon work: {error}')
            finally:
                print(f'Сейчас время {datetime.now().strftime('%d/%m/%Y, %H:%M')}, новая проверка будет выполнена через {self.check_period} секунд')
                await asyncio.sleep(self.check_period)