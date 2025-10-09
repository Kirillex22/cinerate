from datetime import datetime
from src.domain.entities.film import FilmExtended, FilmPreview, Episode, SeasonInfo, Person

EMPTY_IMAGE_URL = 'https://image.openmoviedb.com/kinopoisk-st-images//actor_iphone/iphone360_5409186.jpg'


def parse_episode(ep_data: dict) -> Episode:
    air_date = None
    air_date_str = ep_data.get('airDate', None)
    if air_date_str:
        try:
            air_date = datetime.fromisoformat(air_date_str.replace('Z', '+00:00'))
        except ValueError:
            pass

    still = ep_data.get('still', {})

    preview_link = still.get('url', None)
    if not preview_link:
        preview_link = still.get('previewUrl', EMPTY_IMAGE_URL)

    return Episode(
        number=ep_data.get('number') or 0,
        name=ep_data.get('name') or '',
        en_name=ep_data.get('en_name'),
        air_date=air_date,
        description=ep_data.get('description'),
        preview_link=preview_link
    )


def parse_film_base_fields(response: dict) -> dict:
    film_id = str(response.get('id') or '')  # Обязательно должен быть

    try:
        seasons_info = [
            SeasonInfo(
                number=season.get('number') or 0,
                episodes_count=season.get('episodesCount') or 0
            ) for season in response.get("seasonsInfo") or []
        ]
    except Exception:
        seasons_info = None

    try:
        last_updated_str = response.get('updatedAt')
        last_updated = datetime.strptime(last_updated_str, "%Y-%m-%dT%H:%M:%S.%fZ") if last_updated_str else None
    except Exception:
        last_updated = None

    return dict(
        filmid=film_id,
        season=response.get('number'),
        is_series=response.get("isSeries"),
        seasons_info=seasons_info or None,
        already_added=response.get("already_added"),
        is_watched=response.get("is_watched"),
        user_rating=response.get("user_rating"),
        last_updated=last_updated,
        added_at=response.get("added_at")
    )


def parse_film_extended(response: dict) -> FilmExtended:
    base_fields = parse_film_base_fields(response)

    name = response.get('name') or ''
    poster_link = response.get('poster', {}).get('url') if isinstance(response.get('poster'), dict) else EMPTY_IMAGE_URL
    alternative_name = response.get('alternativeName')
    release_year = response.get('year')
    genres = [g.get('name') for g in response.get('genres') or [] if g.get('name')]
    slogan = response.get('slogan')
    countries = [c.get('name') for c in response.get('countries') or [] if c.get('name')]
    description = response.get('description') or ''

    persons = []
    director = None
    for p in response.get('persons') or []:
        if not isinstance(p, dict):
            continue
        en_prof = (p.get('enProfession') or '').lower()
        prof = (p.get('profession') or '').lower()
        if en_prof in {"director", "actor", "producer", "writer"}:
            person = Person(
                id=p.get('id'),
                name=p.get('name') or '',
                photo=p.get('photo'),
                en_profession=p.get('enProfession')
            )
            persons.append(person)
            if 'director' in en_prof or 'режиссёр' in prof or 'режиссер' in prof:
                director = p.get('name') or person.name

    time_minutes = response.get('movieLength')

    ratings = response.get('rating')
    if ratings and isinstance(ratings, dict):
        ratings.pop('await', None)

    trailers = [
        t.get('url') for t in response.get('videos', {}).get('trailers') or [] if t.get('url')
    ]

    end_year = response.get('endYear') or (
        response.get('releaseYears', [{}])[0].get('endYear') if response.get('releaseYears') else None
    )

    status = response.get('status')
    tops = [str(response.get(k)) for k in ('top10', 'top250') if response.get(k) is not None]
    episodes = [parse_episode(ep) for ep in response.get('episodes') or []]
    age_rating = response.get('ageRating')

    return FilmExtended(
        **base_fields,
        name=name,
        poster_link=poster_link,
        alternative_name=alternative_name,
        release_year=release_year,
        genres=genres or [],
        slogan=slogan,
        countries=countries or [],
        director=director,
        description=description,
        persons=persons or [],
        time_minutes=time_minutes,
        ratings=ratings or [],
        trailers=trailers or [],
        end_year=end_year,
        status=status,
        tops=tops or [],
        episodes=episodes or [],
        age_rating=age_rating
    )


def parse_film_preview(response: dict) -> FilmPreview:
    base_fields = parse_film_base_fields(response)

    name = response.get('name') or ''
    poster_link = response.get('poster', {}).get('url', EMPTY_IMAGE_URL) if isinstance(response.get('poster'),
                                                                                       dict) else EMPTY_IMAGE_URL
    if poster_link is None:
        poster_link = EMPTY_IMAGE_URL

    release_year = response.get('year')
    alternative_name = response.get('alternativeName')
    genres = [g.get('name') for g in response.get('genres') or [] if g.get('name')]
    countries = [c.get('name') for c in response.get('countries') or [] if c.get('name')]

    director = None
    for p in response.get('persons') or []:
        if not isinstance(p, dict):
            continue
        en_prof = (p.get('enProfession') or '').lower()
        prof = (p.get('profession') or '').lower()
        if 'director' in en_prof or 'режиссёр' in prof or 'режиссер' in prof:
            director = p.get('name') or ''
            break

    time_minutes = response.get('movieLength')
    age_rating = response.get('ageRating')
    return FilmPreview(
        **base_fields,
        name=name,
        poster_link=poster_link,
        release_year=release_year,
        alternative_name=alternative_name,
        genres=genres or [],
        countries=countries or [],
        director=director,
        time_minutes=time_minutes,
        age_rating=age_rating
    )
