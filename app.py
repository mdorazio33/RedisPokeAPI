from flask import Flask, jsonify
import matplotlib.pyplot as plt
import requests
import json
from flask_restx import Api, Resource
from db_config import get_redis_connection

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="My Python App using Redis and the PokeAPI",
    description="A Python app that reads JSON from an API, inserts into RedisJSON, and creates 3 Matplotlib Charts.",
)

# Establish database connections
redis_conn = get_redis_connection()


@api.route("/")
class HomePage(Resource):
    def get(self):
        """Load HomePage.

        Returns:
            json: Welcome to my Python App!
        """
        return jsonify("Welcome to my Python App!")


@api.route("/pokemon/<string:pokemon_name>")
class Pokemon(Resource):
    def get(self, pokemon_name):
        """Read Pokemon data by name as JSON and insert into Redis.

        Args:
            pokemon_name (str): The name of the Pokemon.

        Returns:
            json: Pokemon data.
        """
        pokemon_data_loader = PokemonDataLoader()
        pokemon_data = pokemon_data_loader.fetch_pokemon_data(pokemon_name)
        if pokemon_data:
            pokemon_data_loader.insert_into_redis(pokemon_name, pokemon_data)
            return jsonify(pokemon_data)
        else:
            return jsonify({"message": f"Failed to fetch data for {pokemon_name.capitalize()} from the Pokemon API."})


@api.route("/pokemon/<string:pokemon_name>/height_comparison")
class PokemonHeightComparison(Resource):
    def get(self, pokemon_name):
        """Compare Pokemon height with the average heights of a dog, human, and elephant via three separate bar charts.

        Args:
            pokemon_name (str): The name of the Pokemon.

        Returns:
            json: Comparison results.
        """
        comparer = PokemonHeightComparer()
        dog_height = 0.5
        human_height = 1.7
        elephant_height = 3.5
        
        pokemon_data_loader = PokemonDataLoader()
        pokemon_data = pokemon_data_loader.fetch_pokemon_data_from_redis(pokemon_name)
        
        if pokemon_data:
            comparer.plot_height_comparison(pokemon_name, human_height, dog_height, elephant_height)
            return jsonify({"message": "Height comparison charts created."})
        else:
            return jsonify({"message": f"Data for {pokemon_name.capitalize()} does not exist in Redis."})

class PokemonDataLoader:
    """
    A class to fetch Pokemon data from the API and store it in Redis.
    """

    def __init__(self):
        self.api_url = "https://pokeapi.co/api/v2/pokemon"

    def fetch_pokemon_data(self, pokemon_name):
        """
        Fetches data for a specific Pokemon from the PokeAPI.

        Args:
            pokemon_name (str): The name of the Pokemon.

        Returns:
            dict or None: A dictionary containing the Pokemon's data if the request is successful,
            otherwise None if the request fails or the Pokemon data is not found.
        """
        url = f"{self.api_url}/{pokemon_name.lower()}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def insert_into_redis(self, pokemon_name, data):
        """
        Inserts Pokemon data into Redis.

        Args:
            pokemon_name (str): The name of the Pokemon.
            data (dict): The Pokemon's data to be inserted into Redis.

        Returns:
            None
        """
        redis_key = f"pokemon:{pokemon_name.lower()}"
        redis_conn.set(redis_key, json.dumps(data))

    def fetch_pokemon_data_from_redis(self, pokemon_name):
        """
        Fetches Pokemon data from Redis.

        Args:
            pokemon_name (str): The name of the Pokemon.

        Returns:
            dict or None: A dictionary containing the Pokemon's data if it exists in Redis,
            otherwise None.
        """
        redis_key = f"pokemon:{pokemon_name.lower()}"
        data = redis_conn.get(redis_key)
        if data:
            return json.loads(data)
        else:
            return None


class PokemonHeightComparer:
    """
    A class to compare the height of a Pokemon with average heights.
    """

    def __init__(self):
        pass

    def plot_height_comparison(self, pokemon_name, human_height, dog_height, elephant_height):
        """
        Plots three separate outputs as bar graphs, each comparing the height of the Pokemon with the average heights
        of a dog, human, and elephant.

        Args:
            pokemon_name (str): The name of the Pokemon.
            dog_height (float): The average height of a dog in meters.
            human_height (float): The average height of a human in meters.
            elephant_height (float): The average height of an elephant in meters.
        """
        pokemon_data_loader = PokemonDataLoader()
        pokemon_data = pokemon_data_loader.fetch_pokemon_data_from_redis(pokemon_name)
        if pokemon_data is not None:
            pokemon_height = float(pokemon_data['height']) / 10  # Convert height from decimeters to meters

            # Dog vs Pokemon Bar Chart
            categories_dog = ['Dog', pokemon_name.capitalize()]
            heights_dog = [dog_height, pokemon_height]
            plt.figure()
            plt.bar(categories_dog, heights_dog, color='blue')
            plt.ylabel('Height (m)')
            plt.title(f'Height Comparison: Dog vs {pokemon_name.capitalize()}')
            plt.show()

            # Human vs Pokemon Bar Chart
            categories_human = ['Human', pokemon_name.capitalize()]
            heights_human = [human_height, pokemon_height]
            plt.figure()
            plt.bar(categories_human, heights_human, color='blue')
            plt.ylabel('Height (m)')
            plt.title(f'Height Comparison: Human vs {pokemon_name.capitalize()}')
            plt.show()

            # Elephant vs Pokemon Bar Chart
            categories_elephant = ['Elephant', pokemon_name.capitalize()]
            heights_elephant = [elephant_height, pokemon_height]
            plt.figure()
            plt.bar(categories_elephant, heights_elephant, color='blue')
            plt.ylabel('Height (m)')
            plt.title(f'Height Comparison: Elephant vs {pokemon_name.capitalize()}')
            plt.show()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
