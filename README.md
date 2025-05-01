
# 🚗 SPOT - Smart Parking Organization Tool  

SPOT is a **Django-based web application** designed to streamline parking management efficiently. The system enables users to register parking details, track vehicle entries and exits, calculate parking duration, process payments, and manage parking lot operations—all with a **modern, responsive UI**.  

![Spot Banner](./home/static/images/spot-banner.png)

## 📌 Features  
✅ **Add Parking Records** – Register vehicle details and assign parking spots.  
✅ **Track Vehicle Entries & Exits** – Log entry and exit times.  
✅ **Calculate Parking Duration** – Automatically compute time parked.  
✅ **Payment System** – Update and track parking payments.  
✅ **Glassmorphism UI** – A sleek, modern, and responsive design.  
✅ **Admin Authorization** – Track who authorized the parking entry.  

## 🏗️ Tech Stack  
🔹 **Backend:** Django (Python)  
🔹 **Frontend:** HTML, CSS (Glassmorphism UI)  
🔹 **Database:** SQLite / PostgreSQL  
🔹 **Templating:** Django Templates  

## 🚀 Getting Started  

### 1️⃣ Clone the Repository  
```sh
git clone https://github.com/tharun977spot-main.git
cd spot-main
```

### 2️⃣ Set Up a Virtual Environment  
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3️⃣ Install Dependencies  
```sh
pip install -r requirements.txt
```

### 4️⃣ Apply Migrations  
```sh
python manage.py migrate
```

### 5️⃣ Run the Server  
```sh
python manage.py runserver
```
Now, open **http://127.0.0.1:8000/** in your browser! 🚀  

## 📂 Project Structure  
```
SPOT/
│── parking/              # Parking app (Django app)
│   ├── templates/        # HTML Templates
│   ├── static/           # CSS & JS Files
│   ├── views.py          # Views (Business logic)
│   ├── models.py         # Database models
│   ├── urls.py           # URL routing
│── spot/                 # Main Django project settings
│── db.sqlite3            # Database file (for development)
│── manage.py             # Django project management script
│── requirements.txt      # Dependencies
│── README.md             # Project documentation
```

## 🛠️ Environment Variables  
Make sure to create a **`.env`** file in the root directory and set the required environment variables. Example:  
```ini
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

## 📸 UI Preview  
<img src="screenshot.png" alt="SPOT Dashboard" width="600">  

## 💡 Future Enhancements  
🔹 **QR Code Integration** for quick check-ins  
🔹 **Role-Based Access Control** for admins and staff  
🔹 **Automated Payment System** with online transactions  

## 🤝 Contributing  
1. **Fork the repository**  
2. **Create a new branch:** `git checkout -b feature-branch`  
3. **Commit your changes:** `git commit -m "Add new feature"`  
4. **Push to the branch:** `git push origin feature-branch`  
5. **Submit a pull request** 🚀  

## 📜 License  
This project is **open-source** and available under the **MIT License**.  

---

👨‍💻 Developed by **Tharun Raman & Rohan Ravindran**  
