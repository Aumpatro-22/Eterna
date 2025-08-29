#!/bin/bash
echo "Creating virtual environment..."
python3 -m venv venv
echo

echo "Activating virtual environment..."
source venv/bin/activate
echo

echo "Installing requirements..."
pip install -r requirements.txt
echo

echo "Setting up environment variables..."
cp .env.example .env
echo

echo "Setting up database..."
python manage.py migrate
echo

echo "Creating superuser..."
python manage.py createsuperuser
echo

echo "Setup complete!"
echo "Run 'source venv/bin/activate' to activate the virtual environment"
echo "Run 'python manage.py runserver' to start the development server"
