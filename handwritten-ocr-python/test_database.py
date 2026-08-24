from database import check_database


print("=" * 60)
print("MONGODB CONNECTION TEST")
print("=" * 60)


success = check_database()


if success:

    print("\nMongoDB test PASSED.")

else:

    print("\nMongoDB test FAILED.")