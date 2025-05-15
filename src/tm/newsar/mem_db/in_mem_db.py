import httpx
import asyncio


class CouchDriver(object):
    def __init__(self, host="127.0.0.1", port=5984, creds=None):
        if not creds:
            creds = ("admin", "admin")
        self.couch_db_url = f"http://{host}:{port}"
        self.creds = creds
        self.client = None
    
    async def init_client(self):
        if self.client:
            return

        self.client = httpx.AsyncClient(auth=self.creds)

    async def create(self, db_name, doc):
        if not self.client:
            await self.init_client()

        res = await self.client.post(
            f"{self.couch_db_url}/{db_name}", json=doc
        )
        if res.status_code != 201:
            raise Exception(f"Not able to create doc {doc} error: {res}")
        return res, ""

    async def all_docs(self, db_name, partition="p1"):
        await self.init_client()

        if partition:
            url = f"{self.couch_db_url}/{db_name}/_partition/{partition}/_all_docs?include_docs=true"
        else:
            url = f"{self.couch_db_url}/{db_name}/_all_docs?include_docs=true"
            
        res = await self.client.get(url)
        # print(res.json())
        return res.status_code, res.json()

# cd = CouchDriver()
# asyncio.run(cd.all_docs('newsar'))

# doc = {"_id": "p1:x3", "time": "pass"}
# asyncio.run(cd.create("newsar", doc))