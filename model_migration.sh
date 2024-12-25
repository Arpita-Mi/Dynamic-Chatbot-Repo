
# Set environment variables if needed
export DATABASE_URL="postgresql+psycopg2://postgres:admin@localhost:5432/dynamic_chatbot"

# Generate the migration
alembic revision --autogenerate -m "Add dynamic fields for organization model"

#Apply the migration
alembic upgrade head

echo "Alembic migration applied successfully!"
