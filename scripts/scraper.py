import requests
import re
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = 'https://books.toscrape.com/'
OUTPUT_PATH = 'data/books.csv'


def get_categories(url):
    response = requests.get(url)

    if response.status_code !=200:
        raise Exception(f"Falha ao acessar {response}: {response.status_code}")
    
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    elementos_categoria = soup.find_all(href=re.compile("category/books/"))

    categorias = []
    for elemento in elementos_categoria:
        cat = elemento.text.strip()
        url = urljoin(BASE_URL,  elemento.get('href'))
        categorias.append({'categoria': cat ,'url': url})
    
    return categorias


def get_book_data(soup, categoria, base_url):
    livros_pagina = []
    livros = soup.find_all('article', class_='product_pod')

    for livro in livros:
        titulo = livro.h3.a['title']  

        categoria_livro = categoria.get('categoria')

        preco = livro.find(class_='price_color').text
        preco_limpo = preco.replace("Â", "") 

        rating = livro.find('p', class_='star-rating')['class'][1]

        disponibilidade = livro.find(class_='instock availability').text.strip()

        imagem = urljoin(base_url, livro.find('img')['src'])

        livros_pagina.append({
            
            "titulo": titulo,
            "categoria": categoria_livro,
            "preço": preco_limpo,
            "rating": rating,
            "disponibilidade":disponibilidade,
            "imagem": imagem
            })
    return livros_pagina


def get_book_dict(categorias):
    livros = []
    livros_completo=[]

    for categoria in categorias:
        categoria_url = categoria.get('url')   
        categoria_response = requests.get(categoria_url)

        if categoria_response.status_code !=200:
            raise Exception(f"Falha ao acessar {categoria_response}: {categoria_response.status_code}")

        categoria_soup = BeautifulSoup(categoria_response.text, 'html.parser')
        livros.extend(get_book_data(categoria_soup, categoria, categoria_url))
        
        while categoria_soup.find("a", string="next") != None: 
            new_url = urljoin( categoria_url, categoria_soup.find("a", string="next").get('href'))
            categoria_response = requests.get(new_url)

            if categoria_response.status_code !=200:
                raise Exception(f"Falha ao acessar {categoria_response}: {categoria_response.status_code}")

            categoria_soup = BeautifulSoup(categoria_response.text, 'html.parser') 
            livros.extend(get_book_data(categoria_soup, categoria, new_url))
    
    id_counter = 0
    for livro in livros:
        livro_id = {'id':id_counter}
        livro_atualizado = {**livro_id, **livro}
        livros_completo.append(livro_atualizado)
        id_counter += 1
   
    return livros_completo


def create_csv(books_data):
    nomes_colunas = books_data[0].keys()

    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.DictWriter(arquivo_csv, fieldnames=nomes_colunas)
        escritor.writeheader()
        escritor.writerows(books_data)


def main():
    categorias = get_categories(BASE_URL)
    books_data = get_book_dict(categorias)
    create_csv(books_data)



if __name__=="__main__":
    main()


