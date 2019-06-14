from django.shortcuts import render
import requests

class Pelicula:
  def __init__(self, peli):
    self.id = peli["id"]
    self.episode_id = peli["episodeID"]
    self.title = peli["title"]
    self.ano = peli["releaseDate"][0:4]
    self.director = peli["director"]
    self.producer = peli["producers"]

  def load_pelicula(self, peli):
    self.opening = peli["openingCrawl"]

class Actor:
  def __init__(self, actor):
    self.name = actor['name']
    self.id = actor['id']

  def load_actor(self, actor):
    self.height = actor['height']
    self.mass = actor['mass']
    self.hair = actor['hairColor']
    self.skin = actor['skinColor']
    self.eye = actor['eyeColor']
    self.birth = actor['birthYear']
    self.gender = actor['gender']
    self.homeworld = self.load_homeworld(actor)

  def load_homeworld(self, actor):
    return actor['homeworld']['name']

class Ship:
  def __init__(self, ship):
    self.name = ship['name']
    self.id = ship['id']

  def load_ship(self, ship):
    self.model = ship['model']
    self.manufacturer = ship['manufacturers']
    self.cost_in_credits = ship['costInCredits']
    self.length = ship['length']
    self.max_atmosphering_speed = ship['maxAtmospheringSpeed']
    self.crew = ship['crew']
    self.passengers = ship['passengers']
    self.cargo_capacity = ship['cargoCapacity']
    self.consumables = ship['consumables']
    self.hyperdrive_rating = ship['hyperdriveRating']
    self.mglt = ship['MGLT']
    self.starship_class = ship['starshipClass']


class Planet:
  def __init__(self, planet):
    self.name = planet['name']
    self.id = planet['id']

  def load_planet(self, planet):
    self.rotation_period = planet['rotationPeriod']
    self.orbital_period = planet['orbitalPeriod']
    self.diameter = planet['diameter']
    self.climate = planet['climates']
    self.gravity = planet['gravity']
    self.terrain = planet['terrains']
    self.surface_water = planet['surfaceWater']
    self.population = planet['population']

class Search:
    def __init__(self, name, url):
        self.name = name
        self.url = url


# Create your views here.
def index(request):

    body = {"query": "query{allFilms {edges {node {id title episodeID releaseDate director producers}}}}"}
    url = "https://swapi-graphql-integracion-t3.herokuapp.com/ "
    response = requests.post(url, data=body)
    films = response.json()
    peliculas = list()
    for peli in films["data"]["allFilms"]["edges"]:
        p = Pelicula(peli["node"])
        peliculas.append(p)

    return render(request, 'index.html', {'data': peliculas})


def film(request):

    film_id = request.GET.get('id', '')

    body = {"query": "query{film(id: \"" + film_id + "\") {id title episodeID releaseDate director producers openingCrawl characterConnection{characters{id name}}starshipConnection{starships{id name}}planetConnection{planets{id name}}}}"}
    url = "https://swapi-graphql-integracion-t3.herokuapp.com/ "
    response = requests.post(url, data=body)
    peli = response.json()["data"]["film"]
    pelicula = Pelicula(peli)
    pelicula.load_pelicula(peli)

    actores = list()
    for actor in peli['characterConnection']['characters']:
        actores.append(Actor(actor))

    ships = list()
    for ship in peli['starshipConnection']['starships']:
        ships.append(Ship(ship))

    planets = list()
    for planet in peli['planetConnection']['planets']:
        planets.append(Planet(planet))

    return render(request, 'film.html', {'pelicula':pelicula, 'actores':actores, 'ships':ships, 'planets':planets})

def actor(request):

    actor_id = request.GET.get('id', '')

    body = {"query": "query{person(id: \"" + actor_id +"\"){id name birthYear eyeColor gender hairColor height mass skinColor homeworld{id name}starshipConnection{starships{id name}}filmConnection{films{id title episodeID releaseDate director producers}}}}"}
    url = "https://swapi-graphql-integracion-t3.herokuapp.com/ "
    response = requests.post(url, data=body)
    person = response.json()["data"]["person"]
    actor = Actor(person)
    actor.load_actor(person)

    films = list()
    for film in person['filmConnection']['films']:
        films.append(Pelicula(film))

    ships = list()
    for ship in person['starshipConnection']['starships']:
        ships.append(Ship(ship))

    return render(request, 'actor.html', {'actor':actor, 'films':films, 'ships':ships})

def ship(request):

    ship_id = request.GET.get('id', '')

    body = {"query": "query{starship(id: \"" + ship_id + "\") {id name model starshipClass manufacturers costInCredits length crew passengers maxAtmospheringSpeed hyperdriveRating MGLT cargoCapacity consumables filmConnection{films{id title episodeID releaseDate director producers}}pilotConnection{pilots{id name}}}}"}
    url = "https://swapi-graphql-integracion-t3.herokuapp.com/ "
    response = requests.post(url, data=body)
    nave = response.json()["data"]["starship"]
    ship = Ship(nave)
    ship.load_ship(nave)

    pilots = list()
    for pilot in nave['pilotConnection']['pilots']:
        pilots.append(Actor(pilot))

    films = list()
    for film in nave['filmConnection']['films']:
        films.append(Pelicula(film))

    return render(request, 'ship.html', {'ship':ship, 'pilots':pilots, 'films':films})

def planet(request):
    planet_id = request.GET.get('id', '')

    body = {"query": "query{planet(id: \"" + planet_id + "\") { id name diameter rotationPeriod orbitalPeriod gravity population climates terrains surfaceWater filmConnection{films{id title episodeID releaseDate director producers}}residentConnection{residents{id name}}}}"}
    url = "https://swapi-graphql-integracion-t3.herokuapp.com/ "
    response = requests.post(url, data=body)
    planet_json = response.json()["data"]["planet"]
    planet = Planet(planet_json)
    planet.load_planet(planet_json)

    residents = list()
    for resident in planet_json['residentConnection']['residents']:
        residents.append(Actor(resident))

    films = list()
    for film in planet_json['filmConnection']['films']:
        films.append(Pelicula(film))

    return render(request, 'planet.html', {'planet': planet, 'residents':residents, 'films':films})

def search(request):
    selection = request.GET.get('selection', '')
    text = request.GET.get('text', '')

    people_result = list()
    starships_result = list()
    films_result = list()
    planets_result = list()

    def look_up(url):
        response = requests.get(url)
        json = response.json()
        resultado_local = json['results']

        search_result = list()
        for elem in resultado_local:
            if "films" in url:
                search_result.append(Search(elem['title'], elem['url']))
            else:
                search_result.append(Search(elem['name'], elem['url']))

        if json['next'] != None:
            search_result.extend(look_up(json['next']))

        return search_result

    if selection == "people":
        new_url = "https://swapi.co/api/people/?search="+text
        people_result = look_up(new_url)

    elif selection == "starships":
        new_url = "https://swapi.co/api/starships/?search="+text
        starships_result = look_up(new_url)

    elif selection == "films":
        new_url = "https://swapi.co/api/films/?search="+text
        films_result = look_up(new_url)

    elif selection == "planets":
        new_url = "https://swapi.co/api/planets/?search="+text
        planets_result = look_up(new_url)

    else:
        new_url = "https://swapi.co/api/people/?search=" + text
        people_result = look_up(new_url)

        new_url = "https://swapi.co/api/starships/?search=" + text
        starships_result = look_up(new_url)

        new_url = "https://swapi.co/api/films/?search=" + text
        films_result = look_up(new_url)

        new_url = "https://swapi.co/api/planets/?search=" + text
        planets_result = look_up(new_url)

    return render(request, 'search.html', {'selection':selection, 'people_result':people_result,
                                           'starships_result':starships_result, 'films_result':films_result,
                                           'planets_result':planets_result})
