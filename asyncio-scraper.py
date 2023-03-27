import asyncio
import hashlib
import os
import re
from urllib.parse import quote, unquote
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from markdownify import markdownify

PAGES_TO_SCRAPE = [('Páginas', 'Consul', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/Consul.aspx'),
('Páginas', 'Consulado', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/Consulado.aspx'),
('Páginas', 'Demarcación', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/Demarcaci%c3%b3n.aspx'),
('Páginas', 'Horario, localización y contacto', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/Horario,-localizaci%c3%b3n-y-contacto.aspx'),
('Páginas', 'Ofertas de empleo', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/Ofertas-de-empleo.aspx'),
('Páginas', 'Tasas consulares 2023', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Consulado/Paginas/TASAS-CONSULARES-2023.aspx'),
('Páginas', 'Establecerse', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Establecerse.aspx'),
('Páginas', 'Trabajar', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Trabajar.aspx'),
('Páginas', 'Educación y sanidad', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Educaci%c3%b3n-y-sanidad.aspx'),
('Páginas', 'Enlaces de interés', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Enlaces-de-inter%c3%a9s.aspx'),
('Páginas', 'Seguridad y otros aspectos', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Seguridad-y-otros-aspectos.aspx'),
('Páginas', 'Consejode Residentes-Españoles', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Consejo-de-Residentes-Espa%c3%b1oles.aspx'),
('Páginas', 'Documentación y trámites', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Documentaci%c3%b3n-y-tr%c3%a1mites.aspx'),
('Páginas', 'Conoce Espana', 'https://www.exteriores.gob.es/es/ServiciosAlCiudadano/Paginas/Conoce-Espana.aspx'),
('Páginas', 'Recomendaciones de viaje', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/ViajarA/Paginas/Recomendaciones-de-viaje.aspx'),
('Páginas', 'Noticias', 'https://www.exteriores.gob.es/Consulados/amsterdam/es/Comunicacion/Noticias/Paginas/index.aspx'),
# paginas web de la embajada
('Páginas', 'Embajador-a',"https://www.exteriores.gob.es/Embajadas/lahaya/es/Embajada/Paginas/Embajador.aspx"),
('Páginas', 'Contacto. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/Embajada/Paginas/Contacto.aspx"),
('Páginas', 'Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/Embajada/Paginas/Embajada.aspx"),
('Páginas', 'Consulados',"https://www.exteriores.gob.es/Embajadas/lahaya/es/Embajada/Paginas/Consulados.aspx"),
('Páginas', 'Horario, localización y contacto. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/Embajada/Paginas/Horario,-localizaci%c3%b3n-y-contacto.aspx"),
('Páginas', 'Ofertas de empleo. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/Embajada/Paginas/Ofertas-de-empleo.aspx"),
('Páginas', 'Documentación y trámites. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/ViajarA/Paginas/Documentaci%c3%b3n-y-tr%c3%a1mites.aspx"),
('Páginas', 'Establecerse. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/ViajarA/Paginas/Establecerse.aspx"),
('Páginas', 'Educación y sanidad. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/ViajarA/Paginas/Educaci%c3%b3n-y-Sanidad.aspx"),
('Páginas', 'Trabajar. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/ViajarA/Paginas/Trabajar.aspx"),
('Páginas', 'Enlaces de interés. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/ViajarA/Paginas/Enlaces-de-inter%c3%a9s.aspx"),
('Páginas', 'Recomendaciones de viaje. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/ViajarA/Paginas/Recomendaciones-de-viaje.aspx"),
('Páginas', 'Noticias. Embajada',"https://www.exteriores.gob.es/Embajadas/lahaya/es/Comunicacion/Noticias/Paginas/index.aspx")
 ]

URL_BASE = "https://www.exteriores.gob.es/Consulados/amsterdam/es/ServiciosConsulares/Paginas/index.aspx"
USER_AGENT = UserAgent().random
MAX_CONCURRENT_REQUESTS = 3
DELAY_BETWEEN_REQUESTS = 1


async def fetch_url(url,semaphore):
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"User-Agent": USER_AGENT}) as response:
                return await response.text()
        

async def get_services(semaphore):
    html_content = await fetch_url(URL_BASE,semaphore)
    html = BeautifulSoup(html_content, "html.parser")
    services = []
    for select in html.find_all("select"):
        for option in select.find_all("option"):
            if option.get("parentcategory"):
                category = option.get("parentcategory")
                page = option.get("value")
                path = f'Servicios Consulares/{category}'
                url = f"{URL_BASE}?scco=Pa%C3%ADses+Bajos&scd=9&scca={quote(category)}&scs={quote(page)}"
                services.append((path, page, url))

    return services


async def process_page(directory, filename, url,semaphore):
    
    html_content = await fetch_url(url,semaphore)
    soup = BeautifulSoup(html_content, "html.parser")
    container = BeautifulSoup("<div></div>", "html.parser").div

    section_content = soup.find_all("div", class_="single__detail-Wrapper")
    if len(section_content) == 0 :
        print(f' error empty {filename}')        
        return "No content"
    
    if section_content:
        container.append(section_content[-1])
    
    news_section = soup.find("ul", class_="newResults__list")
    if news_section:
        container.append(news_section)

    travel = soup.find("div", class_="main-content-travel-recommendation")
    if travel:
        container.append(travel)

    accordeon = soup.find("div", class_="section__accordion-wrapper")
    if accordeon:
        container.append(accordeon)

    # link to original page
    original_link = soup.new_tag('a', href=url)
    original_link.string = 'Enlace a la página original'
    container.append(original_link)

    for link in container.find_all("a", target="_blank"):
        link.attrs = {k: v for k, v in link.attrs.items() if k != "title"}
        for img in link.find_all("img"):
            img.decompose()

    for link in container.find_all("a", href=True):
        if link["href"].startswith("/"):
            link["href"] = "https://www.exteriores.gob.es" + quote(unquote(link["href"]))

    md_content = markdownify(str(container))

    return md_content

async def save_content(directory, filename, md_content):
    changes = False
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f"{os.path.basename(filename)}.md")
    if not os.path.exists(file_path):
        async with aiofiles.open(file_path, "w") as file:
            await file.write(md_content)
        changes = True
    else:
        async with aiofiles.open(file_path, "rb") as file:
            file_content = await file.read()
            old_hash = hashlib.sha256(file_content).hexdigest()
        new_hash = hashlib.sha256(md_content.encode()).hexdigest()
        if old_hash != new_hash:
            async with aiofiles.open(file_path, "w") as file:
                await file.write(md_content)
            changes = True
    return changes

async def process_and_save(directory, filename, url,semaphore):
    md_content = await process_page(directory, filename, url,semaphore)
    changed = await save_content(directory, filename, md_content)
    return changed

async def send_telegram_notification():
    bot_token, chat_id = open('bot-token.txt', 'r').read().split(',')
    payload = {
        "chat_id": chat_id,
        "text": f'[🔄 Cambios web consulado](https://github.com/JuanMaCuevas/consulado-es-amsterdam/commits/develop/)',
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data=payload) as response:
            await response.text()

async def main():
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    services = await get_services(semaphore)
    
    pages = PAGES_TO_SCRAPE + services
    print(f"PReady to scrape {len(pages)} pages...")    
    tasks = []
    for directory, filename, url in pages:
            tasks.append(process_and_save(directory, filename, url,semaphore))
            await asyncio.sleep(DELAY_BETWEEN_REQUESTS)
    
    print(f"Executing {len(tasks)} tasks...")

    results = await asyncio.gather(*tasks)
    changes = any(results)

    if changes:
        print("Changes detected!")
        # await send_telegram_notification()
    else:
        print("No changes detected.")

if __name__ == "__main__":
    asyncio.run(main())

