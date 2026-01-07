import csv
from fastapi import APIRouter, Depends, HTTPException
from scripts.scraper import main
from api.models import User
from api.auth import get_current_user



with open('data/books.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    books = list(reader)


def normalize(text):
    return text.lower().replace(" ", "")



def normalize_price(price: str): 
    return float(price.replace("£", ""))



def get_categories():
    categories = []
    for book in books:
        if book["categoria"] not in categories:
            categories.append(book["categoria"])
    return categories



router = APIRouter()


@router.get("/books")
def list_books():
    if books:
        return books
    raise HTTPException(status_code=404, detail="Books list not available")



@router.get("/categories")
def list_categories():
    return get_categories()



@router.get("/health")
def health_check():
    return {"status": "healthy", "books_loaded": len(books)}



@router.get("/books/search")
def book_search(title:str = "", category:str = ""):
    
    if title == "" and category == "":
       raise HTTPException(status_code = 404, detail="Invalid Search")  

    normalized_title = normalize(title)
    normalized_category = normalize(category)
    
    result = []
    for book in books:
        title_pass = True
        category_pass = True 
    
        if title != "":
            title_pass = normalized_title in normalize(book["titulo"])
            
        
        if category != "":
            category_pass = normalized_category in normalize(book["categoria"])
            
            
        if title_pass and category_pass:
            result.append(book)


    if result:
        return result
    raise HTTPException(status_code = 404, detail="Book not found")



@router.get("/stats/overview")
def books_overview():
    rating = {"One": 0, "Two": 0, "Three": 0, "Four": 0, "Five": 0}
    books_total = len(books)
    sum_price = 0.00
         
    for book in books:
        sum_price += normalize_price(book["preço"])
        rating[book["rating"]] += 1

    avg_price = sum_price / books_total
    
    return {
        "Total de livros": books_total,
        "Preço Médio" : f"£{round(avg_price, 2)}",
        "Rating One" : rating["One"],
        "Rating Two" : rating["Two"],
        "Rating Three" : rating["Three"],
        "Rating Four" : rating["Four"],
        "Rating Five" : rating["Five"],
    }



@router.get("/stats/categories")
def category_stats():
    categories_list = get_categories()
    result = []

    for category in categories_list:
        
        num_books = 0
        price_sum = 0.0
        
        for book in books:
            if book["categoria"] == category:
                num_books += 1
                price_sum += normalize_price(book["preço"])

        avg_price = round(price_sum / num_books, 2)
        result.append({"Category" : category, "Number of Books": num_books, "Average Price": f"£{avg_price}"})
    
    return result



@router.get("/books/top-rated")
def top_rated():
    result = []
    for book in books:
        if book["rating"] == "Five":
            result.append(book)
    
    return result



@router.get("/books/price-range")
def get_books_per_price_range(min:float, max:float):
    if min > max:
        raise HTTPException(status_code=404, detail="Invalid search: min value > max value.")
    
    result = []
    for book in books:
        if min <= normalize_price(book["preço"]) <= max:
            result.append(book)

    return result 



@router.post("/scraping/trigger")
def trigger_scrapper(current_user: User = Depends(get_current_user)):
    main()
    return {"message": "Scrapper executed", "triggered_by": current_user.user_name}



@router.get("/books/{id}")
def book_id(id:int):
    if -1 < id < len(books):
        return books[id]
    raise HTTPException(status_code=404, detail="id not found")


