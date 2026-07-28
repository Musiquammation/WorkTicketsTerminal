from Database import Database
from shell import shell
from dotenv import load_dotenv
import os

load_dotenv()




def getEnv(key):
	value = os.getenv(key)
	if value is None:
		raise Exception("Missing " + key)

	return value


if __name__ == "__main__":
	db = Database(getEnv("DATABASE_URL"))
	shell(db)

