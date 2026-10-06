

def main():
    username = input("MySQL username: ")
    password = getpass("MySQL password: ")

    engine = get_engine(username, password)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT DATABASE()"))
        print(f"Connected to: {result.scalar()}")

    save_to_database(df, "cleaned_data", engine)

    results = run_query(
    "SELECT * FROM cleaned_data LIMIT 5",
    engine
    )

    print(results)

if __name__ == "__main__":
    main()