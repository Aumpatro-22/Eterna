@echo off
echo Creating virtual environment...
python -m venv venv
echo.

echo Activating virtual environment...
call venv\Scripts\activate
echo.

echo Installing requirements...
pip install -r requirements.txt
echo.

echo Setting up environment variables...
copy .env.example .env
echo.

echo Setting up database...
python manage.py migrate
echo.

echo Creating superuser...
python manage.py createsuperuser
echo.

echo Setup complete!
echo Run 'venv\Scripts\activate' to activate the virtual environment
echo Run 'python manage.py runserver' to start the development server
