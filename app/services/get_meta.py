import aiohttp, asyncio

S2_URL = "https://api.semanticscholar.org/graph/v1/paper/{}"
FIELDS = "title,abstract,year,venue,referenceCount,citationCount," \
         "influentialCitationCount,fieldsOfStudy,authors,tldr"

async def fetch_paper(session, pid):
    url = S2_URL.format(pid)
    params = {"fields": FIELDS}
    async with session.get(url, params=params, timeout=10) as r:
        r.raise_for_status()
        return await r.json()

async def fetch_many(pids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_paper(session, pid) for pid in pids]
        return await asyncio.gather(*tasks)