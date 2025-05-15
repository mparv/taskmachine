import asyncio
import uuid
import datetime

from mem_db.in_mem_db import CouchDriver
from new_scraper.scraper import extract_data


class Worker(object):
    def __init__(self, cooldown_period=120, url_list=None):
        self.cooldown_period = cooldown_period
        self.url_list = url_list
        self.running = False
        self.curr_indx = 0
        self.cd = CouchDriver()

    async def execute(self):
        self.running = True

        while self.running and self.curr_indx < len(url_list):
            print(f"Processing {self.curr_indx}")
            url = url_list[self.curr_indx]
            self.curr_indx += 1

            heading = ['h1']
            content = ['p']
            headings, contents = await extract_data(url, heading, content)
            headings = ' '.join(headings)
            contents = ' '.join(contents)

            doc = {
                '_id': f"p1:{str(uuid.uuid4())}",
                "title": headings,
                "content": contents,
                "liked": 0,
                "viewed": 0,
                "created_on": str(datetime.datetime.now())
            }
            await self.cd.create("article", doc)

            print(f"Sleeping for {self.cooldown_period}")
            await asyncio.sleep(self.cooldown_period)

url_list = [
]

worker = Worker(url_list=url_list)
asyncio.run(worker.execute())