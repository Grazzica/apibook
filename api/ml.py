import csv
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.routes import get_categories
from api.models import User, Prediction
from api.schemas import Prediction_schema
from api.database import get_db
from api.auth import get_current_user

with open('data/books.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    books = list(reader)

router = APIRouter()

def normalize_for_ml(price: str):
    return round(float(price.replace("£", ""))/100, 4)

def get_features(data):
    category_conversion = {}
    categories = get_categories()
    for category in categories:
        category_conversion[category] = categories.index(category)
    
    availability_conversion = {"In stock": 1, "Out of stock": 0}
    rating_conversion = {"One" : 1, "Two" : 2, "Three" : 3, "Four" : 4, "Five" : 5}
    
    ml_title = data["titulo"]
    ml_category = category_conversion[data['categoria']]
    ml_price = normalize_for_ml(data['preço'])
    ml_rating = rating_conversion[data['rating']]
    ml_availability = availability_conversion[data['disponibilidade']]

    return {'titulo': ml_title, 
            'categoria': ml_category, 
            'preço': ml_price,
            'rating': ml_rating,
            'disponibilidade': ml_availability
            }


@router.get("/ml/features")
def get_ml_features():
    ml_features = []
    for book in books:
        ml_features.append(get_features(book))
    
    return ml_features



@router.get("/ml/training-data")
def get_ml_features(target:str):
    available_targets = ["preço", "rating"]
    if target not in available_targets:
        raise HTTPException(status_code=404, detail=f"Target not available.")
    
    ml_features = []
    for book in books:
        ml_features.append(get_features(book))
    
    target_name = ""
    feature_name = ""
    
    x = []
    y = []

    if target == available_targets[0]:
        for item in ml_features:
            x.append([item["rating"], item["disponibilidade"], item["categoria"]])
            y.append(item["preço"])
        target_name = available_targets[0]
        feature_name = available_targets[1]

    elif target == available_targets[1]:
        for item in ml_features:
            x.append([item["preço"], item["disponibilidade"], item["categoria"]])
            y.append(item["rating"])
        target_name = available_targets[1]
        feature_name = available_targets[0]

    return {
        "target_name": target_name,
        "feature_names": [feature_name, "disponibilidade", "categoria"],
        "X" : x,
        "y" : y
        }

    
@router.post("/ml/prediction")
def receive_prediction(prediction: list[Prediction_schema], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    predictions = []
    for item in prediction:
        predict = Prediction(
            book_title = item.book_title,
            target = item.target,
            prediction = item.prediction,
            user = current_user.user_name,
            created_at = datetime.datetime.utcnow()
        )
        predictions.append({
            "book_title": predict.book_title,
            "targer": predict.target,
            "prediction": predict.prediction
        })

        db.add(predict)
    db.commit()
    return {"username": current_user.user_name, "date": datetime.datetime.utcnow(), "Predictions added": predictions }
    
    