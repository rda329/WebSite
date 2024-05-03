from flask import Blueprint
from flask import render_template, request, session
import spacy
import json
import requests
from .models import update_total_api_call
import os
from dotenv import find_dotenv, load_dotenv


views = Blueprint('views', __name__)
missing_ing_lst = []
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
key = os.getenv("key")
app_id = os.getenv("app_id")

def store_recipe_json(user_id, data):
    with open(f"{user_id}_recipe_json.json", "w") as json_file:
        # Serialize the data dictionary into a JSON formatted string and write it to the file
        json.dump(data, json_file)

def load_json(file_name):
    with open(file_name, "r") as json_file:
        # Load the JSON data from the file into a Python dictionary
        data = json.load(json_file)
    return data

def extract_food_ingredients(list):
    # Load English tokenizer, tagger, parser, NER, and word vectors
    nlp = spacy.load('App/website/food_ner_model')
    missing_food_ingredients_list = []
    for text in list :
        doc = nlp(text)
        # Iterate through the entities detected by spaCy
        for entity in doc.ents:
            # Check if the entity is recognized as a FOOD entity
            if entity.label == 17898275690771780158 and entity.label not in missing_food_ingredients_list:
                missing_food_ingredients_list.append(entity.text)

    return missing_food_ingredients_list

#spoonacular api call to get recipes
def get_recipe(**kwargs):
    cuisine_type = kwargs["cuisine_type"]
    meal_type = kwargs["meal_type"]
    main_query = kwargs["main_query"]
    MinCarbs = kwargs["MinCarbs"]
    MaxCarbs = kwargs["MaxCarbs"]
    MinProtein = kwargs["MinProtein"]
    MaxProtein = kwargs["MaxProtein"]
    MinFat = kwargs["MinFat"]
    MaxFat = kwargs["MaxFat"]
    MinSugar = kwargs["MinSugar"]
    MaxSugar = kwargs["MaxSugar"]
    MinCalories = kwargs["MinCalories"]
    MaxCalories = kwargs["MaxCalories"]
    dish_Type = kwargs["dish_Type"]

    
    global app_id
    global key

    missing_ing_lst=session["missing_ing_lst"]  
    session["recipe_cnt"] = 0
    out_Ingredients="" 
    user_id = session["user_id"]   
    update_total_api_call(user_id)

    if missing_ing_lst:
        for item in missing_ing_lst:
            out_Ingredients+=f"&excluded={item}"
    else:
        out_Ingredients=""

    url = f"https://api.edamam.com/api/recipes/v2?app_id={app_id}&app_key={key}"+out_Ingredients
    params = {
    "type" : "public",
    "cuisineType" : cuisine_type,
    "mealType" : meal_type, 
    "q" : main_query, #A comma-separated list of ingredients or ingredient types that the recipes must contain.
    "nutrients[CHOCDF.net]" : f"{MinCarbs}-{MaxCarbs}", 
    "nutrients[PROCNT]" : f"{MinProtein}-{MaxProtein}",
    "nutrients[FAT]" : f"{MinFat}-{MaxFat}", 
    "nutrients[SUGAR]" : f"{MinSugar}-{MaxSugar}",
    "calories" : f"{MinCalories}-{MaxCalories}",
    "dishType" : dish_Type,
    "random" : "True",
    }

    for param in params :
        if params[param] == "" or params[param]=="-" or params[param]== None:
            continue
        else:
            url+=f"&{param}={params[param]}"

    result=requests.get(url)
    recipe_json=result.json()
    user_id = session["user_id"]
    store_recipe_json(user_id,recipe_json)
    

def results_for_user():
    user_id = session["user_id"]
    recipe_json = load_json(f"{user_id}_recipe_json.json")
    total_recipes =len(recipe_json['hits'])
    recipe_cnt = session["recipe_cnt"]
    recipe_found = False
    ingredient_list = None
    display = session["display"]
    try:
        if total_recipes==0:
            recipe_title = "Sorry We Could Not Find What You Were Craving"
            recipe_img = "/static/angry_chef.png"
            display = "onlyShowHeader"
            recipe_url = ""
            ingredient_list = []
        while not recipe_found and recipe_cnt < total_recipes:
            # Extracting recipe title, image, instructions, ingredient list, and recipe URL
            recipe_title = recipe_json['hits'][recipe_cnt]['recipe']['label']
            recipe_img = recipe_json['hits'][recipe_cnt]['recipe']['image']
            recipe_url = recipe_json['hits'][recipe_cnt]['recipe']['url']
            ingredient_list = recipe_json['hits'][recipe_cnt]['recipe']['ingredientLines']
            # Check if recipe URL is empty
            if recipe_url and recipe_title and recipe_img and ingredient_list:
                recipe_found = True
    except KeyError:
        display = "onlyShowHeader"
        recipe_title = "There Has Been An Issue In The Kitchen!"
        recipe_img = "/static/angry_chef.png"
        recipe_url = ""
        ingredient_list = []  
    
    if ingredient_list:
        for i in range(len(ingredient_list)):
                    ingredient_list[i]=ingredient_list[i].title()
    else:
        display = "onlyShowHeader"
        recipe_title = "Sorry We Could Not Find What You Were Craving"
        recipe_img = "/static/angry_chef.png"
        recipe_url = ""
        ingredient_list = []  
    
    return the_kitchen(recipe_title=recipe_title, recipe_img=recipe_img, display=display, recipe_url=recipe_url, ingredient_list=ingredient_list, total_recipes=total_recipes)


@views.route('/')
def home():
    session.clear()
    return render_template("Homepage.html")

@views.route('/learn_more')
def instructions():
    return render_template('learn_more.html')

@views.route('/thekitchen', methods=['GET','POST'], endpoint="Thekitchen")
def the_kitchen(**kwargs):
    if "logged_in" in session:
        try:
            recipe_title = kwargs["recipe_title"]
        except KeyError:
            recipe_title = ""
        try:
            recipe_img = kwargs["recipe_img"]
        except KeyError:
            recipe_img = ""
        try:
            display = kwargs["display"]
        except KeyError:
            display = "mySection_hidden"
        try:
            recipe_url = kwargs["recipe_url"]
        except KeyError:
            recipe_url = ""
        try:
            ingredient_list = kwargs["ingredient_list"]
        except KeyError:
            ingredient_list = []
        if "recipe_cnt" in session:
            recipe_cnt = int(session["recipe_cnt"])
        else:
            recipe_cnt = 0
            session["recipe_cnt"] = recipe_cnt
        try:
            total_recipes = kwargs["total_recipes"]
        except KeyError:
            total_recipes = 0

        try:
            alert = kwargs["alert"]
        except:
            alert = ""
        
        fname = session["fname"]
        if "missing_ing_lst" in session:
            missing_ing_lst = session["missing_ing_lst"] 
        else:
            missing_ing_lst = [] #Get missing list from db
            session["missing_ing_lst"] = missing_ing_lst
        if missing_ing_lst == []:
            missing_ing_lst_display = "mySection_hidden"
        else:
            missing_ing_lst_display = "mySection_visible"
        return render_template("TheKitchen.html", display_result=display, food_img=recipe_img, food_title=recipe_title , recipe_url=recipe_url, food_ingredients=ingredient_list, missing_ing_lst_display=missing_ing_lst_display , missing_ing_items=missing_ing_lst, recipe_cnt=recipe_cnt+1, total_recipes=total_recipes, alert=alert, fname=fname)
    else:
        return render_template("login_signup.html", display= "sign_in") 

#API call when Lets cook button is clicked
@views.route('/thekitchen/turn_on_theheat', methods=['GET','POST'], endpoint="getrecipeparms")
def find_recipe():
    if "logged_in" in session:
        if request.method == 'POST':
            display="mySection_visible"
            session["display"] = display
            cuisine_type = request.form.get("selectedOption")
            button = request.form.get('row1_value')
            dish_Type = ""
            meal_type = ""
            if button== "Button 1":
                meal_type = "Breakfast"
            elif button == "Button 2":
                meal_type = "Lunch"
            elif button == "Button 3":
                meal_type = "Dinner"
            elif button == "Button 4":
                meal_type = "Snack"
            elif button == "Button 5":
                meal_type = "Teatime"
            elif button == "Button 6":
                meal_type = ""
                dish_Type = "Desserts"
            
            try:
                MaxCarbs = request.form.get("Maxcarbs")
                if MaxCarbs:
                    MaxCarbs = float(MaxCarbs)
                else:
                    MaxCarbs = "10000"
                MinCarbs = request.form.get("Mincarbs")
                if MinCarbs:
                    MinCarbs = float(MinCarbs)
                else:
                    MinCarbs = "0"
                MaxProtein = request.form.get("Maxprotein")
                if MaxProtein:
                    MaxProtein = float(MaxProtein)
                else:
                    MaxProtein = "10000"
                MinProtein = request.form.get("Minprotein")
                if MinProtein:
                    MinProtein = float(MinProtein)
                else:
                    MinProtein = "0"
                MaxFat = request.form.get("Maxfat")
                if MaxFat:
                    MaxFat = float(MaxFat)
                else:
                    MaxFat = "10000"
                MinFat = request.form.get("Minfat")
                if MinFat:
                    MaxFat = float(MaxFat)
                else:
                    MinFat = "0"
                MaxSugar = request.form.get("Maxsugar")
                if MaxSugar:
                    MaxSugar = float(MaxSugar)
                else:
                    MaxSugar = "10000"
                MinSugar = request.form.get("Minsugar")
                if MinSugar:
                    MinSugar = float(MinSugar)
                else:
                    MinSugar = "0"
                MaxCalories = request.form.get("Maxcalories")
                if MaxCalories:
                    MaxCalories = float(MaxCalories)
                else:
                    MaxCalories = "10000"
                MinCalories = request.form.get("Mincalories")
                if MinCalories:
                    MinCalories = float(MinCalories)
                else:
                    MinCalories = "0"
            except ValueError:
                return the_kitchen(alert="Invalid Input: \nMacro-nutrients must be numerical inputs.")

            itemsArray = request.form.getlist('items-input')
            main_query=""
            for item in itemsArray:
                main_query+=f"{item},"
            

            get_recipe(cuisine_type=cuisine_type, meal_type=meal_type, main_query=main_query, MinCarbs=MinCarbs, MaxCarbs=MaxCarbs, MinProtein=MinProtein, MaxProtein=MaxProtein, MinFat=MinFat, MaxFat=MaxFat, MinSugar=MinSugar, MaxSugar=MaxSugar, MinCalories=MinCalories, MaxCalories=MaxCalories, dish_Type=dish_Type)
            return results_for_user()
    else:
        return render_template("login_signup.html", display= "sign_in") 
        
          
    

#When you click New Recipe Button
@views.route('/newRecipe', methods=['GET','POST'])
def new_recipe():
    if "logged_in" in session:
        recipe_cnt = session["recipe_cnt"]
        recipe_cnt+=1
        session["recipe_cnt"] = recipe_cnt
        return results_for_user()
    else:
        return render_template("login_signup.html", display= "sign_in") 
    


#Shopping list
@views.route('/thekitchen/missing_ingredient', methods=['GET','POST'], endpoint="shoppinglist")
def shopping_list():
    if "logged_in" in session:
        if request.method == "POST":
            # Access the list data sent from the client side
            items_list = request.form.getlist('items[]')
            # Print the items
            missing_ing_lst=[]
            for item in items_list:
                updated_item=item[:-1]
                missing_ing_lst.append(updated_item) 
                #write code to update missing_ing_lst in db
        session["missing_ing_lst"] = missing_ing_lst
        return results_for_user()
    else:
        return render_template("login_signup.html", display= "sign_in") 

#When you save mssing item
@views.route('/thekitchen/save_missing_ingredient', methods=['GET','POST'], endpoint="letscook")
def get_missing_ingredients():
    if "logged_in" in session:
        if request.method == "POST":
            missing_ing_lst = session["missing_ing_lst"]
            user_input_missing_items=request.form.getlist("missing_food_item")
            missing_food_ingredients_list=extract_food_ingredients(user_input_missing_items)
            for item in missing_food_ingredients_list:
                if item in missing_ing_lst:
                    pass
                else:
                    missing_ing_lst.append(item)
        session["missing_ing_lst"] = missing_ing_lst 
        # write code to update missing_ing_lst in db
        return results_for_user()
    else:
        return render_template("login_signup.html", display= "sign_in") 
