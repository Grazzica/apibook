from pydantic import BaseModel

class Prediction_schema(BaseModel):
    book_title: str
    target: str
    prediction: float
    

  