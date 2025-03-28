# 🍽️ Django Recipe Chatbot 🤖

A chatbot-powered recipe recommendation web application built using **Django**, **spaCy**, and **PostgreSQL/MySQL/SQLite**. The chatbot intelligently filters recipes based on user queries like `"high protein recipes"`, `"vegetarian dishes"`, or `"low-calorie meals"`.

---

## 🚀 Features

✅ Search recipes using **Natural Language Processing (NLP)** with **spaCy**  
✅ Filter by **calories, protein, fat, meal type, cooking time, vegetarian, and spiciness**  
✅ Supports **pagination** for browsing recipes  
✅ Uses **PostgreSQL, MySQL, or SQLite** as the database  
✅ Import recipes from a **CSV file**  

---

## 📦 Installation & Setup

### 1⃣ Clone the Repository  
```bash
git clone https://github.com/yourusername/django-recipe-chatbot.git
cd django-recipe-chatbot
```

### 2⃣ Create a Virtual Environment (Optional, but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3⃣ Install Dependencies  
```bash
pip install -r requirements.txt
```

### 4⃣ Download spaCy Language Model  
```bash
python -m spacy download en_core_web_sm
```

---

## 🛠️ Database Configuration

### **SQLite (Default)**
SQLite is the default database, and no extra setup is needed. The database file will be created automatically.

### **PostgreSQL Setup**
download and connect your database to this project(update the setting.py with your credentials)

## 📥 Import Recipes from CSV
Run the following Django command to import data:  
   ```bash
   python manage.py import_recipes recipes.csv
   ```

---

## 🚀 Run the Application
```bash
python manage.py migrate
python manage.py runserver
```

---



