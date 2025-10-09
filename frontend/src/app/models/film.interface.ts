export interface Film {
  filmid: string;
  name: string;
  season : string | null;
  poster_link: string;
  release_year: number;
  countries: string[];
  time_minutes: number | null;
  is_series: boolean;
  already_added: boolean | null;
  alternative_name: string;
}
