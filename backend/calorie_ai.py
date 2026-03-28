
def calculate_calories(data):
    weight=data.get("weight",80)
    height=data.get("height",175)
    age=data.get("age",28)
    return int((10*weight)+(6.25*height)-(5*age)+5)
