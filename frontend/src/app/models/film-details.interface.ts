export interface FilmDetails {
  filmid: string;
  season: number | null;
  is_series: boolean;
  seasons_info: any | null;
  already_added: boolean | null;
  is_watched: boolean;
  user_rating: UserRating | null;
  last_updated: string;
  added_at: string;
  name: string;
  poster_link: string;
  alternative_name: string;
  release_year: number;
  genres: string[];
  slogan: string;
  countries: string[];
  director: string;
  description: string;
  age_rating: number;
  persons: Person[];
  time_minutes: number;
  ratings: {
    kp: number;
    imdb: number;
    filmCritics: number;
    russianFilmCritics: number;
  };
  trailers: string[];
  episodes: Episode[] | null; 
}

export interface Person {
  id: number;
  name: string;
  photo: string;
  en_profession: string;
}

export interface UserRating {
  acting_game: number;
  atmosphere: number;
  montage: number;
  music: number;
  originality: number;
  storyline: number;
}

export interface Episode {
  number: number;
  name: string;
  en_name: string | null;
  air_date: string;
  description: string;
  preview_link: string;
}

export interface SeasonInfo {
  number: number;
  episodes_count: number;
}

export type FilmDetailsResponse = FilmDetails | FilmDetails[];